#! /usr/bin/python
# -*- coding: utf-8 -*-

#Alan Rodrigo
#UFMT -IC
#INAU

import wave
import numpy as np
import sys
#from __future__ import print_function, division, unicode_literals

# Created input file with:
audio_in = sys.argv[1]
wr = wave.open(audio_in, 'r')
par = list(wr.getparams()) # Get the parameters from the input.
par[3] = 0 # The number of samples will be set by writeframes.

# Open the output file
audio_out = audio_in[:-4]+'F.wav'
print audio_out
ww = wave.open(audio_out, 'w')
ww.setparams(tuple(par)) # Use the same parameters as the input file.

lowpass = 300 # Remove lower frequencies.
highpass = 20000 # Remove higher frequencies.

sz = wr.getframerate() # Read and process 1 second at a time.
c = int(wr.getnframes()/sz) # whole file
for num in range(c):
    print('Processing {}/{} s'.format(num+1, c))
    da = np.fromstring(wr.readframes(sz), dtype=np.int16)
    left, right = da[0::2], da[1::2] # left and right channel
    lf, rf = np.fft.rfft(left), np.fft.rfft(right)
    lf[:lowpass], rf[:lowpass] = 0, 0 # low pass filter
    lf[55:66], rf[55:66] = 0, 0 # line noise
    lf[highpass:], rf[highpass:] = 0,0 # high pass filter
    nl, nr = np.fft.irfft(lf), np.fft.irfft(rf)
    ns = np.column_stack((nl,nr)).ravel().astype(np.int16)
    ww.writeframes(ns.tostring())
# Close the files.
print ('Fechando arquivos\n')
wr.close()
ww.close()
