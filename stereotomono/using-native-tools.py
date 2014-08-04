#! /usr/bin/python
# Converts stereo .wav files into mono .wav files

import struct # For converting the (two's complement?) binary data to integers
import sys # For command line arguments
import wave # For .wav input and output
import time
from os import system

system("clear")

# Set sensible defaults
channel = 'both'
inputFilenames = []

acceptableChannels = ['both', 'left', 'right']

# Override the defaults
for argument in sys.argv:
	# Override the filename
	if (argument[-4:].lower() == '.wav'):
		inputFilenames.append(argument)
		continue

	# Override the channel
	if (argument[:10] == '--channel='):
		if (argument[10:] in acceptableChannels):
			channel = argument[10:]
			continue
		else:
			print(argument[10:], "ain't any channel I ever heard of")
			exit()
a
if (len(inputFilenames) == 0):
	print("""\
Usage:
python3 makemono.py [option...] input.wav

Options: (may appear before or after arguments)
	--channel=foo
		set which channel to extract (default is both, other options are left and right)
	""")
	exit()
	
###############################################
# TO LEFT
#########

# Cycle through files
for inputFilename in inputFilenames:
	outputFilename = inputFilename[:-4] + '-left' + '.wav'
	print""
	try:
		inputFile = wave.open(inputFilename, 'r')
	except:
		print(inputFilename, "doesn't look like a valid .wav file.  Skipping.")
		continue

	if (inputFile.getnchannels() != 2):
		print(inputFilename, "isn't stereo.  Skipping.")
		continue

	try:
		outputFile = wave.open(outputFilename, 'w')
		outputFile.setnchannels(1)
		outputFile.setsampwidth(inputFile.getsampwidth())
		outputFile.setframerate(inputFile.getframerate())
	except:
		print("I couldn't write to", outputFilename, "Skipping.")
		continue

	sampleWidth = inputFile.getsampwidth()
	
	print"""
		##################################
		#   Extraindo canal esquerdo...  #
		##################################
	 """
	print "\t",inputFilename, '=====>', outputFilename
	
	start_time = time.clock()
	for iteration in range (0, inputFile.getnframes()):
		datum = inputFile.readframes(1)
		outputFile.writeframes(datum[:sampleWidth]) # Write the left channel; ignore the right channel.

	inputFile.close()
	outputFile.close()
	print "\t",outputFilename, "gerado."
	print '\tTempo: ',start_time - time.clock()
	print ""

###############################################
# TO RIGHT
##########

# Cycle through files
for inputFilename in inputFilenames:
	outputFilename = inputFilename[:-4] + '-right' + '.wav'
	print ""
	try:
		inputFile = wave.open(inputFilename, 'r')
	except:
		print(inputFilename, "doesn't look like a valid .wav file.  Skipping.")
		continue

	if (inputFile.getnchannels() != 2):
		print(inputFilename, "isn't stereo.  Skipping.")
		continue

	try:
		outputFile = wave.open(outputFilename, 'w')
		outputFile.setnchannels(1)
		outputFile.setsampwidth(inputFile.getsampwidth())
		outputFile.setframerate(inputFile.getframerate())
	except:
		print("I couldn't write to", outputFilename, "Skipping.")
		continue

	sampleWidth = inputFile.getsampwidth()

	print"""
		##################################
		#   Extraindo canal direito...   #
		##################################
	 """
	print "\t",inputFilename, '=====>', outputFilename
	start_time = time.clock()
	for iteration in range (0, inputFile.getnframes()):
		datum = inputFile.readframes(1)
		outputFile.writeframes(datum[sampleWidth:]) # Write the right channel; ignore the left channel.

	inputFile.close()
	outputFile.close()
	print "\t",outputFilename, "gerado."
	print '\tTempo: ',start_time - time.clock()
	print ""
	
	print '\tExtracao de canais concluida com sucesso.'
