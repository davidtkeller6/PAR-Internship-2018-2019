#!/usr/bin/env python

##################################################

# Gnuradio Python Flow Graph

# Title: Tutorial Three

# Generated: Wed Mar 12 15:35:18 2014

##################################################


from gnuradio import analog

from gnuradio import audio

from gnuradio import eng_notation

from gnuradio import gr

from gnuradio.eng_option import eng_option

from gnuradio.filter import firdes

from optparse import OptionParser


class tutorial_three(gr.top_block):


    def __init__(self):

        gr.top_block.__init__(self, "Tutorial Three")


        ##################################################

        # Variables

        ##################################################

        self.samp_rate = samp_rate = 32000


        ##################################################

        # Blocks

        ##################################################

        self.audio_sink_0 = audio.sink(samp_rate, "", True)

        self.analog_sig_source_x_1 = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, 350, .1, 0)

        self.analog_sig_source_x_0 = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, 440, .1, 0)


        ##################################################

        # Connections

        ##################################################

        self.connect((self.analog_sig_source_x_1, 0), (self.audio_sink_0, 1))

        self.connect((self.analog_sig_source_x_0, 0), (self.audio_sink_0, 0))



# QT sink close method reimplementation


    def get_samp_rate(self):

        return self.samp_rate


    def set_samp_rate(self, samp_rate):

        self.samp_rate = samp_rate

        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)

        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)


if __name__ == '__main__':

    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")

    (options, args) = parser.parse_args()

    tb = tutorial_three()

    tb.start()

    raw_input('Press Enter to quit: ')

    tb.stop()

    tb.wait()
