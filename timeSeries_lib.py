#################
#### IMPORTS ####
#################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#################
#### FUNCTIONS ####
#################

def genTimeSeries(trialNum, ds):
	
	# keep startTime at 0 because we need to refer to specific frames that we can only access if time starts at 0
	startTime = 0
	endTime = ds.trial_ts[2 * trialNum + 1] # retrieve endTime from array such as [trial1start, trial1end, trial2start, trial2end, etc]
	endTime = np.around(endTime*ds.framerate)/ds.framerate # round endTime to sample at framerate

	# make new timeSeries vector at resolution of eye-tracker (120 hz)
	timeSeriesTime = np.arange(startTime, endTime+1/ds.framerate, 1/ds.framerate)
	timeMaxTS = np.amax(timeSeriesTime)
	timeSeriesTime = pd.Series(timeSeriesTime)

	# get the frame #'s in which the keys were pressed and released
	indicesAon, indicesAoff = getPressIndices(trialNum, ds.A_trial, ds.framerate)
	indicesBon, indicesBoff = getPressIndices(trialNum, ds.B_trial, ds.framerate)

	# create new column for key press A and add 1's to the frames when key A is pressed
	timeSeriesA = pd.Series(np.zeros(timeSeriesTime.size))
	for ind in range(indicesAon.size):
		timeSeriesA[indicesAon[ind]:indicesAoff[ind]] = 1

	# create new column for key press B and add 1's to the frames when key B is pressed
	timeSeriesB = pd.Series(np.zeros(timeSeriesTime.size))
	for ind in range(indicesBon.size):
		timeSeriesB[indicesBon[ind]:indicesBoff[ind]] = 1

	# check work by plotting
	plt.subplot(1, 3, 1)
	plt.plot(timeSeriesTime, timeSeriesA, 'r-', linewidth = 2)
	plt.axis([0, 20000, 0, 1.5])

	plt.subplot(1, 3, 2)
	plt.plot(timeSeriesTime, timeSeriesB, 'b-', linewidth = 3)
	plt.axis([0, 20000, 0, 1.5])

	plt.subplot(1, 3, 3)
	plt.plot(timeSeriesTime, timeSeriesA, 'r-', linewidth = 2)
	plt.plot(timeSeriesTime, timeSeriesB, 'b-', linewidth = 3)
	plt.axis([0, 20000, 0, 1.5])
	plt.show()
	plt.close()

def getPressIndices(trialNum, pressData, framerate):
	# make two vectors consisting of times (sec) of (1) press on and (2) press off
	pressON = []
	pressOFF = []

	for val in pressData[trialNum]:
	    pressON.append(val[0])
	    pressOFF.append(val[1])
	    
	pressON =  pd.Series(pressON)
	pressOFF =  pd.Series(pressOFF)

	# find the frame #'s when press on and off
	pressON_ind = np.around(pressON/(1/framerate))
	pressON_ind = pd.Series(pressON_ind, dtype = int)
	pressOFF_ind = np.around(pressOFF/(1/framerate))
	pressOFF_ind = pd.Series(pressOFF_ind, dtype = int)

	return pressON_ind, pressOFF_ind