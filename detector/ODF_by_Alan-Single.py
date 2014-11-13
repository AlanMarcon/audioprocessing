#!/usr/bin/python
# -*- coding: utf-8 -*-

###################################################################################################
# Developed by: Alan Rodrigo da Silva Marcon                                                      #
#				Nielsen Simões                                                                    #
#                                                                                                 #
# Used Onset Detection Functions                                                                  #
# 		Modal - GLOVER , John ;	 LAZZARINI , Victor; TIMONEY, Joseph. (2011)                      #
#		Essentia - Copyright (C) 2006-2013  Music Technology Group - Universitat Pompeu Fabra     #
#                                                                                                 #
# Research Project envolved                                                                       #
# 		CO.BRA (Computational Bioacoustic Resource Unit)                                          #
#		INAU (Instituto Nacional de Áreas Úmidas)                                                 #
# 		GAIIA (Gerenciamento e Armazenamento Inteligente de Imagens Ambientais)                   #
#																								  #
# Objective:                                                                                      #
#		Develop a tool to help to find snippets with an animal's vocalization                     #
#                                                                                                 #
# UFMT (Mato Grosso Federal University) - IC (Computer Institute)                                 #
# PT - Detector de eventos em áudio produzido por animais                                         #
###################################################################################################

# Garbage collect
import gc

# For Modal ODF
import numpy as np 						
import scipy.io.wavfile as wavfile
import modal
import modal.onsetdetection as od
from modal.onsetdetection import OnsetDetection
from modal.detectionfunctions import ComplexODF
from modal.ui.plot import plot_detection_function, plot_onsets
from scipy.io.wavfile import read
import scipy as sp
import modal.ui.plot as trplot

# Slice audio wave and directory
import sys
import glob
import wave

# Usefull Libraries
import os

# For essentia ODF
from essentia import Pool, array
from essentia.standard import *

# Date and time
import time

#############################################################

#------------Options------------------------------------------------------------------------
def menu():# Show initial menu
	# Show avaliable ODF options	
	# and background definition
	print"""
	[DIGITE O TIPO DE METODO DE DETECCAO]
	[        QUE DESEJA UTILIZAR        ]
	

	| 1 - MODAL SIMPLE
	| 2 - MODAL COMPLEX
	| 3 - ESSENTIA HFC 
	| 4 - ESSENTIA COMPLEX
	| 5 - ESSENTIA MELFLUX
	| 6 - ESSENTIA COMPLEX_PHASE
	| 7 - ESSENTIA RMS
	"""

	valid_options = [1,2,3,4,5,6,7] #Valid options
	option = -1 # Flag option
	while not option in valid_options:
		option = int(raw_input())

	os.system('clear')
	if option ==1:
		print '''
		[METODO : 1 - MODAL SIMPLES]
		'''
	elif option ==2:
		print '''
		[METODO : 2 - MODAL COMPLEXO]
		'''
	elif option ==3:
		print '''
		[METODO : 3 - ESSENTIA HFC]
		'''
	elif option ==4:
		print '''
		[METODO : 4 - ESSENTIA COMPLEX]
		'''
	elif option ==5:
		print '''
		[METODO : 5 - ESSENTIA MELFLUX]
		'''
	elif option ==6:
		print '''
		[METODO : 6 - ESSENTIA COMPLEX_PHASE]
		'''
	elif option ==7:
		print '''
		[METODO : 7 - ESSENTIA RMS]
		'''	

	print'''
		DIGITE O TAMANHO DO BACKGROUND 0~60seg
	'''
	back = -1
	while back <1 or back >61:
		back = int(raw_input())
	# Return:
	# option -> Chosen option
	# back -> Chosen Background
	return option,back 
def deteccoes(arquivo_audio,tipo,audio): # Return a list with all detections by the choice
	# Call chosen ODF
	if tipo == 1:
		return detect_modal_simples(arquivo_audio)
	elif tipo == 2:
		return detect_modal_complex(arquivo_audio)
	elif tipo == 3:
		return detect_essentia(arquivo_audio, 3,audio)
	elif tipo == 4:
		return detect_essentia(arquivo_audio, 4,audio)
	elif tipo == 5:
		return detect_essentia(arquivo_audio, 5,audio)
	elif tipo == 6:
		return detect_essentia(arquivo_audio, 6,audio)
	elif tipo == 7:
		return detect_essentia(arquivo_audio, 7,audio)


#-------------ODF's-------------------------------------------------------------------------
def detect_essentia(arquivo_audio,selected,audio): # ODF using essentia library
	# arquivo_audio <- selected audio file 
	# selected <- detection option
	try:
	    filename = arquivo_audio
	except:
	    print "usage:", sys.argv[0], "<audiofile>"
	    sys.exit()

	# don't forget, we can actually instantiate and call an algorithm on the same line!

	# Phase 1: compute the onset detection function
	# The OnsetDetection algorithm tells us that there are several methods available in Essentia,
	if selected==3:
		od = OnsetDetection(method = 'hfc')
	elif selected==4:
		od = OnsetDetection(method = 'complex')
	elif selected==5:
		od = OnsetDetection(method = 'melflux')
	elif selected==6:
		od = OnsetDetection(method = 'complex_phase')
	elif selected==7:
		od = OnsetDetection(method = 'rms')

	# let's also get the other algorithms we will need, and a pool to store the results
	w = Windowing(type = 'hann')
	fft = FFT() # this gives us a complex FFT
	c2p = CartesianToPolar() # and this turns it into a pair (magnitude, phase)

	pool = Pool()

	# let's get down to business
	print 'Computing onset detection functions...'
	for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512): # Important parameters that we can change
	    mag, phase, = c2p(fft(w(frame)))
	    pool.add('features.method', od(mag, phase))

	# Phase 2: compute the actual onsets locations
	onsets = Onsets()
	print 'Computing onset times...'
	onsets_method = onsets(array([ pool['features.method'] ]), [ 1 ])

	# and mark them on the audio, which we'll write back to disk
	# we use beeps instead of white noise to mark them, as it's more distinctive

	# convert to a simple python list
	listadet = onsets_method.tolist()

	# convert listadet(seconds) to listadet(frames)
	listadet = [int(SecToFrames(x)) for x in listadet if x >= 0]

	#return list of frames ODF
	return listadet
def detect_modal_simples(arquivo_audio): # ODF using modal by GLOVER v1
	# arquivo_audio <- selected audio file 
	# read audio file
	# values between -1 and 1
	audio = audio / 32768.0

	# create detection function
	codf = ComplexODF()
	hop_size = codf.get_hop_size()
	odf = sp.zeros(len(audio)/hop_size, dtype=sp.double)
	codf.process(audio, odf)

	# create onset detection object
	od = OnsetDetection()
	onsets = od.find_onsets(odf) * hop_size

	print 'apllied'

	# Return a python simple list with OD
	return onsets.tolist()
def detect_modal_complex(arquivo_audio): #ODF using modal by GLOVER v2
	# arquivo_audio <- selected audio file 
	file_name = arquivo_audio # taking audio file name
	sampling_rate = wavfile.read(file_name) # extract useful informations
	audio = np.asarray(audio, dtype=np.double)
	audio /= np.max(audio)

	# Define window and hop
	frame_size = 960 
	hop_size = 340

	# Aplling Modal ODF
	odf = modal.ComplexODF()
	odf.set_hop_size(hop_size)
	odf.set_frame_size(frame_size)
	odf.set_sampling_rate(sampling_rate)
	odf_values = np.zeros((len(audio) / hop_size), dtype=np.double)
	odf.process(audio, odf_values)

	# create onset detection object
	onset_det = od.OnsetDetection()
	onset_det.peak_size = 3
	onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()

	print 'apllied'
	# Return a python simple list with OD
	return onsets.tolist()


#-------------Directorys-------------------------------------------------------------------	
def creat_folder(file_name): #Creat a folder for slices
	print 'Creating folder'
	if not os.path.exists(file_name+"-logs"):
		os.makedirs(file_name+"-logs")
	print 'Folder created'


#-------------Audio's Work------------------------------------------------------------------	
def slice(infile, outfilename, start_ms, end_ms): #Slice a wav file
	# infile <- name of file to be slice
	# outfilename <- name of file generated after it was sliced
	# start_ms <- slice start (frame)
	# end_ms <- slice end (frame)

	# Taking audio characteristcs
    width = infile.getsampwidth()
    rate = infile.getframerate()
    length = (end_ms - start_ms)
    start_index = start_ms

    # Setting .wav generated file
    out = wave.open(outfilename, "w")
    out.setparams((infile.getnchannels(), width, rate, length, infile.getcomptype(), infile.getcompname()))
    
    # Recording just the selected frames in the new .wav file
    infile.rewind()
    anchor = infile.tell()
    infile.setpos(anchor + start_index)
    out.writeframes(infile.readframes(length))
    infile.close()
def eh_mono(arquivo_audio): # Verify if is mono 
	# Check if file is mono	
	aa = wave.open(arquivo_audio,'r') # open input audio
	if aa.getnchannels() != 1:
		aa.close()
		return False 
	else: 
		aa.close()
		return True


#-------------String/Numbers/Time Editor----------------------------------------------------
def SecToFrames(sec): # Convert seconds to frames
		# Convert seconds to frames
		# sec -> seconds to be convert 
		return sec*48000 # 48000 =  standard audio input
def frToSeg(fr): #Convert frames to seconds
	# fr <- the frame to be converted
	
	sec = float(fr)/48000
	minu = sec//60
	sec = sec-minu*60
	# Return a corresponding second size to the frame
	return int(minu *10000 + sec * 100)
def escDur(tempo): #Return the  string time
	# tempo <- a number compsed by minutes and seconds

	tempo = str(tempo)[0:-2]
	sec = tempo[-2:]	
	
	# Return a string with a extended vison of time
	if len(tempo) > 2:
		return tempo[0:-2]+' min '+sec+'sec'
	elif sec == '':
		return '0 min 0sec'
	else:
		return '0 min '+sec+'sec'	


#-------------Editing lists------------------------------------------------------------------	
def list_of_slices(lista,back): #Return list of slices
	# lista <- a lista containing detections frames
	# baclground <- a time (seconds) after and before detecions
	sec = 48000 * back  # Setting backgroud seconds
	ini = lista[0] # Slice's start
	end = 0 # Slice's end
	i = 0 # index
	j =0 # index
	dim = len(lista) 
	slices = []

	while i <= dim-1:
		j = i
		ini = lista[i]
		while j < dim:
			end = lista[j]+sec					
			i += 1
			if i == dim: 
				slices.append((ini-sec,lista[-1]))
				break					
			if end < lista[i]:
				if ini < sec:
					slices.append((lista[0],end))
				elif (end > lista[-1]):
					slices.append((ini-sec,lista[-1]))
				else:
					slices.append((ini-sec,end))
				break
			else:
				j = i		

	# Return a list of intervals for each detection
	return slices					
def merge_r_l(l,r,maxi): #Return a list with the merge between l and r channels 
	# l <- list that corresponding left side(audio) or other simple list
	# r <- list that corresponding right side(audio) or other simple list
	# maxi <- define the maximun size(frames) of a merge of two other lists
	
	lr =  []
	dim_l = len(l) # Size of list l
	dim_r = len(r) # Size of list r

	while dim_l > 0 or dim_r > 0:
		l_ok = False
		r_ok = False

		if dim_r > 0 and dim_l > 0:
		    if l[0][0] <= r[0][0]:
		        ini = l[0][0]
		        l_ok = True
		    else:
		        ini= r[0][0]
		        r_ok = True

		    if l[0][1] <= r[0][1]:
		        fim = r[0][1]
		        l_ok = True
		    else:
		        fim = l[0][1]
		        r_ok = True

		    if l[0][1] >= r[0][0] and l[0][0] <= r[0][1]: l_ok = True
		    if r[0][1] >= r[0][1] and r[0][0] >= l[0][1]: r_ok = True     
		    
		    if fim - ini > maxi:
		    	lr.append(l[0])
		    	lr.append(r[0])
		    	l.pop(0)
		    	r.pop(0)
		    	dim_l -= 1
		    	dim_r -= 1
		    else:	
		    	lr.append((ini,fim))

		    	if l_ok: l.pop(0)
		    	if r_ok: r.pop(0)

		    	dim_l = len(l)
		    	dim_r = len(r)

		else: # When any list is empty	
		    if dim_l > 0:
		        lr.append(l[0])
		        l.pop(0)
		        dim_l = len(l)
		    else:
		        lr.append(r[0])
		        r.pop(0)
		        dim_r = len(r)	

	# Return a list that is a combination of two other lists	        
	return lr


#------------Organizer the process of call other functions-----------------------------------
def detecta(audioin,option,backgroud,audio): # ODF main function
	# audioin -> input audio file name 
	# option -> detection option
	# background -> interval before and after detection
	try:

		print ('\nCreation of detecions list...')
		listadet = deteccoes(audioin,option,audio) # Call deteccoes function

		lenlista = len(listadet) # Get the size of listadet

		# with open(audioin[:-4]+'-det_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
		# 	f.write('\n\n\n')
		# 	f.write(str(listadet))
		# 	f.write('\n')

		cont = 0 # count for number of cuts
		tempototal = 0 

		print ('Creation of cuts list...')
		listacorte = list_of_slices(listadet,backgroud) # Taking a list of slices to record
		#with open(audioin[:-4]+'-cut_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
		# 	f.write('\n\n\n')
		#	f.write(str(listacorte))
		#	f.write('\n')			

		# Writing in a log file's name
		with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
			f.write('\n\n--------------------------------------'+'\n')
			f.write(audioin+'\n')
			f.write('--------------------------------------'+'\n')

		# Create a folder for slices
		#creat_folder(audioin)

		lenlistacorte = len(listacorte)	
		while cont < lenlistacorte:
			ini = listacorte[cont][0]
			end = listacorte[cont][1]

			# Writing in a file the standard name of each detection by CO.BRA agreements
			out_file = 'BRMTPSC009S_'+audioin[12:20]+'T'+audioin[21:27]+"AB_S"+str(frToSeg(ini)).zfill(6)+"E"+str(frToSeg(end)).zfill(6)+'ID0'+audioin[len(audioin)-4:]
			with open(audioin[:-4]+'-nomenclatura-'+str(option)+'-b'+str(backgroud)+'.txt','a') as nome:
				nome.write(''+out_file+'\n')

			tempototal += end-ini # Taking the sum of the whole time detection
			# Writing in a log the characteriscs of each detection
			with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','a') as f:
				f.write('\n')
				f.write('--------------------------------------'+'\n')
				f.write('Corte n:'+str(cont+1)+'\n')
				f.write('Inicio do corte: '+escDur(str(frToSeg(ini)))+'\n')
				f.write('Fim do corte: '+escDur(str(frToSeg(end)))+'\n')
				f.write('Tempo total: '+escDur(str(frToSeg(end-ini)))+'\n')	
			
			cont += 1		

			# Save a file containg the detection
			#slice(wave.open(audioin,"r"), out_file , ini, end) #funcao de corte


		# Writing in a log total time of detection
		with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','a') as f:
			f.write('\n\n\n'+escDur(str(frToSeg(tempototal))))


		print 'Tamanho lista de deteccoes: ',len(listadet)	
		print 'Tamanho lista de cortes: ',len(listacorte)
		print 'Numero de cortes: ',cont+1
		print 'Tempo total de cortes: ',escDur(str(frToSeg(tempototal)))

		# Writing in a general execution-log info about the ODF
		with open('log-geral-validacao.txt','a') as lg:			
			part = tempototal
			whole = wave.open(audioin,'r').getnframes()
			if part < whole:
				perc = 100- (float(part)/whole*100)
			else:
				perc  =0
			lg.write(audioin+'\t'+'op: '+str(option)+'\tbackgroud: '+str(backgroud)+'\ttotal: '+escDur(str(frToSeg(tempototal)))+'\tdeteccoes: '+str(len(listadet))+'\t\tcortes: '+str(cont+1)+'\t'+'diminuicao: '+'{0:.2f}%'.format(perc)+'\n')

		# If all was right return true
		return True


	except:
		print ('Deu ruim!')
		return False


#------------Main----------------------------------------------------------------------------
def main(): # Main function
	os.system('clear')
	#Exibir menu
	#option,backgroud = menu()

	# Enable Garbage Colector
	gc.enable()

	starttime = time.asctime(time.localtime(time.time())) #Execution start

	print 'Loading audio file...'
	audio = MonoLoader(filename = sys.argv[1])() # A numpy array contain the actual used aidio
	gc.collect()

	#Call the detection manually
	detecta(sys.argv[1],3,10,audio)
	gc.collect()
	detecta(sys.argv[1],4,10,audio)
	gc.collect()
	detecta(sys.argv[1],6,10,audio)
	gc.collect()

	del audio

	endtime = time.asctime(time.localtime(time.time()))  #Execution end

	with open('log-geral-validacao.txt','a') as lg:
		lg.write('Start time: '+str(starttime))
		lg.write('\nEnd time:   '+str(endtime))
		lg.write('\n\n')
		
	#Finished
	print('Done!')


# Start of execution
if __name__ == '__main__':
	main()
