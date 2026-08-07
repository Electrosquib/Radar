#include <uhd/types/tune_request.hpp>
#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/utils/safe_main.hpp>
#include <boost/program_options.hpp>
#include <boost/format.hpp>
#include <chrono>
#include <complex>
#include <csignal>
#include <fstream>
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <algorithm>
#include <filesystem>
#include <functional>
#include <type_traits>
#include <cstdint>
#include <cmath>
#include <cstddef>
#include <exception>
#include <stdexcept>
#include <cstring>
#include <deque>
#include <condition_variable>
#include <mutex>

namespace po = boost::program_options;
namespace fs = std::filesystem;

namespace {

constexpr double kPcmScale = 32767.0;

enum class IQComponentFormat : uint8_t {
    Float64 = 1,
    Float32 = 2,
    Int16 = 3
};

template <typename>
struct dependent_false : std::false_type {};

struct BinaryIQHeader {
    char magic[4] = {'S', 'R', 'I', 'Q'};
    uint8_t version = 1;
    uint8_t component_format = 0;
    uint16_t reserved = 0;
    double sample_rate_hz = 0.0;
    uint64_t sample_count = 0;
};

static_assert(std::is_standard_layout_v<BinaryIQHeader>, "BinaryIQHeader must be standard layout");

template <typename sample_t>
constexpr IQComponentFormat component_format_for()
{
    using component_t = typename sample_t::value_type;
    if constexpr (std::is_same_v<component_t, double>) {
        return IQComponentFormat::Float64;
    } else if constexpr (std::is_same_v<component_t, float>) {
        return IQComponentFormat::Float32;
    } else if constexpr (std::is_same_v<component_t, short>) {
        return IQComponentFormat::Int16;
    } else {
        static_assert(dependent_false<sample_t>::value, "Unsupported component type for BinaryIQWriter");
    }
}

template <typename sample_t>
class BinaryIQWriter {
public:
    BinaryIQWriter(const std::string& path, double sample_rate_hz)
        : _stream(path, std::ios::binary)
    {
        if (!_stream) {
            throw std::runtime_error("Could not open binary IQ file for writing: " + path);
        }
        _header.component_format = static_cast<uint8_t>(component_format_for<sample_t>());
        _header.sample_rate_hz = sample_rate_hz;
        _stream.write(reinterpret_cast<const char*>(&_header), sizeof(_header));
    }

    BinaryIQWriter(const BinaryIQWriter&) = delete;
    BinaryIQWriter& operator=(const BinaryIQWriter&) = delete;
    BinaryIQWriter(BinaryIQWriter&&) noexcept = default;

    ~BinaryIQWriter()
    {
        try {
            finalize();
        } catch (...) {
        }
    }

    void write_samples(const sample_t* data, size_t count)
    {
        _stream.write(reinterpret_cast<const char*>(data), static_cast<std::streamsize>(count * sizeof(sample_t)));
        _samples_written += count;
    }

    void finalize()
    {
        if (_finalized) return;
        const uint64_t total_samples = static_cast<uint64_t>(_samples_written);
        _stream.seekp(static_cast<std::streamoff>(offsetof(BinaryIQHeader, sample_count)), std::ios::beg);
        _stream.write(reinterpret_cast<const char*>(&total_samples), sizeof(total_samples));
        _stream.flush();
        _stream.close();
        _finalized = true;
    }

private:
    std::ofstream _stream;
    BinaryIQHeader _header{};
    size_t _samples_written = 0;
    bool _finalized = false;
};

template <typename sample_t>
class AsyncBinaryWriter {
public:
    AsyncBinaryWriter(const std::string& path, double sample_rate_hz)
        : _writer(path, sample_rate_hz)
    {
        _thread = std::thread([this]() { writer_loop(); });
    }

    ~AsyncBinaryWriter()
    {
        try {
            finalize();
        } catch (...) {
        }
    }

    void write_async(const sample_t* data, size_t count)
    {
        if (count == 0) return;
        std::vector<sample_t> buffer(data, data + count);
        {
            std::unique_lock<std::mutex> lock(_mutex);
            _queue.emplace_back(std::move(buffer));
        }
        _cv.notify_one();
    }

    void finalize()
    {
        {
            std::unique_lock<std::mutex> lock(_mutex);
            if (_stop) return;
            _stop = true;
        }
        _cv.notify_all();
        if (_thread.joinable()) {
            _thread.join();
        }
    }

private:
    void writer_loop()
    {
        while (true) {
            std::vector<sample_t> chunk;
            {
                std::unique_lock<std::mutex> lock(_mutex);
                _cv.wait(lock, [&]() { return _stop || !_queue.empty(); });
                if (_stop && _queue.empty()) break;
                chunk = std::move(_queue.front());
                _queue.pop_front();
            }
            _writer.write_samples(chunk.data(), chunk.size());
        }
        _writer.finalize();
    }

    BinaryIQWriter<sample_t> _writer;
    std::deque<std::vector<sample_t>> _queue;
    std::mutex _mutex;
    std::condition_variable _cv;
    std::thread _thread;
    bool _stop = false;
};

inline void sleep_for_seconds(double seconds)
{
    if (seconds <= 0.0) return;
    std::this_thread::sleep_for(std::chrono::duration<double>(seconds));
}

struct StereoWavData {
    uint32_t sample_rate = 0;
    std::vector<int16_t> interleaved_samples;
};

StereoWavData load_stereo_wav_iq(const std::string& path)
{
    std::ifstream file(path, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Could not open WAV file: " + path);
    }

    auto read_exact = [&](char* dst, std::streamsize count) {
        file.read(dst, count);
        if (!file) {
            throw std::runtime_error("Unexpected EOF while reading WAV header: " + path);
        }
    };

    char riff[4];
    read_exact(riff, 4);
    if (std::strncmp(riff, "RIFF", 4) != 0) {
        throw std::runtime_error("Invalid WAV header (missing RIFF): " + path);
    }

    uint32_t chunk_size = 0;
    read_exact(reinterpret_cast<char*>(&chunk_size), sizeof(chunk_size));

    char wave_id[4];
    read_exact(wave_id, 4);
    if (std::strncmp(wave_id, "WAVE", 4) != 0) {
        throw std::runtime_error("Invalid WAV header (missing WAVE): " + path);
    }

    bool fmt_found = false;
    bool data_found = false;
    uint16_t audio_format = 0;
    uint16_t num_channels = 0;
    uint32_t sample_rate = 0;
    uint16_t bits_per_sample = 0;
    std::vector<int16_t> samples;

    while (!data_found && file) {
        char chunk_id[4];
        file.read(chunk_id, 4);
        if (!file) break;

        uint32_t subchunk_size = 0;
        read_exact(reinterpret_cast<char*>(&subchunk_size), sizeof(subchunk_size));

        if (std::strncmp(chunk_id, "fmt ", 4) == 0) {
            read_exact(reinterpret_cast<char*>(&audio_format), sizeof(audio_format));
            read_exact(reinterpret_cast<char*>(&num_channels), sizeof(num_channels));
            read_exact(reinterpret_cast<char*>(&sample_rate), sizeof(sample_rate));

            uint32_t byte_rate = 0;
            read_exact(reinterpret_cast<char*>(&byte_rate), sizeof(byte_rate));

            uint16_t block_align = 0;
            read_exact(reinterpret_cast<char*>(&block_align), sizeof(block_align));

            read_exact(reinterpret_cast<char*>(&bits_per_sample), sizeof(bits_per_sample));

            const std::streamoff remaining = static_cast<std::streamoff>(subchunk_size) - 16;
            if (remaining > 0) {
                file.seekg(remaining, std::ios::cur);
            }
            fmt_found = true;
        } else if (std::strncmp(chunk_id, "data", 4) == 0) {
            samples.resize(subchunk_size / sizeof(int16_t));
            if (!samples.empty()) {
                read_exact(reinterpret_cast<char*>(samples.data()), static_cast<std::streamsize>(subchunk_size));
            }
            data_found = true;
        } else {
            file.seekg(subchunk_size, std::ios::cur);
        }

        if (subchunk_size & 1) {
            file.seekg(1, std::ios::cur);
        }
    }

    if (!fmt_found || !data_found) {
        throw std::runtime_error("Incomplete WAV file (missing fmt or data chunk): " + path);
    }

    if (audio_format != 1) {
        throw std::runtime_error("Unsupported WAV encoding (only PCM supported): " + path);
    }

    if (num_channels != 2 || bits_per_sample != 16) {
        throw std::runtime_error("Expected stereo 16-bit WAV file: " + path);
    }

    if (samples.size() % 2 != 0) {
        throw std::runtime_error("Stereo WAV file must have an even number of samples: " + path);
    }

    StereoWavData result;
    result.sample_rate = sample_rate;
    result.interleaved_samples = std::move(samples);
    return result;
}

template <typename sample_t>
std::vector<sample_t> convert_pcm_to_iq(const std::vector<int16_t>& pcm_samples)
{
    using component_t = typename sample_t::value_type;
    static_assert(
        std::is_same_v<component_t, short> ||
        std::is_same_v<component_t, float> ||
        std::is_same_v<component_t, double>,
        "Unsupported sample component type"
    );

    if (pcm_samples.size() % 2 != 0) {
        throw std::runtime_error("PCM sample array must contain I/Q pairs");
    }

    const size_t frames = pcm_samples.size() / 2;
    std::vector<sample_t> iq(frames);

    for (size_t n = 0; n < frames; ++n) {
        const int16_t i_val = pcm_samples[2 * n];
        const int16_t q_val = pcm_samples[2 * n + 1];

        if constexpr (std::is_same_v<component_t, short>) {
            iq[n] = sample_t(static_cast<short>(i_val), static_cast<short>(q_val));
        } else if constexpr (std::is_same_v<component_t, float>) {
            const float scale = 1.0f / static_cast<float>(kPcmScale);
            iq[n] = sample_t(static_cast<float>(i_val) * scale, static_cast<float>(q_val) * scale);
        } else if constexpr (std::is_same_v<component_t, double>) {
            const double scale = 1.0 / static_cast<double>(kPcmScale);
            iq[n] = sample_t(static_cast<double>(i_val) * scale, static_cast<double>(q_val) * scale);
        }
    }

    return iq;
}

} // namespace

static std::atomic<bool> stop_signal_called(false);

void sig_int_handler(int)
{
    stop_signal_called = true;
}

template <typename samp_type>
size_t timed_tx_from_buffer(
    uhd::tx_streamer::sptr tx_stream,
    const samp_type* samples,
    size_t total_samps,
    size_t spb,
    double start_time,
    const std::function<void(const samp_type*, size_t)>& on_chunk = {}
)
{
    if (total_samps == 0) {
        return 0;
    }

    std::vector<const samp_type*> buffs(tx_stream->get_num_channels(), samples);

    uhd::tx_metadata_t md;
    md.start_of_burst = true;
    md.end_of_burst = false;
    md.has_time_spec = true;
    md.time_spec = uhd::time_spec_t(start_time);

    size_t offset = 0;

    while (!stop_signal_called && offset < total_samps) {
        const size_t chunk = std::min(spb, total_samps - offset);
        for (auto& ptr : buffs) {
            ptr = samples + offset;
        }

        md.end_of_burst = ((offset + chunk) == total_samps);

        const size_t sent = tx_stream->send(buffs, chunk, md);
        if (sent != chunk) {
            throw std::runtime_error("TX send failed or timed out");
        }

        if (on_chunk) {
            on_chunk(samples + offset, chunk);
        }

        offset += sent;
        md.start_of_burst = false;
        md.has_time_spec = false;
        md.end_of_burst = false;
    }

    if (offset != total_samps) {
        throw std::runtime_error("TX stream terminated early");
    }

    return offset;
}

template <typename samp_type>
size_t timed_rx(
    uhd::rx_streamer::sptr rx_stream,
    size_t spb,
    double start_time,
    size_t total_rx_samps,
    const std::function<void(const samp_type*, size_t)>& on_chunk
)
{
    std::vector<samp_type> buff(spb);
    std::vector<void*> buffs(1);
    buffs[0] = buff.data();

    uhd::stream_cmd_t cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
    cmd.num_samps = total_rx_samps;
    cmd.stream_now = false;
    cmd.time_spec = uhd::time_spec_t(start_time);
    rx_stream->issue_stream_cmd(cmd);

    uhd::rx_metadata_t md;
    size_t samps_received = 0;

    while (!stop_signal_called && samps_received < total_rx_samps) {
        const size_t samps = rx_stream->recv(buffs, spb, md, 2.0, false);

        if (md.error_code == uhd::rx_metadata_t::ERROR_CODE_TIMEOUT) {
            continue;
        }

        if (md.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE) {
            throw std::runtime_error("RX error: " + md.strerror());
        }

        if (samps > 0) {
            if (on_chunk) {
                on_chunk(buff.data(), samps);
            }
            samps_received += samps;
        }
    }

    return samps_received;
}

template <typename samp_type>
size_t timed_rx_to_file(
    uhd::rx_streamer::sptr rx_stream,
    const std::string& rx_file,
    double sample_rate,
    size_t spb,
    double start_time,
    size_t total_rx_samps
)
{
    AsyncBinaryWriter<samp_type> writer(rx_file, sample_rate);
    auto write_fn = [&](const samp_type* data, size_t samps) {
        writer.write_async(data, samps);
    };
    const size_t received = timed_rx<samp_type>(rx_stream, spb, start_time, total_rx_samps, write_fn);
    writer.finalize();
    return received;
}

int UHD_SAFE_MAIN(int argc, char* argv[])
{
    std::signal(SIGINT, &sig_int_handler);

    std::string args, tx_file, rx_file, ant, tx_ant, rx_ant, subdev, ref, otw, type;
    double rate, freq, tx_gain, rx_gain, bw, lo_offset, start_delay, rx_extra_time;
    double device_settle, retune_settle, thread_lead;
    double chirp_start, chirp_end, subchirp_ratio;
    size_t spb, tx_channel, rx_channel, subchirp_count_override, subchirp_base_idx;
    bool single_shot = false;
    std::string output_dir, rx_prefix;

    po::options_description desc("Allowed options");
    desc.add_options()
        ("help,h", "help")
        ("args", po::value<std::string>(&args)->default_value(""), "device args")
        ("tx-file", po::value<std::string>(&tx_file)->required(), "TX IQ WAV file (stereo 16-bit)")
        ("rx-file", po::value<std::string>(&rx_file)->default_value("rx_capture.bin"), "RX output file")
        ("type", po::value<std::string>(&type)->default_value("float"), "double|float|short")
        ("rate,r", po::value<double>(&rate)->required(), "sample rate")
        ("freq,f", po::value<double>(&freq)->default_value(0.0), "center frequency (single-shot)")
        ("tx-gain", po::value<double>(&tx_gain)->default_value(0.0), "TX gain dB")
        ("rx-gain", po::value<double>(&rx_gain)->default_value(0.0), "RX gain dB")
        ("bw", po::value<double>(&bw), "frontend bandwidth")
        ("lo-offset", po::value<double>(&lo_offset)->default_value(0.0), "LO offset")
        ("ant", po::value<std::string>(&ant), "legacy antenna setting (applies to TX/RX)")
        ("tx-ant", po::value<std::string>(&tx_ant)->default_value("TX/RX"), "TX antenna port")
        ("rx-ant", po::value<std::string>(&rx_ant)->default_value("RX2"), "RX antenna port")
        ("subdev", po::value<std::string>(&subdev), "subdev")
        ("ref", po::value<std::string>(&ref), "internal|external|mimo|gpsdo")
        ("otw", po::value<std::string>(&otw)->default_value("sc16"), "otw format")
        ("spb", po::value<size_t>(&spb)->default_value(200000), "samples per buffer")
        ("tx-channel", po::value<size_t>(&tx_channel)->default_value(0), "TX channel")
        ("rx-channel", po::value<size_t>(&rx_channel)->default_value(0), "RX channel")
        ("start-delay", po::value<double>(&start_delay)->default_value(0.1), "seconds in future to start")
        ("rx-extra-time", po::value<double>(&rx_extra_time)->default_value(0.01), "extra RX capture time in seconds")
        ("device-settle", po::value<double>(&device_settle)->default_value(0.05), "seconds to wait after configuring USRP before streaming")
        ("retune-settle", po::value<double>(&retune_settle)->default_value(0.02), "seconds to wait after each retune during scan mode")
        ("thread-lead", po::value<double>(&thread_lead)->default_value(0.005), "seconds RX thread runs before TX starts")
        ("single-shot", po::bool_switch(&single_shot), "Disable subchirp scan and run one capture to --rx-file")
        ("chirp-start", po::value<double>(&chirp_start)->default_value(2.0e9), "Scan start frequency (Hz)")
        ("chirp-end", po::value<double>(&chirp_end)->default_value(3.1e9), "Scan end frequency (Hz)")
        ("subchirp-ratio", po::value<double>(&subchirp_ratio)->default_value(0.8), "Subchirp bandwidth ratio relative to sample rate")
        ("subchirp-count", po::value<size_t>(&subchirp_count_override)->default_value(0), "Manual subchirp count (0 auto)")
        ("subchirp-base-idx", po::value<size_t>(&subchirp_base_idx)->default_value(0), "Base index for file naming")
        ("output-dir", po::value<std::string>(&output_dir)->default_value("Stitched"), "Directory for binary captures")
        ("rx-prefix", po::value<std::string>(&rx_prefix)->default_value("rx_chirp_"), "Prefix for RX binary files");

    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);

    if (vm.count("help")) {
        std::cout << desc << std::endl;
        return 0;
    }

    po::notify(vm);

    const bool scan_mode = !single_shot;
    fs::path output_path(output_dir);

    if (single_shot && freq == 0.0) {
        throw std::runtime_error("--freq must be specified in single-shot mode");
    }

    if (rate <= 0.0) {
        throw std::runtime_error("Sample rate must be positive");
    }

    if (subchirp_ratio <= 0.0 || subchirp_ratio > 1.0) {
        throw std::runtime_error("subchirp-ratio must be within (0, 1]");
    }
    device_settle = std::max(0.0, device_settle);
    retune_settle = std::max(0.0, retune_settle);
    thread_lead = std::max(0.0, thread_lead);

    size_t planned_subchirps = subchirp_count_override;
    const double subchirp_bw = subchirp_ratio * rate;

    if (scan_mode) {
        if (chirp_end <= chirp_start) {
            throw std::runtime_error("chirp-end must be greater than chirp-start");
        }

        const size_t auto_count = static_cast<size_t>((chirp_end - chirp_start) / subchirp_bw);
        if (auto_count == 0) {
            throw std::runtime_error("Subchirp bandwidth larger than scan span");
        }

        if (planned_subchirps == 0 || planned_subchirps > auto_count) {
            planned_subchirps = auto_count;
        }

        if (freq == 0.0) {
            freq = chirp_start + rate / 2.0;
        }

        fs::create_directories(output_path);
    }

    std::cout << boost::format("Creating USRP with args: %s") % args << std::endl;
    auto usrp = uhd::usrp::multi_usrp::make(args);

    if (vm.count("subdev")) {
        usrp->set_tx_subdev_spec(subdev);
        usrp->set_rx_subdev_spec(subdev);
    }

    if (vm.count("ref")) {
        usrp->set_clock_source(ref);
        usrp->set_time_source(ref);
    }

    if (vm.count("ant")) {
        tx_ant = ant;
        rx_ant = ant;
    }

    if (tx_channel >= usrp->get_tx_num_channels()) {
        throw std::runtime_error("Invalid TX channel");
    }

    if (rx_channel >= usrp->get_rx_num_channels()) {
        throw std::runtime_error("Invalid RX channel");
    }

    usrp->set_tx_rate(rate, tx_channel);
    usrp->set_rx_rate(rate, rx_channel);

    usrp->set_tx_freq(uhd::tune_request_t(freq, lo_offset), tx_channel);
    usrp->set_rx_freq(uhd::tune_request_t(freq, lo_offset), rx_channel);

    usrp->set_tx_gain(tx_gain, tx_channel);
    usrp->set_rx_gain(rx_gain, rx_channel);

    if (vm.count("bw")) {
        usrp->set_tx_bandwidth(bw, tx_channel);
        usrp->set_rx_bandwidth(bw, rx_channel);
    }

    usrp->set_tx_antenna(tx_ant, tx_channel);
    usrp->set_rx_antenna(rx_ant, rx_channel);

    std::cout << boost::format("Actual TX rate: %f Msps") % (usrp->get_tx_rate(tx_channel) / 1e6) << std::endl;
    std::cout << boost::format("Actual RX rate: %f Msps") % (usrp->get_rx_rate(rx_channel) / 1e6) << std::endl;
    std::cout << boost::format("Actual TX freq: %f MHz") % (usrp->get_tx_freq(tx_channel) / 1e6) << std::endl;
    std::cout << boost::format("Actual RX freq: %f MHz") % (usrp->get_rx_freq(rx_channel) / 1e6) << std::endl;

    sleep_for_seconds(device_settle);

    usrp->set_time_now(uhd::time_spec_t(0.0));

    auto tx_wav = load_stereo_wav_iq(tx_file);
    const double wav_sample_rate = static_cast<double>(tx_wav.sample_rate);
    if (std::fabs(wav_sample_rate - rate) > 1.0) {
        throw std::runtime_error("WAV sample rate does not match requested --rate");
    }

    std::string cpu_format;
    size_t tx_file_samps = 0;

    std::vector<std::complex<double>> tx_samples_double;
    std::vector<std::complex<float>> tx_samples_float;
    std::vector<std::complex<short>> tx_samples_short;

    if (type == "double") {
        cpu_format = "fc64";
        tx_samples_double = convert_pcm_to_iq<std::complex<double>>(tx_wav.interleaved_samples);
        tx_file_samps = tx_samples_double.size();
    } else if (type == "float") {
        cpu_format = "fc32";
        tx_samples_float = convert_pcm_to_iq<std::complex<float>>(tx_wav.interleaved_samples);
        tx_file_samps = tx_samples_float.size();
    } else if (type == "short") {
        cpu_format = "sc16";
        tx_samples_short = convert_pcm_to_iq<std::complex<short>>(tx_wav.interleaved_samples);
        tx_file_samps = tx_samples_short.size();
    } else {
        throw std::runtime_error("Unknown type: " + type);
    }

    tx_wav.interleaved_samples.clear();
    tx_wav.interleaved_samples.shrink_to_fit();

    if (tx_file_samps == 0) {
        throw std::runtime_error("TX WAV file missing or empty");
    }

    const double extra_time = std::max(0.0, rx_extra_time);
    const size_t extra_samples = static_cast<size_t>(std::llround(extra_time * rate));
    const size_t rx_samples_single = tx_file_samps + extra_samples;
    const size_t rx_samples_scan = tx_file_samps + extra_samples + 5000;

    uhd::stream_args_t tx_args(cpu_format, otw);
    tx_args.channels = {tx_channel};
    auto tx_stream = usrp->get_tx_stream(tx_args);

    uhd::stream_args_t rx_args(cpu_format, otw);
    rx_args.channels = {rx_channel};
    auto rx_stream = usrp->get_rx_stream(rx_args);

    std::cout << boost::format("TX samples per burst: %u") % tx_file_samps << std::endl;
    if (scan_mode) {
        std::cout << boost::format("RX samples per subchirp: %u") % rx_samples_scan << std::endl;
        std::cout << boost::format("Planned subchirps: %u | Start %.3f GHz | End %.3f GHz | Span %.3f MHz")
                     % planned_subchirps
                     % (chirp_start / 1e9)
                     % (chirp_end / 1e9)
                     % (subchirp_bw / 1e6)
                  << std::endl;
    } else {
        std::cout << boost::format("RX samples: %u") % rx_samples_single << std::endl;
    }

    auto schedule_start = [&]() {
        return usrp->get_time_now().get_real_secs() + start_delay;
    };

    auto set_center_frequency = [&](double center) {
        usrp->set_tx_freq(uhd::tune_request_t(center, lo_offset), tx_channel);
        usrp->set_rx_freq(uhd::tune_request_t(center, lo_offset), rx_channel);
    };

    auto run_single_capture = [&](auto sample_tag, const auto& tx_samples) {
        using sample_t = decltype(sample_tag);
        const double start_time = schedule_start();
        std::cout << boost::format("Scheduled start time: %.9f s") % start_time << std::endl;

        size_t rx_received = 0;
        std::thread rx_thread([&]() {
            rx_received = timed_rx_to_file<sample_t>(rx_stream, rx_file, rate, spb, start_time, rx_samples_single);
        });

        sleep_for_seconds(thread_lead);

        const size_t sent = timed_tx_from_buffer<sample_t>(
            tx_stream,
            tx_samples.data(),
            tx_samples.size(),
            spb,
            start_time
        );

        rx_thread.join();

        if (sent != tx_file_samps) {
            throw std::runtime_error("TX sample count mismatch in single-shot mode");
        }
        if (rx_received != rx_samples_single) {
            throw std::runtime_error("RX sample count mismatch in single-shot mode");
        }
    };

    auto run_scan_sequence = [&](auto sample_tag, const auto& tx_samples) {
        using sample_t = decltype(sample_tag);
        size_t completed = 0;
        double current_start = chirp_start;

        while (completed < planned_subchirps && !stop_signal_called) {
            const double center_frequency = current_start + rate / 2.0;
            const double subchirp_end = current_start + subchirp_bw;

            set_center_frequency(center_frequency);
            sleep_for_seconds(retune_settle);

            const size_t file_idx = subchirp_base_idx + completed;
            const fs::path rx_path = output_path / (rx_prefix + std::to_string(file_idx) + ".bin");

            std::cout << boost::format("[Subchirp %u/%u] Start %.6f GHz | Center %.6f GHz | End %.6f GHz")
                         % (completed + 1)
                         % planned_subchirps
                         % (current_start / 1e9)
                         % (center_frequency / 1e9)
                         % (subchirp_end / 1e9)
                      << std::endl;

            AsyncBinaryWriter<sample_t> rx_writer(rx_path.string(), rate);

            const double start_time = schedule_start();
            size_t rx_received = 0;

            std::thread rx_thread([&]() {
                rx_received = timed_rx<sample_t>(
                    rx_stream,
                    spb,
                    start_time,
                    rx_samples_scan,
                    [&](const sample_t* data, size_t samps) {
                        rx_writer.write_async(data, samps);
                    }
                );
            });

            sleep_for_seconds(thread_lead);

            const size_t sent = timed_tx_from_buffer<sample_t>(
                tx_stream,
                tx_samples.data(),
                tx_samples.size(),
                spb,
                start_time
            );

            rx_thread.join();
            rx_writer.finalize();

            if (sent != tx_file_samps) {
                throw std::runtime_error("TX sample count mismatch during scan");
            }
            if (rx_received != rx_samples_scan) {
                throw std::runtime_error("RX sample count mismatch during scan");
            }

            ++completed;
            current_start += subchirp_bw;
        }

        std::cout << boost::format("Completed %u subchirps") % completed << std::endl;
    };

    if (type == "double") {
        if (scan_mode) {
            run_scan_sequence(std::complex<double>{}, tx_samples_double);
        } else {
            run_single_capture(std::complex<double>{}, tx_samples_double);
        }
    } else if (type == "float") {
        if (scan_mode) {
            run_scan_sequence(std::complex<float>{}, tx_samples_float);
        } else {
            run_single_capture(std::complex<float>{}, tx_samples_float);
        }
    } else if (type == "short") {
        if (scan_mode) {
            run_scan_sequence(std::complex<short>{}, tx_samples_short);
        } else {
            run_single_capture(std::complex<short>{}, tx_samples_short);
        }
    }

    std::cout << "Done" << std::endl;
    return 0;
}
