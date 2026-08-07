#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: continuous_chirp
# Author: Levi Farinas
# GNU Radio version: 3.10.12.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import threading




class default(gr.top_block):

    def __init__(self, bb_chirp_period=(1e-3), center_freq=2.5e9, mask=0, pilot_amplitude=.2, rx_gain=60, sdr_fs=int(10e6), subchirp_idx=0, tx_gain=50, usrp_string=""):
        gr.top_block.__init__(self, "continuous_chirp", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.bb_chirp_period = bb_chirp_period
        self.center_freq = center_freq
        self.mask = mask
        self.pilot_amplitude = pilot_amplitude
        self.rx_gain = rx_gain
        self.sdr_fs = sdr_fs
        self.subchirp_idx = subchirp_idx
        self.tx_gain = tx_gain
        self.usrp_string = usrp_string

        ##################################################
        # Variables
        ##################################################
        self.prechirp_buffer = prechirp_buffer = int(10e3)
        self.postchirp_buffer = postchirp_buffer = int(1e3)
        self.pilot_bb_freq = pilot_bb_freq = (sdr_fs/2) * .9
        self.pi = pi = 3.141592653
        self.chirp_bw = chirp_bw = .8 * (sdr_fs)
        self.c = c = 3e8

        ##################################################
        # Blocks
        ##################################################

        self.blocks_wavfile_sink_1 = blocks.wavfile_sink(
            '/Users/levifarinas/Documents/SAR Research/Data/sweep_rx.wav',
            3,
            sdr_fs,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_float*1, sdr_fs, True, 0 if "auto" == "auto" else max( int(float(0.1) * sdr_fs) if "auto" == "time" else int(0.1), 1) )
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(mask)
        self.blocks_complex_to_float_1 = blocks.complex_to_float(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_1 = analog.sig_source_c(sdr_fs, analog.GR_COS_WAVE, pilot_bb_freq, pilot_amplitude, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(sdr_fs, analog.GR_SAW_WAVE, (1/bb_chirp_period), 1, pi, pi)
        self.analog_sig_source_x_0.set_max_output_buffer(100)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(((2*3.14159*chirp_bw)/(sdr_fs)))
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, mask)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_wavfile_sink_1, 2))
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_complex_to_float_1, 0), (self.blocks_wavfile_sink_1, 0))
        self.connect((self.blocks_complex_to_float_1, 1), (self.blocks_wavfile_sink_1, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_complex_to_float_1, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.analog_frequency_modulator_fc_0, 0))


    def get_bb_chirp_period(self):
        return self.bb_chirp_period

    def set_bb_chirp_period(self, bb_chirp_period):
        self.bb_chirp_period = bb_chirp_period
        self.analog_sig_source_x_0.set_frequency((1/self.bb_chirp_period))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq

    def get_mask(self):
        return self.mask

    def set_mask(self, mask):
        self.mask = mask
        self.analog_const_source_x_0.set_offset(self.mask)
        self.blocks_multiply_const_vxx_0.set_k(self.mask)

    def get_pilot_amplitude(self):
        return self.pilot_amplitude

    def set_pilot_amplitude(self, pilot_amplitude):
        self.pilot_amplitude = pilot_amplitude
        self.analog_sig_source_x_1.set_amplitude(self.pilot_amplitude)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain

    def get_sdr_fs(self):
        return self.sdr_fs

    def set_sdr_fs(self, sdr_fs):
        self.sdr_fs = sdr_fs
        self.set_chirp_bw(.8 * (self.sdr_fs))
        self.set_pilot_bb_freq((self.sdr_fs/2) * .9)
        self.analog_frequency_modulator_fc_0.set_sensitivity(((2*3.14159*self.chirp_bw)/(self.sdr_fs)))
        self.analog_sig_source_x_0.set_sampling_freq(self.sdr_fs)
        self.analog_sig_source_x_1.set_sampling_freq(self.sdr_fs)
        self.blocks_throttle2_0.set_sample_rate(self.sdr_fs)

    def get_subchirp_idx(self):
        return self.subchirp_idx

    def set_subchirp_idx(self, subchirp_idx):
        self.subchirp_idx = subchirp_idx

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain

    def get_usrp_string(self):
        return self.usrp_string

    def set_usrp_string(self, usrp_string):
        self.usrp_string = usrp_string

    def get_prechirp_buffer(self):
        return self.prechirp_buffer

    def set_prechirp_buffer(self, prechirp_buffer):
        self.prechirp_buffer = prechirp_buffer

    def get_postchirp_buffer(self):
        return self.postchirp_buffer

    def set_postchirp_buffer(self, postchirp_buffer):
        self.postchirp_buffer = postchirp_buffer

    def get_pilot_bb_freq(self):
        return self.pilot_bb_freq

    def set_pilot_bb_freq(self, pilot_bb_freq):
        self.pilot_bb_freq = pilot_bb_freq
        self.analog_sig_source_x_1.set_frequency(self.pilot_bb_freq)

    def get_pi(self):
        return self.pi

    def set_pi(self, pi):
        self.pi = pi
        self.analog_sig_source_x_0.set_offset(self.pi)
        self.analog_sig_source_x_0.set_phase(self.pi)

    def get_chirp_bw(self):
        return self.chirp_bw

    def set_chirp_bw(self, chirp_bw):
        self.chirp_bw = chirp_bw
        self.analog_frequency_modulator_fc_0.set_sensitivity(((2*3.14159*self.chirp_bw)/(self.sdr_fs)))

    def get_c(self):
        return self.c

    def set_c(self, c):
        self.c = c



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--bb-chirp-period", dest="bb_chirp_period", type=eng_float, default=eng_notation.num_to_str(float((1e-3))),
        help="Set bb_chirp_period [default=%(default)r]")
    parser.add_argument(
        "--center-freq", dest="center_freq", type=eng_float, default=eng_notation.num_to_str(float(2.5e9)),
        help="Set center_freq [default=%(default)r]")
    parser.add_argument(
        "--pilot-amplitude", dest="pilot_amplitude", type=eng_float, default=eng_notation.num_to_str(float(.2)),
        help="Set pilot_amplitude [default=%(default)r]")
    parser.add_argument(
        "--rx-gain", dest="rx_gain", type=intx, default=60,
        help="Set rx_gain [default=%(default)r]")
    parser.add_argument(
        "--sdr-fs", dest="sdr_fs", type=intx, default=int(10e6),
        help="Set sdr_fs [default=%(default)r]")
    parser.add_argument(
        "--subchirp-idx", dest="subchirp_idx", type=intx, default=0,
        help="Set subchirp_idx [default=%(default)r]")
    parser.add_argument(
        "--tx-gain", dest="tx_gain", type=intx, default=50,
        help="Set tx_gain [default=%(default)r]")
    parser.add_argument(
        "--usrp-string", dest="usrp_string", type=str, default="",
        help="Set usrp_string [default=%(default)r]")
    return parser


def main(top_block_cls=default, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bb_chirp_period=options.bb_chirp_period, center_freq=options.center_freq, pilot_amplitude=options.pilot_amplitude, rx_gain=options.rx_gain, sdr_fs=options.sdr_fs, subchirp_idx=options.subchirp_idx, tx_gain=options.tx_gain, usrp_string=options.usrp_string)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    tb.wait()


if __name__ == '__main__':
    main()
