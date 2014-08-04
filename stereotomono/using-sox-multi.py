#! /usr/bin/python
# -*- coding: utf-8 -*-
#!/bin/bash

#Alan Rodrigo
#UFMT -IC
#Converts all files in folder stereo .wav files into mono .wav files
#Only work in Linux plataform using sox
#Default extract left channel ignore right

import os, sys
import commands
import glob
from os import *

arquivos = glob.glob('*.wav')

os.system("clear")

for arq in arquivos:
	print arq,' ======> ',arq[:-4]+"-l.wav"

	comando =str('sox '+arq+' '+arq[:-4]+'-l.wav'+' remix 1')
	print ''
	os.system(comando)

for arq in arquivos:
	print arq,' ======> ',arq[:-4]+"-r.wav"

	comando =str('sox '+arq+' '+arq[:-4]+'-r.wav'+' remix 2')
	print ''
	os.system(comando)	
