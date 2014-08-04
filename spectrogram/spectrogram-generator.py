#! /usr/bin/python
# -*- coding: utf-8 -*-

#Alan Rodrigo
#UFMT -IC
#INAU

import os
import wave
import sys
import pylab

def graph_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    pylab.figure(num=None, figsize=(8, 6))
    pylab.subplot(111)
    pylab.title('spectrogram of %r' % wav_file)
    pylab.ylabel('Frequency')
    pylab.xlabel('Time')
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.png')


def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate


if __name__ == '__main__':
    wav_file = sys.argv[1]
    graph_spectrogram(wav_file)
