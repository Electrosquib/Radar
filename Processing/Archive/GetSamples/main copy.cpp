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

namespace po = boost::program_options;

static std::atomic<bool> stop_signal_called(false);

void sig_int_handler(int)
{
    stop_signal_called = true;
}

size_t get_file_size(const std::string& path)
{
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) return 0;
    return static_cast<size_t>(f.tellg());
}

template <typename samp_type>
size_t get_num_file_samples(const std::string& path)
{
    const size_t bytes = get_file_size(path);
    return bytes / sizeof(samp_type);
}

template <typename samp_type>
void timed_tx_from_file(
    uhd::tx_streamer::sptr tx_stream,
    const std::string& tx_file,
    size_t spb,
    double start_time
)
{
    std::ifstream infile(tx_file, std::ios::binary);
    if (!infile) throw std::runtime_error("Could not open TX file: " + tx_file);

    std::vector<samp_type> buff(spb);
    std::vector<samp_type*> buffs(tx_stream->get_num_channels(), buff.data());

    uhd::tx_metadata_t md;
    md.start_of_burst = true;
    md.end_of_burst = false;
    md.has_time_spec = true;
    md.time_spec = uhd::time_spec_t(start_time);

    while (!stop_signal_called && infile.good()) {
        infile.read(reinterpret_cast<char*>(buff.data()), buff.size() * sizeof(samp_type));
        const size_t num_tx_samps = static_cast<size_t>(infile.gcount() / sizeof(samp_type));
        if (num_tx_samps == 0) break;

        const bool eof_now = infile.eof();
        md.end_of_burst = eof_now;

        const size_t sent = tx_stream->send(buffs, num_tx_samps, md);
        if (sent != num_tx_samps) {
            throw std::runtime_error("TX send failed or timed out");
        }

        md.start_of_burst = false;
        md.has_time_spec = false;
    }

    if (!md.end_of_burst) {
        md.start_of_burst = false;
        md.end_of_burst = true;
        md.has_time_spec = false;
        tx_stream->send("", 0, md);
    }
}

template <typename samp_type>
void timed_rx_to_file(
    uhd::rx_streamer::sptr rx_stream,
    const std::string& rx_file,
    size_t spb,
    double start_time,
    size_t total_rx_samps
)
{
    std::ofstream outfile(rx_file, std::ios::binary);
    if (!outfile) throw std::runtime_error("Could not open RX file: " + rx_file);

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
            outfile.write(reinterpret_cast<const char*>(buff.data()), samps * sizeof(samp_type));
            samps_received += samps;
        }
    }
}

int UHD_SAFE_MAIN(int argc, char* argv[])
{
    std::signal(SIGINT, &sig_int_handler);

    std::string args, tx_file, rx_file, ant, subdev, ref, otw, type;
    double rate, freq, tx_gain, rx_gain, bw, lo_offset, start_delay, rx_extra_time;
    size_t spb, tx_channel, rx_channel;

    po::options_description desc("Allowed options");
    desc.add_options()
        ("help,h", "help")
        ("args", po::value<std::string>(&args)->default_value(""), "device args")
        ("tx-file", po::value<std::string>(&tx_file)->required(), "TX IQ file")
        ("rx-file", po::value<std::string>(&rx_file)->default_value("rx_capture.bin"), "RX output file")
        ("type", po::value<std::string>(&type)->default_value("float"), "double|float|short")
        ("rate,r", po::value<double>(&rate)->required(), "sample rate")
        ("freq,f", po::value<double>(&freq)->required(), "center frequency")
        ("tx-gain", po::value<double>(&tx_gain)->default_value(0.0), "TX gain dB")
        ("rx-gain", po::value<double>(&rx_gain)->default_value(0.0), "RX gain dB")
        ("bw", po::value<double>(&bw), "frontend bandwidth")
        ("lo-offset", po::value<double>(&lo_offset)->default_value(0.0), "LO offset")
        ("ant", po::value<std::string>(&ant), "antenna")
        ("subdev", po::value<std::string>(&subdev), "subdev")
        ("ref", po::value<std::string>(&ref), "internal|external|mimo|gpsdo")
        ("otw", po::value<std::string>(&otw)->default_value("sc16"), "otw format")
        ("spb", po::value<size_t>(&spb)->default_value(10000), "samples per buffer")
        ("tx-channel", po::value<size_t>(&tx_channel)->default_value(0), "TX channel")
        ("rx-channel", po::value<size_t>(&rx_channel)->default_value(0), "RX channel")
        ("start-delay", po::value<double>(&start_delay)->default_value(0.1), "seconds in future to start")
        ("rx-extra-time", po::value<double>(&rx_extra_time)->default_value(0.01), "extra RX capture time in seconds");

    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);

    if (vm.count("help")) {
        std::cout << desc << std::endl;
        return 0;
    }

    po::notify(vm);

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

    if (vm.count("ant")) {
        usrp->set_tx_antenna(ant, tx_channel);
        usrp->set_rx_antenna(ant, rx_channel);
    }

    std::cout << boost::format("Actual TX rate: %f Msps") % (usrp->get_tx_rate(tx_channel) / 1e6) << std::endl;
    std::cout << boost::format("Actual RX rate: %f Msps") % (usrp->get_rx_rate(rx_channel) / 1e6) << std::endl;
    std::cout << boost::format("Actual TX freq: %f MHz") % (usrp->get_tx_freq(tx_channel) / 1e6) << std::endl;
    std::cout << boost::format("Actual RX freq: %f MHz") % (usrp->get_rx_freq(rx_channel) / 1e6) << std::endl;

    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    usrp->set_time_now(uhd::time_spec_t(0.0));
    const double start_time = usrp->get_time_now().get_real_secs() + start_delay;

    std::string cpu_format;
    size_t tx_file_samps = 0;

    if (type == "double") {
        cpu_format = "fc64";
        tx_file_samps = get_num_file_samples<std::complex<double>>(tx_file);
    } else if (type == "float") {
        cpu_format = "fc32";
        tx_file_samps = get_num_file_samples<std::complex<float>>(tx_file);
    } else if (type == "short") {
        cpu_format = "sc16";
        tx_file_samps = get_num_file_samples<std::complex<short>>(tx_file);
    } else {
        throw std::runtime_error("Unknown type: " + type);
    }

    if (tx_file_samps == 0) {
        throw std::runtime_error("TX file missing or empty");
    }

    const size_t total_rx_samps = tx_file_samps + static_cast<size_t>(std::max(0.0, rx_extra_time) * rate);

    uhd::stream_args_t tx_args(cpu_format, otw);
    tx_args.channels = {tx_channel};
    auto tx_stream = usrp->get_tx_stream(tx_args);

    uhd::stream_args_t rx_args(cpu_format, otw);
    rx_args.channels = {rx_channel};
    auto rx_stream = usrp->get_rx_stream(rx_args);

    std::cout << boost::format("TX samples: %u") % tx_file_samps << std::endl;
    std::cout << boost::format("RX samples: %u") % total_rx_samps << std::endl;
    std::cout << boost::format("Scheduled start time: %.9f s") % start_time << std::endl;

    std::thread rx_thread([&]() {
        if (type == "double") {
            timed_rx_to_file<std::complex<double>>(rx_stream, rx_file, spb, start_time, total_rx_samps);
        } else if (type == "float") {
            timed_rx_to_file<std::complex<float>>(rx_stream, rx_file, spb, start_time, total_rx_samps);
        } else if (type == "short") {
            timed_rx_to_file<std::complex<short>>(rx_stream, rx_file, spb, start_time, total_rx_samps);
        }
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(20));

    if (type == "double") {
        timed_tx_from_file<std::complex<double>>(tx_stream, tx_file, spb, start_time);
    } else if (type == "float") {
        timed_tx_from_file<std::complex<float>>(tx_stream, tx_file, spb, start_time);
    } else if (type == "short") {
        timed_tx_from_file<std::complex<short>>(tx_stream, tx_file, spb, start_time);
    }

    rx_thread.join();

    std::cout << "Done" << std::endl;
    return 0;
}