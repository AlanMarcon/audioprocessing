#!/usr/bin/python
# -*- coding: utf-8 -*-

#Detect tools
import numpy as np
import scipy.io.wavfile as wavfile
import modal
import modal.onsetdetection as od

#slice audio wave and directory
import sys
import time
from os import system
import wave
import os
import glob


#############################################################
def detecta(arquivo_audio):
	print arquivo_audio	
	system("clear")
	
	file_name = arquivo_audio
	sampling_rate, audio = wavfile.read(file_name)
	audio = np.asarray(audio, dtype=np.double)
	audio /= np.max(audio)
	
	frame_size = 480
	hop_size = 170
	
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
		
	print "sampling_rate: ", sampling_rate
	print "Audio file:", file_name
	print "Total length:", float(len(audio)) / sampling_rate, "seconds"
	
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
	
	print "Deteccoes", len(onsets)
	print "Running time:", run_time, "seconds"
	print "tempo", run_time / i

	if not os.path.exists(file_name+"-out"):
		os.makedirs(file_name+"-out")
		
	#Divide o audio em partes
	def slice(infile, outfilename, start_ms, end_ms):
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
	
	def frToSeg(fr): #Converte frames para segundos
		sec = float(fr)/48000
		minu = sec//60
		sec = sec-minu*60
		return int(minu *10000 + sec * 100)
		
	def escDur(tempo):
		tempo = str(tempo)[0:-2]
		sec = tempo[-2:]	
		if len(tempo) > 2:
			return tempo[0:-2]+'min '+sec+'seg'
		elif sec == '':
			return '0seg'
		else:
			return sec+'seg'	
	
	#Variaveis para o corte
	fn = file_name[:len(file_name)-4]+".wav" #nome do arquivo trabalhado
	sec = 48000*10  # segundos
	ini = lista[0]# inicio do corte
	end = 0 # fim do corte
	cont = 0 # numero do corte
	i = 0 # index
	j =0 # index
	
	while i <= len(lista):
		while j < len(lista): #percorre a lista
			end = lista[j]+sec #estipula o proximo valor de fim
			if end > lista[-1]: #verifica a deteccao e a ultima
				end = lista[-1]
				cont +=1
				break			
			if lista[j]+sec > lista[j+1]: #vai para a proxima deteccao					
				j +=1
			else:
				j +=1			
				cont +=1						
				break
		print ""
		print "--------------------------------------------"
		print "Corte n: ",cont
		print "Inicio do corte: ",escDur(str(frToSeg(ini)))
		print "Fim do corte: ",escDur(str(frToSeg(end)))
		print "Entre a detec. ",i ," e a detec. ",j 
		
		if end != 0: #verifica se encontrou pelo menos uma deteccao
			if ini >= 0:
				out_file = fn[:len(fn)-4] +"-S"+str(frToSeg(ini)).zfill(6)+"E"+str(frToSeg(end)).zfill(6)+"-slice"+str(cont) +fn[len(fn)-4:]
				print out_file
				slice(wave.open(fn,"r"), out_file , ini, end) #funcao de corte			
		
		print "Arquivo: ",out_file
		print 'Duração: '+escDur(str(frToSeg(end-ini)))
		if end == 0 or end == lista[-1]: #se for o ultimo para o laco encerrando os cortes
			break
		else: 
			ini =lista[j] -sec #define o novo inicio ja com o background
			i = j

arq = sys.argv[1]
print arq
detecta(arq)		
