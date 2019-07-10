#!/usr/bin/env python

from gnuradio import blocks
from gnuradio import filter
from gnuradio import audio
from gnuradio import analog
import uhd
from gnuradio.eng_option import eng_option
from gnuradio import eng_notation
from gnuradio import gr
#from optparse import OptionParser
#import sys



class Test_Ex(gr.top_block):

    def __init__(self):
        
        gr.top_block.__init__(self)
        '''
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-a", "--args", type="string", default="",
                          help="UHD device address args [default=%default]")
        
        parser.add_option("", "--spec", type="string", default=None,
	                  help="Subdevice of UHD device where appropriate")
        parser.add_option("-A", "--antenna", type="string", default=None,
                          help="select Rx Antenna where appropriate")
        parser.add_option("-f", "--freq", type="eng_float", default=100.1e6,
                          help="set frequency to FREQ", metavar="FREQ")
        parser.add_option("-g", "--gain", type="eng_float", default=None,
                          help="set gain in dB (default is midpoint)")
        parser.add_option("-V", "--volume", type="eng_float", default=None,
                          help="set volume (default is midpoint)")
        parser.add_option("-O", "--audio-output", type="string", default="default",
                          help="pcm device name.  E.g., hw:0,0 or surround51 or /dev/dsp")
        parser.add_option("", "--freq-min", type="eng_float", default=87.9e6,
                          help="Set a minimum frequency [default=%default]")
        parser.add_option("", "--freq-max", type="eng_float", default=108.1e6,
                          help="Set a maximum frequency [default=%default]")

        (options, args) = parser.parse_args()
        if len(args) != 0:
            parser.print_help()
            sys.exit(1)

        '''
        self.usrp_rate = usrp_rate = 250000
        self.interp = interp = 192000
        self.decim = decim = 250000
        self.audio_decim = audio_decim = 10
        self.quad_rate = quad_rate = 192000
        self.audio_rate = audio_rate = 48000
        nfilts = 32
        self.usrp_src = uhd.usrp_source([], stream_args=uhd.stream_args('fc32'))
       
        '''
        # Set the subdevice spec
        if(options.spec):
            self.usrp_src.set_subdev_spec(options.spec, 0)

        # Set the antenna
        if(options.antenna):
            self.usrp_src.set_antenna(options.antenna, 0)
        '''
            
        self.usrp_src.set_samp_rate(usrp_rate)
        self.usrp_src.set_antenna(TX/RX,0)
        
        self.FM_rcv = analog.wfm_rcv(quad_rate, audio_decim)
        
        chan_coeffs = filter.optfir.low_pass(nfilts,           # gain
                                             nfilts*usrp_rate, # sampling rate
                                             80e3,             # passband cutoff
                                             115e3,            # stopband cutoff
                                             0.1,              # passband ripple
                                             60)               # stopband attenuation
                                             
        self.chan_filt = filter.pfb.arb_resampler_ccf(interp, chan_coeffs, nfilts)
        
        self.audio = audio.sink(sample_rate, "")
        
        self.connect(self.usrp_src, self.chan_filt, self.FM_rcv, self.audio)
        
if __name__ == '__main__':

    try:

        Test_Ex().run()

    except [[KeyboardInterrupt]]:

        pass       

'''
if __name__ == '__main__':

    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")

    (options, args) = parser.parse_args()

    tb = Test_Ex()

    tb.start()

    raw_input('Press Enter to quit: ')

    tb.stop()

    tb.wait()       
'''            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
