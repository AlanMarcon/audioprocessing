#!/usr/bin/python
# -*- coding: utf-8 -*-

#Alan Rodrigo
#UFMT -IC
#Detector de eventos em áudio stereo no formato .wav

# garbage collect
import gc

# Detect tools
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


# slice audio wave and directory
import sys
import time
from os import system
import os
import glob
import wave

# for essentia detection
from essentia import Pool, array
from essentia.standard import *

# date and time
import time


#############################################################
def menu():# Show initial menu
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

		valid_options = [1,2,3,4,5,6,7]
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

		return option,back

def detecta(entrada):
	# audioin -> input audio file name 
	# option -> detection option
	# background -> interval before and after detection
	infile = str(entrada.infile)
	option =  int(entrada.option)
	backgroud = int(entrada.backgroud)
	
	def SecToFrames(sec): # Convert seconds to frames
		# Convert seconds to frames
		# sec -> seconds to be convert 
		return sec*48000 # 48000 =  standard audio input

	def eh_mono(arquivo_audio): # Verify if is mono 
		# Check if file is mono	
		aa = wave.open(arquivo_audio,'r') # open input audio
		if aa.getnchannels() != 1:
			aa.close()
			return False 
		else: 
			aa.close()
			return True

	def detect_essentia(arquivo_audio,selected): #ODF using essentia library
		# 
		try:
		    filename = arquivo_audio
		except:
		    print "usage:", sys.argv[0], "<audiofile>"
		    sys.exit()

		# don't forget, we can actually instantiate and call an algorithm on the same line!
		global audio

		# Phase 1: compute the onset detection function
		# The OnsetDetection algorithm tells us that there are several methods available in Essentia,
		# let's do two of them
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
		for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
		    mag, phase, = c2p(fft(w(frame)))
		    pool.add('features.method', od(mag, phase))

		# Phase 2: compute the actual onsets locations
		onsets = Onsets()
		print 'Computing onset times...'
		onsets_method = onsets(array([ pool['features.method'] ]), [ 1 ])

		# and mark them on the audio, which we'll write back to disk
		# we use beeps instead of white noise to mark them, as it's more distinctive

		#convertendo para o tipo list
		listadet = onsets_method.tolist()

		#convertendo os segundos para frames
		listadet = [int(SecToFrames(x)) for x in listadet if x >= 0]
		 
		return listadet

	def detect_modal_simples(arquivo_audio): #ODF using modal by GLOVER v1
		from modal.onsetdetection import OnsetDetection
		from modal.detectionfunctions import ComplexODF
		from scipy.io.wavfile import read

		# read audio file
		print type(audio)
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
		sampling_rate = wavfile.read(file_name)
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
		
	def deteccoes(arquivo_audio,tipo): # Return a list with all detections by the choice

		if tipo == 1:
			return detect_modal_simples(arquivo_audio)
		elif tipo == 2:
			return detect_modal_complex(arquivo_audio)
		elif tipo == 3:
			return detect_essentia(arquivo_audio, 3)
		elif tipo == 4:
			return detect_essentia(arquivo_audio, 4)
		elif tipo == 5:
			return detect_essentia(arquivo_audio, 5)
		elif tipo == 6:
			return detect_essentia(arquivo_audio, 6)
		elif tipo == 7:
			return detect_essentia(arquivo_audio, 7)

	def creat_folder(file_name): #Creat a folder for slices
		print 'Criando pasta'
		if not os.path.exists(file_name+"-logs"):
			os.makedirs(file_name+"-logs")
		print 'Pasta criada'
		
	def slice(infile, outfilename, start_ms, end_ms, file_name): #Slice a wav file
	    width = infile.getsampwidth()
	    rate = infile.getframerate()
	    length = (end_ms - start_ms)
	    start_index = start_ms

	    out = wave.open(outfilename, "w")
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
		
	def escDur(tempo): #Return the  string time
		tempo = str(tempo)[0:-2]
		sec = tempo[-2:]	
		if len(tempo) > 2:
			return tempo[0:-2]+'min '+sec+'seg'
		elif sec == '':
			return '0 min 0seg'
		else:
			return '0min '+sec+'seg'	
	
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

		print ('\nCriando lista de deteccoes...')
		listadet = deteccoes(audioin,option)

		lenlista = len(listadet)

		# with open(audioin[:-4]+'-det_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
		# 	f.write('\n\n\n')
		# 	f.write(str(listadet))
		# 	f.write('\n')

		cont = 0
		fn = audioin
		tempototal = 0

		print ('Criando lista de cortes...')
		listacorte = list_of_slices(listadet)

		# with open(audioin[:-4]+'-cut_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
		# 	f.write('\n\n\n')
		# 	f.write(str(listacorte))
		# 	f.write('\n')			

		with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','w') as f:
			f.write('\n\n--------------------------------------'+'\n')
			f.write(audioin+'\n')
			f.write('--------------------------------------'+'\n')

		#creat_folder(audioin)

		lenlistacorte = len(listacorte)	
		while cont < lenlistacorte:
			ini = listacorte[cont][0]
			end = listacorte[cont][1]

			#out_file = fn[:len(fn)-4] +"-S"+str(frToSeg(ini)).zfill(6)+"E"+str(frToSeg(end)).zfill(6)+"-slice"+str(cont) +fn[len(fn)-4:]
			tempototal += end-ini

			with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','a') as f:
				f.write('\n')
				f.write('--------------------------------------'+'\n')
				f.write('Corte n:'+str(cont)+'\n')
				f.write('Inicio do corte: '+escDur(str(frToSeg(ini)))+'\n')
				f.write('Fim do corte: '+escDur(str(frToSeg(end)))+'\n')
				f.write('Tempo total: '+escDur(str(frToSeg(end-ini)))+'\n')	
			
			cont += 1		
			#slice(wave.open(audioin,"r"), out_file , ini, end, fn) #funcao de corte


		with open(audioin[:-4]+'-log_list-op-'+str(option)+'-b'+str(backgroud)+'.txt','a') as f:
			f.write('\n\n\n'+escDur(str(frToSeg(tempototal))))

		print 'Tamanho lista de deteccoes: ',len(listadet)	
		print 'Tamanho lista de cortes: ',len(listacorte)
		print 'Numero de cortes: ',cont+1
		print 'Tempo total de cortes: ',escDur(str(frToSeg(tempototal)))

		with open('log-geral-validacao.txt','a') as lg:			
			part = tempototal
			whole = wave.open(audioin,'r').getnframes()
			if part < whole:
				perc = 100- (float(part)/whole*100)
			else:
				perc  =0
			lg.write(audioin+'\t'+'op: '+str(option)+'\tbackgroud: '+str(backgroud)+'\ttotal: '+escDur(str(frToSeg(tempototal)))+'\tdeteccoes: '+str(len(listadet))+'\t\tcortes: '+str(cont+1)+'\t'+'diminuicao: '+'{0:.2f}%'.format(perc)+'\n')

		return True
	except:
		print ('Deu ruim!')
		return False


def multipool():
	from multiprocessing import Pool
	print 'Loading audio file...'
	audio = MonoLoader(filename = sys.argv[1])()
	a = AudioInfo(sys.argv[1],3,10)
	b = AudioInfo(sys.argv[1],4,10)
	c = AudioInfo(sys.argv[1],6,10)

	todo = []
	todo.append(a)
	todo.append(b)
	todo.append(c)

	pool = Pool(3)
	pool.map(detecta,todo)

class AudioInfo(object):
	def __init__(self, infile, option, backgroud):
		super(AudioInfo, self).__init__()
		self.infile = infile
		self.option = option
		self.backgroud = backgroud

if __name__ == '__main__':
	os.system('clear')
	#Exibir menu
	#option,backgroud = menu()

	gc.enable()

	starttime = time.asctime(time.localtime(time.time())) #Execution start
	multipool() #
	endtime = time.asctime(time.localtime(time.time()))  #Execution end

	with open('log-geral-validacao.txt','a') as lg:
		lg.write('Start time: '+str(starttime))
		lg.write('\nEnd time:   '+str(endtime))
		lg.write('\n\n')
	gc.collect()

	#Finished
	#os.system('clear')
	print('Done!')
