#!/usr/bin/python

# scan a wave file for dropouts - repeated samples for more than thresh consecutive samples

import wave 
import struct
import numpy as np
import sys

fname="ph1995-06-13d1t07_raw.wav"
thresh= 100

CHUNK=4096
#  1024 0m56.249s
#  2048 0m54.811s
#  4096 0m54.317s
#  8192 0m55.491s
# 16384 0m56.624s

class Dropout_Scan:
    """
    " scan a wav file from a DAT transfer for "drop-outs"
    " or sections where successive samples are equal for a count
    " of more than thresh samples
    """
    def __init__(self):
        first_left=None
        last_left=None
        count_left=0
        first_right=None
        last_right=None
        count_right=0
    # END Dropout_Scan.init()
        
    def sample_to_time( self, sample ):
        sample_rate = self.framerate
        seconds = sample // sample_rate
        samples = sample  % sample_rate
        minutes = seconds // 60
        seconds = seconds  % 60
        timestr = "{0:08d} {1:03d}m{2:02d}s+{3:05d}samp".format( sample, minutes, seconds, samples)
        return timestr

    def init_file(self):
        self.left_state  = { "first":None, "last":None, "count":0, "prev":0, "channel":"L" }
        self.right_state = { "first":None, "last":None, "count":0, "prev":0, "channel":"R" }
        self.error = 0
    # END Dropout_Scan.init_file()

    def analyze_frame( self, sample, state ):
        #print("A: "+fname+" {0:s} {1:s}".format( self.sample_to_time( self.frame_num), state["channel"] ))
        for i in range( len(sample) ):
            if sample[i] == state["prev"]:
                if 0 == state["count"]:
                    state["first"] ="{0:s} {1:5d}".format( self.sample_to_time( i+ self.frame_num), sample[i] )
                    state["count"] = 1
                else:
                    state["count"] += 1
                    if state["count"] > thresh:
                        state["last"] = "{0:s} {1:5d}".format( self.sample_to_time( i + self.frame_num ), sample[i])
            else: # not equal
                if state["first"] is not None and state["last"] is not None:
                    if self.error == 0:
                        print("") # force newline
                        self.error = 1
                    print ( state["channel"] + " Start " + state["first"] + " End " + state["last"] +
                            " Dur " + self.sample_to_time( state["count"] ))
                state["first"]=None
                state["last"]=None
                state["count"] = 0
                state["prev"] = sample[i]
    # END Dropout_Scan.analyze_frame()
        
    def analyze_frame_last( self, state ):
        if state["first"] is not None and state["last"] is not None:
            if self.error == 0:
                print("") # force newline
                self.error = 1
            print ( state["channel"] + " Start " + state["first"] + " End " + state["last"] +
                    " Dur " + self.sample_to_time( state["count"] ))
    # END Dropout_Scan.analyze_frame_last()
        
    
    def scan_file( self, fname ):
        if fname is None:
            raise ValueError

        wav = wave.open (fname, "r")

        (self.nchannels, self.sampwidth, self.framerate,
         self.nframes, self.comptype, self.compname)     = wav.getparams ()

        #print("O: "+fname+" {0:d} channels {1:d} frames".format(self.nchannels, self.nframes) )
        
        print("A: "+fname, end='', flush=True)
        self.init_file()

        # ceil( nframes / CHUNK)
        # thanks to https://stackoverflow.com/questions/14822184/is-there-a-ceiling-equivalent-of-operator-in-python
        # ceil ( a /b ) == -( -a // b)
        num_chunks = -( -self.nframes // CHUNK)
        
        self.frame_num = 0
        
        for chunk_num in range( num_chunks ):

            # handle possibly odd sized last chunk
            if self.frame_num + CHUNK > self.nframes:
                chunk_size = self.nframes - chunk_num*CHUNK
            else:
                chunk_size = CHUNK

            # read the next chunk
            frame = wav.readframes ( chunk_size )
            out = struct.unpack_from ( "%dh" % self.nchannels * chunk_size, frame )

            # Convert 2 channels to numpy arrays and analyze for drop-outs
            if self.nchannels == 2:
                left_samples  = np.array (list ( out[0::2] ))
                right_samples = np.array (list ( out[1::2] ))
                self.analyze_frame( left_samples,  self.left_state )
                self.analyze_frame( right_samples, self.right_state )
            else:
                left_samples  = np.array (list ( out[0::2] ))
                self.analyze_frame( left_samples, self.left_state )
            self.frame_num += chunk_size

        # catch "hanging" dropout at end of file
        self.analyze_frame_last( self.left_state )
        self.analyze_frame_last( self.right_state )

        # close file
        wav.close()

        if self.error == 0:
            print(" OK")
        else:
            print( "Done" )
    # END Dropout_Scan.scan_file()

if len(sys.argv) > 1:
    ds=Dropout_Scan()
    
    for fname in sys.argv[1:]:
        #print("F: "+fname)
        ds.scan_file( fname )

