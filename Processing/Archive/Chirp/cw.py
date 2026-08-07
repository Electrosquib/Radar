#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Continuous Wave
# Author: Levi Farinas
# GNU Radio version: 3.10.12.0

from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import threading




class cw(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Continuous Wave", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.usrp_string = usrp_string = ""
        self.sdr_fs = sdr_fs = int(300e3)
        self.rf_gain = rf_gain = 50
        self.center_freq = center_freq = 2.5e9

        ##################################################
        # Blocks
        ##################################################

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
        self.uhd_usrp_sink_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_sink_0.set_center_freq(center_freq-1e3, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(rf_gain, 0)
        self.analog_sig_source_x_1 = analog.sig_source_c(sdr_fs, analog.GR_COS_WAVE, 1e3, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_1, 0), (self.uhd_usrp_sink_0, 0))


    def get_usrp_string(self):
        return self.usrp_string

    def set_usrp_string(self, usrp_string):
        self.usrp_string = usrp_string

    def get_sdr_fs(self):
        return self.sdr_fs

    def set_sdr_fs(self, sdr_fs):
        self.sdr_fs = sdr_fs
        self.analog_sig_source_x_1.set_sampling_freq(self.sdr_fs)
        self.uhd_usrp_sink_0.set_samp_rate(self.sdr_fs)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.uhd_usrp_sink_0.set_gain(self.rf_gain, 0)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq-1e3, 0)




def main(top_block_cls=cw, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
