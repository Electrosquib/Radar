#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Chirp with Pilot Tone
# Author: Levi Farinas
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import sip
import threading



class pilot_chirp(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Chirp with Pilot Tone", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Chirp with Pilot Tone")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pilot_chirp")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.sdr_fs = sdr_fs = int(10e6)
        self.usrp_string = usrp_string = ""
        self.rf_gain = rf_gain = 50
        self.pilot_bb_freq = pilot_bb_freq = sdr_fs/2 * .9
        self.pilot_amplitude = pilot_amplitude = .2
        self.chirp_idx = chirp_idx = 3
        self.chirp_bw = chirp_bw = .8 * (sdr_fs/2)
        self.center_freq = center_freq = 2.5e9
        self.bb_chirp_period = bb_chirp_period = 50e-6

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(sdr_fs)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_gain(60, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join((usrp_string, '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.uhd_usrp_sink_0.set_samp_rate(sdr_fs)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_sink_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(rf_gain, 0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            sdr_fs, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.blocks_wavfile_sink_0_0 = blocks.wavfile_sink(
            f"/Users/levifarinas/Dropbox/University/SAR Research/Data/rx_{chirp_idx}.wav",
            2,
            sdr_fs,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(
            f"/Users/levifarinas/Dropbox/University/SAR Research/Data/pilot_chirp_{chirp_idx}.wav",
            2,
            sdr_fs,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_float*1, sdr_fs, True, 0 if "auto" == "auto" else max( int(float(0.1) * sdr_fs) if "auto" == "time" else int(0.1), 1) )
        self.blocks_head_0 = blocks.head(gr.sizeof_float*1, (int(bb_chirp_period*sdr_fs)))
        self.blocks_complex_to_float_0_0 = blocks.complex_to_float(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_1 = analog.sig_source_c(sdr_fs, analog.GR_COS_WAVE, pilot_bb_freq, pilot_amplitude, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(sdr_fs, analog.GR_SAW_WAVE, (1/bb_chirp_period), 1, 0, 3.14159)
        self.analog_sig_source_x_0.set_max_output_buffer(100)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(((2*3.14159*chirp_bw)/(sdr_fs)))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_head_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_wavfile_sink_0, 1))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_complex_to_float_0_0, 1), (self.blocks_wavfile_sink_0_0, 1))
        self.connect((self.blocks_complex_to_float_0_0, 0), (self.blocks_wavfile_sink_0_0, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.analog_frequency_modulator_fc_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_complex_to_float_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pilot_chirp")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_sdr_fs(self):
        return self.sdr_fs

    def set_sdr_fs(self, sdr_fs):
        self.sdr_fs = sdr_fs
        self.set_chirp_bw(.8 * (self.sdr_fs/2))
        self.set_pilot_bb_freq(self.sdr_fs/2 * .9)
        self.analog_frequency_modulator_fc_0.set_sensitivity(((2*3.14159*self.chirp_bw)/(self.sdr_fs)))
        self.analog_sig_source_x_0.set_sampling_freq(self.sdr_fs)
        self.analog_sig_source_x_1.set_sampling_freq(self.sdr_fs)
        self.blocks_head_0.set_length((int(self.bb_chirp_period*self.sdr_fs)))
        self.blocks_throttle2_0.set_sample_rate(self.sdr_fs)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.sdr_fs)
        self.uhd_usrp_sink_0.set_samp_rate(self.sdr_fs)
        self.uhd_usrp_source_0.set_samp_rate(self.sdr_fs)

    def get_usrp_string(self):
        return self.usrp_string

    def set_usrp_string(self, usrp_string):
        self.usrp_string = usrp_string

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.uhd_usrp_sink_0.set_gain(self.rf_gain, 0)

    def get_pilot_bb_freq(self):
        return self.pilot_bb_freq

    def set_pilot_bb_freq(self, pilot_bb_freq):
        self.pilot_bb_freq = pilot_bb_freq
        self.analog_sig_source_x_1.set_frequency(self.pilot_bb_freq)

    def get_pilot_amplitude(self):
        return self.pilot_amplitude

    def set_pilot_amplitude(self, pilot_amplitude):
        self.pilot_amplitude = pilot_amplitude
        self.analog_sig_source_x_1.set_amplitude(self.pilot_amplitude)

    def get_chirp_idx(self):
        return self.chirp_idx

    def set_chirp_idx(self, chirp_idx):
        self.chirp_idx = chirp_idx

    def get_chirp_bw(self):
        return self.chirp_bw

    def set_chirp_bw(self, chirp_bw):
        self.chirp_bw = chirp_bw
        self.analog_frequency_modulator_fc_0.set_sensitivity(((2*3.14159*self.chirp_bw)/(self.sdr_fs)))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.center_freq, 0)

    def get_bb_chirp_period(self):
        return self.bb_chirp_period

    def set_bb_chirp_period(self, bb_chirp_period):
        self.bb_chirp_period = bb_chirp_period
        self.analog_sig_source_x_0.set_frequency((1/self.bb_chirp_period))
        self.blocks_head_0.set_length((int(self.bb_chirp_period*self.sdr_fs)))




def main(top_block_cls=pilot_chirp, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
