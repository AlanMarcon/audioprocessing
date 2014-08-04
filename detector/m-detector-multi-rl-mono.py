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

#slice audio wave and directory
import sys
import time
from os import system
import os
import glob
import wave


#############################################################
def detecta(arquivo_audio_l,arquivo_audio_r,file_name):

	def eh_mono(arquivo_audio):		
		aa = wave.open(arquivo_audio,'r')
		if aa.getnchannels() != 1:
			aa.close()
			return False 
		else: 
			aa.close()
			return True

	def deteccoes(arquivo_audio): #Return a list with all detections	
		file_name = arquivo_audio
		sampling_rate, audio = wavfile.read(file_name)
		audio = np.asarray(audio, dtype=np.double)
		audio /= np.max(audio)

		frame_size = 4096 #960
		hop_size = 4096 #340
		
		odf = modal.PeakAmpDifferenceODF()
		odf.set_frame_size(frame_size)
		odf.set_hop_size(hop_size)
		odf.set_sampling_rate(sampling_rate)
		odf_values = []
		onsets = []	
		threshold = []
		onset_det = od.RTOnsetDetection()
		
		# pad the input audio if necessary
		if len(audio) % odf.get_frame_size() != 0:
			n_zeros = odf.get_frame_size() - (len(audio) % odf.get_frame_size())
			audio = np.hstack((audio,np.zeros(n_zeros,dtype=np.double)))
		'''
		print ''
		print '------------------------------------------------------'	
		print "sampling_rate: ", sampling_rate
		print "Audio file:", file_name
		print "Total length:", float(len(audio)) / sampling_rate, "seconds"
		'''
		lista = onsets
		audio_pos = 0
		i = 0
		start_time = time.time()
		while audio_pos <= len(audio) - odf.get_frame_size():
		    frame = audio[audio_pos:audio_pos + odf.get_frame_size()]
		    odf_value = odf.process_frame(frame)
		    odf_values.append(odf_value)
		    det_results = onset_det.is_onset(odf_value, return_threshold=True)
		    if det_results[0]:
		        onsets.append(i * odf.get_hop_size())
		    threshold.append(det_results[1])
		    audio_pos += odf.get_hop_size()
		    i += 1
		run_time = time.time() - start_time
		
		return lista

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
		sec = 48000*10  # Backgroud seconds
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

	def merge_r_l(l,r):
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
		if eh_mono(arquivo_audio_l) and eh_mono(arquivo_audio_r): #Verify if both files are mono
		
			print ('\nDetectando... L')			
			lista_l = deteccoes(arquivo_audio_l) #List with left detections
			print 'Deteccoes L:',len(lista_l)

			print ('\nDetectando... R')			
			lista_r = deteccoes(arquivo_audio_r) #List with right detections
			print 'Deteccoes R:',len(lista_r)
			
			print '\nCriando lista de slices L...'	
			lista_l = list_of_slices(lista_l)

			print '\nCriando lista de slices R...'
			lista_r = list_of_slices(lista_r)


			print '\nMergindo listas L R...'
			lista_lr = merge_r_l(lista_l,lista_r)		
			print 'Tamanho merge:',len(lista_lr)

			len_lista_lr = len(lista_lr)
			creat_folder(file_name) #Creat a folder for slices

			cont = 0
			fn = file_name

			if len(lista_l) > len(lista_r):
				escolhido = arquivo_audio_l
			else:
				escolhido = arquivo_audio_r	 

			while cont < len_lista_lr:
				ini = lista_lr[cont][0]
				end = lista_lr[cont][1]
				out_file = fn[:len(fn)-4] +"-S"+str(frToSeg(ini)).zfill(6)+"E"+str(frToSeg(end)).zfill(6)+"-slice"+str(cont) +fn[len(fn)-4:]
				print ""
				print "--------------------------------------------"
				print "Corte n: ",cont
				print "Inicio do corte: ",escDur(str(frToSeg(ini)))
				print "Fim do corte: ",escDur(str(frToSeg(end)))
				slice(wave.open(escolhido,"r"), out_file , ini, end, fn) #funcao de corte
				cont += 1			 

		else:
			return False

		return True
	except:
		return False


if __name__ == '__main__':
	os.system('clear')		
	arquivos_left = glob.glob('*l.wav') #Find all files l.wav at folder
	arquivos_right = glob.glob('*r.wav') #Find all files r.wav at folder
	dim = len(arquivos_left) #Number of files

	for i in range(0,dim): #block file left
		for j in range(0,dim): #find file right equal left
			if (arquivos_left[i][:-6] == arquivos_right[j][:-6]):
				print ("\n\n"+arquivos_left[i]+' <=> '+arquivos_right[j])
				detecta(arquivos_left[i],arquivos_right[j],arquivos_left[i][:-6]+'.wav') #Call detection function		
				break
