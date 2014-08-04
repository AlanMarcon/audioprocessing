#! /usr/bin/python
# -*- coding: utf-8 -*-

#Alan Rodrigo
#UFMT -IC
#INAU

from scipy.io import wavfile
import glob
import os
arquivos = glob.glob('*.wav')

os.system("clear")
for i in arquivos:
	fs, data = wavfile.read(arquivos[i])
	wavfile.write(audio_file[:-4]+'-l.wav',fs,data[:,0])
	wavfile.write(audio_file[:-4]+'-r.wav',fs,data[:,1])
	wavfile.closeall()
