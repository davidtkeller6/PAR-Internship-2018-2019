#!/usr/bin/env python

from gnuradio import qtgui
from gnuradio import gr, gru, eng_notation
from gnuradio import audio
from gnuradio import uhd
#from gnuradio import usrp
from gnuradio import blocks
from gnuradio import filter
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, powermate
from gnuradio.wxgui import stdgui2, fftsink2, form
from optparse import OptionParser
#from usrp import usrp_dbid
import sys
import math
import wx
#import usrp

'''
class wfm_rx_block (stdgui2.std_top_block):
    
    def __init__(self):
        self.u = usrp.source_c()                    # usrp is data source.
        adc_rate = self.u.adc_rate()                # 64 MS/s
        usrp_decim = 200
        self.u.set_decim_rate(usrp_decim)
        usrp_rate = adc_rate / usrp_decim           # 320 kS/s
        chanfilt_decim = 1
        demod_rate = usrp_rate / chanfilt_decim
        audio_decimation = 10
        audio_rate = demod_rate / audio_decimation  # 32 kHz
        if options.rx_subdev_spec is None:
            options.rx_subdev_spec = pick_subdevice(self.u)
        self.u.set_mux(usrp.determine_rx_mux_value(self.u, options.rx_subdev_spec))
        self.subdev = usrp.selected_subdev(self.u, options.rx_subdev_spec)
        chan_filt = gr.fir_filter_ccf (chanfilt_decim, chan_filt_coeffs)
        self.guts = blks2.wfm_rcv (demod_rate, audio_decimation)
        self.volume_control = gr.multiply_const_ff(self.vol)
        audio_sink = audio.sink (int (audio_rate), options.audio_output, False)  # ok_to_block
        self.connect (self.u, chan_filt, self.guts, self.volume_control, audio_sink)
        self.set_gain(options.gain)
        self.set_vol(options.volume)
        if not(self.set_freq(options.freq)):
            self._set_status_msg("Failed to set initial frequency")
        r = usrp.tune(self.u, 0, self.subdev, target_freq)
'''

class FM_Receiver(gr.top_block):
    
    def __init__(self):
        
        gr.top_block.__init__(self,"FM Receiver")
        
        #Variables
        #self.samp_rate = samp_rate = 25000
        #self.volume = volume = 1
        self.audio_decim = audio_decim = 4
        self.input_samp_rate = input_samp_rate = 250e3
        self.output_samp_rate = output_samp_rate = 48000
        #self.output_correction = output_correction = 0
        self.decim_rate = decim_rate = 250e3
        self.interp_rate = interp_rate = 192e3
        #self.current_demodulation = "fm"
        self.frequency = frequency = 98e6
        self.demod_rate = demod_rate = 192e3
        
        #Blocks
        self.u = usrp.source_c()
        self.u.set_sample_rate(input_samp_rate)
        self.u.set_center_freq(frequency,0)
        self.u.set_gain(40,0)
        
        self.r = filter.rational_resampler_ccf(interp_rate, decim_rate, None, None)
        self.wfm_rcv = blocks.wfm_rcv(demod_rate, audio_decim)
        self.audio_sink = audio_sink(output_samp_rate)
        
        #Connections
        self.connect(self.u, self.r, self.wfm_rcv, self.audio_sink)
        
    #def(
        
        
        
if __name__ == '__main__':

    try:

        FM_Receiver().run()

    except [[KeyboardInterrupt]]:

        pass     
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
