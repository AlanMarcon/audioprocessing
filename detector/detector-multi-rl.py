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
	try:
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
			
		def slice(infile, outfilename, start_ms, end_ms): #Slice a wav file
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

		print ('\nDetectando... L')			
		lista_l = deteccoes(arquivo_audio_l) #List with left detections
		print 'Deteccoes L:',len(lista_l)
		
		print ('Criando lista de slices... L')
		lista_l_slice = list_of_slices(lista_l)
		print 'Slices L: ',len(lista_l_slice)
		
		print ('\nDetectando... R')			
		lista_r = deteccoes(arquivo_audio_r) #List with right detections
		print 'Deteccoes R:',len(lista_r)
		
		print ('Criando lista de slices... R')
		lista_r_slice = list_of_slices(lista_r)
		print 'Slices R: ',len(lista_r_slice)	

		if eh_mono(arquivo_audio_l) and eh_mono(arquivo_audio_r): #Verify if both files are mono
			pass
		else:
			return False

		creat_folder(file_name) #Creat a folder for slices	
		

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
				print (arquivos_left[i]+' <=> '+arquivos_right[j])
				detecta(arquivos_left[i],arquivos_right[j],arquivos_left[i][:-6]+'.wav') #Call detection function
		break		




'''
resultados = [detecta(x) for x in arquivos] #Detect by List compreetions
print ''
print 'Arquivos das Deteccoes'
print 'Numero de arquivos: ',len(arquivos)
print ''
print 'Bem sucedidos: ',resultados.count(True)
print 'Mal sucedidos: ',resultados.count(False)
'''
