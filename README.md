# Project - AnalyzeAlternations
Date started: April 2014
Date ended: ACTIVE

# Motivation

Analyze the responses of experimental subjects in a vision science
experiment.

# Synopsis

This project analyzes the timing of perceptual alternations in response to a 
bi-stable visual stimulus. Perceptual alternations may be recorded via mouse 
button presses (right/left or a/b) or via an eye tracking device (Tobii x120).

Currently, the function analyzeAlternations.py will (1) get data, and 
(2) generate a button press time series (list of mouse states as a function 
of time with a fixed dt).  

# To-do
(3) summarize and visualize the time series pre-clean-up, 
(4) clean-up overlaps (not yet gaps) in button presses, 
(5) summarize and visualize time series post-clean-up, 
(6) compare the button press and eye tracking time series data.

# Execution: 
python analyzeAlternations.py  


# Input: 
datafile.txt

# Output:
Currently no output; only a figure that plots the button press time series

# Supporting libraries

- **selectData_lib.py** -
	- Functions:
		- **select_data()** - This function imports the .txt raw data file.
		Called by **analyzeAlternations**
		- **find_nearest_above()** - Called by **DataStruct()**
	- Class:
		- **DataStruct()* - Called by **analyzeAlternations**

- **timeSeries_lib.py** -
	- Functions:
		- **genTimeSeries** - raw data is in the format of a column of 
		mouse press/release events and needs to be converted to an evenly 
		sampled time series format. Called by **analyzeAlternations**
		- **getPressIndices** - the time series vector needs to be labeled with the 
		corresponding button press events. Events are labeled for each frame with a 
		1 if the button was pressed or 0 if a button was not pressed (press A = 
		column 2; press B = column 3). This function finds the times when a button 
		was pressed (pressOn) and released (pressOff) and returns the index of the 
		nearest frame at 120Hz. Called by **genTimeSeries**.
