#!/usr/bin/python
# -*- coding: utf-8 -*-

#Alan Rodrigo
#UFMT -IC
#Detector de eventos em áudio stereo no formato .wav
#

#Detect tools
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


#slice audio wave and directory
import sys
import time
from os import system
import os
import glob
import wave

#for essentia detection
from essentia import Pool, array
from essentia.standard import *


#############################################################
def menu():# Show initial menu
		print"""
		[DIGITE O TIPO DE METODO DE DETECCAO]
		[        QUE DESEJA UTILIZAR        ]
		

		| 1 - MODAL SIMPLE
		| 2 - MODAL COMPLEX
		| 3 - ESSENTIA HFC 
		| 4 - ESSENTIA COMPLEX

		"""

		valid_options = [1,2,3,4]
		option = -1
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
		
		print'''
			DIGITE O TAMANHO DO BACKGROUND 0~60seg
		'''
		back = -1
		while back <1 or back >61:
			back = int(raw_input())

		return option,back

def detecta(audioin,option,backgroud):
			
	def SecToFrames(sec):
		return sec*48000

	def eh_mono(arquivo_audio): # Check if file is mono	
		aa = wave.open(arquivo_audio,'r')
		if aa.getnchannels() != 1:
			aa.close()
			return False 
		else: 
			aa.close()
			return True

	def detect_essentia(arquivo_audio,selected):	#ODF using essentia library

		try:
		    filename = arquivo_audio
		except:
		    print "usage:", sys.argv[0], "<audiofile>"
		    sys.exit()

		# don't forget, we can actually instantiate and call an algorithm on the same line!
		print 'Loading audio file...'
		audio = MonoLoader(filename = filename)()

		# Phase 1: compute the onset detection function
		# The OnsetDetection algorithm tells us that there are several methods available in Essentia,
		# let's do two of them
		od1 = OnsetDetection(method = 'hfc')
		od2 = OnsetDetection(method = 'complex')

		# let's also get the other algorithms we will need, and a pool to store the results

		w = Windowing(type = 'hann')
		fft = FFT() # this gives us a complex FFT
		c2p = CartesianToPolar() # and this turns it into a pair (magnitude, phase)

		pool = Pool()

		# let's get down to business
		print 'Computing onset detection functions...'
		for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
		    mag, phase, = c2p(fft(w(frame)))
		    pool.add('features.hfc', od1(mag, phase))
		    pool.add('features.complex', od2(mag, phase))


		# Phase 2: compute the actual onsets locations
		onsets = Onsets()

		print 'Computing onset times...'
		onsets_hfc = onsets(# this algo expects a matrix, not a vector
		                    array([ pool['features.hfc'] ]),

		                    # you need to specify weights, but as there is only a single
		                    # function, it doesn't actually matter which weight you give it
		                    [ 1 ])

		onsets_complex = onsets(array([ pool['features.complex'] ]), [ 1 ])

		# and mark them on the audio, which we'll write back to disk
		# we use beeps instead of white noise to mark them, as it's more distinctive
		print 'Writing audio files to disk with onsets marked...'

		# mark the 'hfc' onsets:

		#convertendo para o tipo list
		listadethfc = onsets_hfc.tolist()
		listadetcomplex = onsets_complex.tolist()

		#convertendo os segundos para frames
		listadethfc = [int(SecToFrames(x)) for x in listadethfc if x >= 0]
		listadetcomplex = [int(SecToFrames(x)) for x in listadetcomplex if x >= 0]

		print 'aplicou'
		if selected == 3:
			return listadetcomplex
		else:
			return listadethfc

	def detect_modal_simples(arquivo_audio): #ODF using modal by GLOVER v1
		from modal.onsetdetection import OnsetDetection
		from modal.detectionfunctions import ComplexODF
		from scipy.io.wavfile import read

		# read audio file
		audio = read(arquivo_audio)[1]

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

		print 'aplicou'
		return onsets.tolist()

	def detect_modal_complex(arquivo_audio): #ODF using modal by GLOVER v2
		file_name = arquivo_audio
		sampling_rate, audio = wavfile.read(file_name)
		audio = np.asarray(audio, dtype=np.double)
		audio /= np.max(audio)

		frame_size = 960
		hop_size = 340

		odf = modal.ComplexODF()
		odf.set_hop_size(hop_size)
		odf.set_frame_size(frame_size)
		odf.set_sampling_rate(sampling_rate)
		odf_values = np.zeros((len(audio) / hop_size), dtype=np.double)
		odf.process(audio, odf_values)

		onset_det = od.OnsetDetection()
		onset_det.peak_size = 3
		onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()

		print 'aplicou'
		return onsets.tolist()
		
	def deteccoes(arquivo_audio,tipo): #Return a list with all detections	

		if tipo == 1:
			print 'Aplicando metodo 1'
			return detect_modal_simples(arquivo_audio)
		elif tipo == 2:
			print 'Aplicando metodo 2'
			return detect_modal_complex(arquivo_audio)
		elif tipo == 3:
			print 'Aplicando metodo 3'
			return detect_essentia(arquivo_audio, 3)
		elif tipo == 4:
			return detect_essentia(arquivo_audio, 4)

	def creat_folder(file_name): #Creat a folder for slices
		if not os.path.exists(file_name+"-out"):
			os.makedirs(file_name+"-out")
		
	def slice(infile, outfilename, start_ms, end_ms, file_name): #Slice a wav file
	    width = infile.getsampwidth()
	    rate = infile.getframerate()
	    length = (end_ms - start_ms)
	    start_index = start_ms

	    out = wave.open(os.path.join(file_name+"-out/"+outfilename), "w")
	    out.setparams((infile.getnchannels(), width, rate, length, infile.getcomptype(), infile.getcompname()))
	    
	    infile.rewind()
	    anchor = infile.tell()
	    infile.setpos(anchor + start_index)
	    out.writeframes(infile.readframes(length))
	    infile.close()   
	
	def frToSeg(fr): #Convert frames to seconds
		sec = float(fr)/48000
		minu = sec//60
		sec = sec-minu*60
		return int(minu *10000 + sec * 100)
		
	def escDur(tempo): #Print the time
		tempo = str(tempo)[0:-2]
		sec = tempo[-2:]	
		if len(tempo) > 2:
			return tempo[0:-2]+'min '+sec+'seg'
		elif sec == '':
			return '0seg'
		else:
			return sec+'seg'	
	
	def list_of_slices(lista): #Return list of slices
		sec = 48000*backgroud  # Backgroud seconds
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
		return slices			

	def merge_r_l(l,r,maxi): #Return a list with the merge between l and r channels 
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

			else: # When one list is empty	
			    if dim_l > 0:
			        lr.append(l[0])
			        l.pop(0)
			        dim_l = len(l)
			    else:
			        lr.append(r[0])
			        r.pop(0)
			        dim_r = len(r)	

		return lr

	try:
		print ('Lendo arquivo %s ...'%audioin)
		print ('Verificando se eh mono\n')
		if eh_mono(audioin):

			print ('Criando lista de deteccoes.\n')
			listadet = deteccoes(audioin,option)
			print ('Lista criada.\n')

			lenlista = len(listadet)
			print ('Tamanho de lista- %d \n'%lenlista)


			with open(audioin[:-4]+'-det_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
				f.write('\n\n\n')
				f.write(str(listadet))
				f.write('\n')

			#print ('Criando pasta.\n')	
			#creat_folder(audioin)
				

			cont = 0
			fn = audioin
			tempototal = 0

			print ('Criando lista de cortes...')
			listacorte = list_of_slices(listadet)
			print (len(listacorte))
			with open(audioin[:-4]+'-cut_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
				f.write('\n\n\n')
				f.write(str(listacorte))
				f.write('\n')

			print ('lista criada')
			

			with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
				f.write('\n\n--------------------------------------'+'\n')
				f.write(audioin+'\n')
				f.write('--------------------------------------'+'\n')

			lenlistacorte = len(listacorte)	
			while cont < lenlistacorte:
				ini = listacorte[cont][0]
				end = listacorte[cont][1]

				out_file = fn[:len(fn)-4] +"-S"+str(frToSeg(ini)).zfill(6)+"E"+str(frToSeg(end)).zfill(6)+"-slice"+str(cont) +fn[len(fn)-4:]
				tempototal += end-ini

				with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','a') as f:
					f.write('\n')
					f.write('--------------------------------------'+'\n')
					f.write('Corte n:'+str(cont)+'\n')
					f.write('Inicio do corte: '+escDur(str(frToSeg(ini)))+'\n')
					f.write('Fim do corte: '+escDur(str(frToSeg(end)))+'\n')
					f.write('Tempo total: '+escDur(str(frToSeg(end-ini)))+'\n')	
				
				#slice(wave.open(audioin,"r"), out_file , ini, end, fn) #funcao de corte
				cont += 1			 


			with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','a') as f:
				f.write('\n\n\n'+escDur(str(frToSeg(tempototal))))
		else:
			return False

		return True
	except:
		return False

if __name__ == '__main__':
	os.system('clear')

	option,backgroud = menu()

	detecta(sys.argv[1],option,backgroud) #Call detection function		
