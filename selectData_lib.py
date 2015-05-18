#################
#### IMPORTS ####
#################
from Tkinter import Tk 						# for open data file GUI
from tkFileDialog import askopenfilenames 	# for open data file GUI
import os, sys
import numpy as np
import scipy.stats

#################
#### FUNCTIONS ####
#################

#################
#### Select data file ####
#################

## NB - won't work on Mac!!

def select_data():
	Tk().withdraw() 												# we don't want a full GUI, so keep the root window from appearing
	datafile = askopenfilenames(title='Choose file', 				# show an "Open" dialog box and return the path to the selected file
		initialdir = '..')[0] 
	return datafile


#################
#### Add to structure ####
#################

class DataStruct():
    def __init__(self, datafile, A_code = 1, B_code = 4, trial_code = 8, epsilon = 0.0123, plotrange = [-1.1,1.1], 
        winwidth_pix = 1280, winwidth_cm = 35.6, fixdist = 60.0, dataframerate = 120.0):
        
        self.filenamefp     = datafile      # full path of data file
        self.filename       = ''            # data filename 
        self.eyetrackerdata = False         # True if et data, False if just input
        self.numtrials      = 0             # number of trials in data file

        # eyetracker data
        self.timestamps     = []            # eyetracker time stamps
        self.leftgazeX      = []            # 
        self.leftgazeY      = []            # 
        self.leftvalidity   = []            #
        self.leftpupil      = []            #
        self.rightgazeX     = []            # 
        self.rightgazeY     = []            # 
        self.rightvalidity  = []            #
        self.rightpupil     = []            #

        self.leftgazeXvelocity  = []        # to allocate velocity
        self.rightgazeXvelocity = []        # which will be computed
        self.leftgazeYvelocity  = []        # in self.read_data()
        self.rightgazeYvelocity = []        #

        self.dataloss   = []                # store data loss information
        self.snr        = []                # store snr
        self.cv         = []                # store coefficient of variation


        self.trial_ts   = []                # time stamps for trials

        # percept data
        self.A_trial    = []                # time stamps for A in trial
        self.B_trial    = []                # time stamps for B in trial
        self.A_ts       = []                # time stamps for A
        self.B_ts       = []                # time stamps for B

        # constants
        self.A_code     = A_code            # code value for A percept
        self.B_code     = B_code            # code value for B percept
        self.trial_code = trial_code        # code value for trials
        self.epsilon    = epsilon           # epsilon
        self.plotrange  = plotrange         # plotrange 

        self.winwidth_pix = winwidth_pix    #
        self.winwidth_cm  = winwidth_cm     #
        self.fixdist      = fixdist         #
        self.framerate    = dataframerate   #
      

        self.read_data()                    # read data

        self.expname = ''
        self.subjectname = ''

    def read_data(self):
        # read data. try/except for reading different formats -------------------------------------------------------------------------------------------------
        self.filename = os.path.split(self.filenamefp)[1]                                           # get just data file name, not full path
        try:
            data = np.genfromtxt(self.filenamefp, delimiter="\t",                                   # read data file, dtype allows mixed types of data,
            dtype=None, names=True, usecols = range(38))                                            # names reads first row as header, usecols will read just 38 columns
            print '{0}: eyetracker data (38 colums format)'.format(os.path.split(self.filename)[1])
        except ValueError:                                                                          
            try:                                                                                    # if file does not have 38 columns, try 
                data = np.genfromtxt(self.filenamefp, delimiter="\t", 
                    dtype=None, names=True, usecols = range(34))                                    # 34 colums (legacy file)
                print '{0}: eyetracker data (34 colums format). This does not have parameters'.format(os.path.split(self.filename)[1])
            except ValueError:
                try:
                    data = np.genfromtxt(self.filenamefp, delimiter="\t",                           # if that stil does not work
                    dtype=None, names=True, usecols = range(6))                                     # try with 6 colums (only button presses file, no parameters)
                    print '{0}: button press data'.format(os.path.split(self.filename)[1])
                except ValueError:                                                                  # if neither of these work, 
                    print 'cannot read data file {0}'.format(os.path.split(self.filenamefp)[1])     # cannot read data file
                    sys.exit()

        # Determine if datafile contains eyetracker data or just input (mouse) ----------------------------------------
        et_data = True if 'LeftGazePoint2Dx' in data.dtype.names else False                         # if LeftGazePoint2Dx in header, et_data is True, else is False

        
        # Read events data --------------------------------------------------------------------------------------------
        if et_data:
            try:
                ets       = data['EventTimeStamp'][data['EventTimeStamp']!='-'].astype(np.float)    # event time stamp: filter out values with '-' and convert str to float
                ecode     = data['Code'][data['Code'] != '-'].astype(np.float)                      # event code: filter out values with '-' and convert to float
            except ValueError:
                print data.dtype.names
        else:
            try:
                if '-' in data['EventTimeStamp']:
                    ets       = data['EventTimeStamp'][data['EventTimeStamp']!='-'].astype(np.float)# event time stamp
                    ecode     = data['Code'][data['Code'] != '-'].astype(np.float)                 # event code
                else:
                    ets       = data['EventTimeStamp']                                             # event time stamp
                    ecode     = data['Code']                                                       # event code
            except ValueError:
                print 'except'
                ets       = data['Timestamp']                                                       # event time stamp
                ecode     = data['EventCode']                                                       # event code
        # print data['Code']

        Trial_on  = ets[ecode ==  self.trial_code]                                                  # get timestamp of trials start
        Trial_off = ets[ecode == -self.trial_code]                                                  # get timestamp of trials end

        A_on      = ets[ecode ==  self.A_code]                                                      # get timestamp of percept A on (LEFT press)
        A_off     = ets[ecode == -self.A_code]                                                      # get timestamp of percept A off (LEFT release)

        B_on      = ets[ecode ==  self.B_code]                                                      # get timestamp of percept B on (RIGHT press)
        B_off     = ets[ecode == -self.B_code]                                                      # get timestamp of percept B off (RIGHT release)

        self.numtrials = len(Trial_on)                                                              # compute number of trials

        # datastruct
        self.trial_ts = np.empty((Trial_on.size + Trial_off.size,), dtype=Trial_on.dtype)           # create empty matrix of specific lenght
        self.trial_ts[0::2] = Trial_on                                                              # put Trial_on on even spaces 
        self.trial_ts[1::2] = Trial_off                                                             # put Trial_off on odd spaces

        # Check input events --------------------------------------------------------------------------------------------

        # Get input in each trial
        x, y, z = 2, 0, self.numtrials                                                              # size of percept matrix
        self.A_trial = [[[0 for k in xrange(x)] for j in xrange(y)] for i in xrange(z)]             # matrix for A percept of each trial
        self.B_trial = [[[0 for k in xrange(x)] for j in xrange(y)] for i in xrange(z)]             # matrix for B percept of each trial

        for trial in range(self.numtrials):                                                         # for each trial
            start = self.trial_ts[2 * trial]                                                        # timestamp start of trial
            end   = self.trial_ts[2 * trial + 1]                                                    # timestamp end of trial

            A_on_in_trial = [i for i in A_on if start<i<end]                                        # get A_on in trial

            for ts_on in A_on_in_trial:                                                             # for each A_on
                val, idx_start = find_nearest_above(A_off, ts_on)                                   # look for the nearest above A_off
                
                if val is not None:                                                                 # compare nearest above to end of trial,
                    ts_off = np.minimum(end,val)                                                    # get minimum                                               
                else:
                    ts_off = end

                self.A_trial[trial].append([ts_on, ts_off])                                         # add A_on and A_off times to percept matrix

            B_on_in_trial = [i for i in B_on if start<i<end]                                        # get A_on in trial

            for ts_on in B_on_in_trial:                                                             # for each B_on
                val, idx_start = find_nearest_above(B_off, ts_on)                                   # look for the nearest above B_off
                
                if val is not None:                                                                 # compare nearest above to end of trial,
                    ts_off = np.minimum(end,val)                                                    # get minimum
                else:
                    ts_off = end

                self.B_trial[trial].append([ts_on, ts_off])                                         # add B_on and B_off times to percept matrix

            for item in self.A_trial[trial]:                                                        # datastruct.A/B_ts will contain on and off
                self.A_ts.append(item)                                                              # time staps in the following way:
            for item in self.B_trial[trial]:                                                        # [[on_1, off_2], [on_2, off_2] ...]
                self.B_ts.append(item)                                                              # 

        # Read eyetracker data ---------------------------------------------------------------------------------------
        if et_data:
            self.eyetrackerdata = True                                                              # indicate that datastruct contains eyetracker data

            self.timestamps     = np.array(map(float, data['Timestamp']))                           # get time stamps of the eye tracker data

            self.leftgazeX      = np.array(map(float, data['LeftGazePoint2Dx']))                    # get left gaze X data
            self.leftgazeY      = np.array(map(float, data['LeftGazePoint2Dy']))                    # get left gaze Y data
            self.leftvalidity   = np.array(map(float, data['LeftValidity']))                        # get left gaze validity
            self.leftpupil      = np.array(map(float, data['LeftPupil']))                           # get left pupil size
            
            self.rightgazeX     = np.array(map(float, data['RightGazePoint2Dx']))                   # get right gaze X data
            self.rightgazeY     = np.array(map(float, data['RightGazePoint2Dy']))                   # get right gaze Y data
            self.rightvalidity  = np.array(map(float, data['RightValidity']))                       # get right gaze validity
            self.rightpupil     = np.array(map(float, data['RightPupil']))                          # get right pupil size

            self.vergence       = np.array(map(float, data['Vergence']))                            # get vergence
            self.fixationdist   = np.array(map(float, data['FixationDist']))                        # get fixation distance

            # Tobii gives data from 0 to 1, we want it from -1 to 1:
            self.leftgazeX      = 2 * self.leftgazeX    - 1
            self.leftgazeY      = 2 * self.leftgazeY    - 1
            self.rightgazeX     = 2 * self.rightgazeX - 1
            self.rightgazeY     = 2 * self.rightgazeY - 1

            # Map values outside of range to the boundaries
            self.leftgazeX[self.plotrange[0]  > self.leftgazeX]  = self.plotrange[0]; self.leftgazeX[self.plotrange[1] < self.leftgazeX] = self.plotrange[1]
            self.leftgazeY[self.plotrange[0]  > self.leftgazeY]  = self.plotrange[0]; self.leftgazeY[self.plotrange[1] < self.leftgazeY] = self.plotrange[1]
            self.rightgazeX[self.plotrange[0] > self.rightgazeX] = self.plotrange[0]; self.rightgazeX[self.plotrange[1] < self.rightgazeX] = self.plotrange[1]
            self.rightgazeY[self.plotrange[0] > self.rightgazeY] = self.plotrange[0]; self.rightgazeY[self.plotrange[1] < self.rightgazeY] = self.plotrange[1]

            # Compute velocity
            # 1 - convert gaze values from arbitrary units to pixels
            leftgazeX_pix  = self.leftgazeX  * self.winwidth_pix                                    #
            rightgazeX_pix = self.rightgazeX * self.winwidth_pix
            leftgazeY_pix  = self.leftgazeY  * self.winwidth_pix
            rightgazeY_pix = self.rightgazeY * self.winwidth_pix

            # 2 - convert gaze values from pixels to degrees
            V = 2 * np.arctan(self.winwidth_cm/2 * self.fixdist)                                    # in radians
            deg_per_pix = V / self.winwidth_pix                                                     # in degrees

            leftgazeX_deg  = leftgazeX_pix  * deg_per_pix                                           #
            rightgazeX_deg = rightgazeX_pix * deg_per_pix                                           #
            leftgazeY_deg  = leftgazeY_pix  * deg_per_pix                                           #
            rightgazeY_deg = rightgazeY_pix * deg_per_pix                                           #

            # 3 - compute velocity
            self.leftgazeXvelocity  = np.diff(leftgazeX_deg,  n=1) * self.framerate;                #
            self.rightgazeXvelocity = np.diff(rightgazeX_deg, n=1) * self.framerate;                #
            self.leftgazeYvelocity  = np.diff(leftgazeY_deg,  n=1) * self.framerate;                #
            self.rightgazeYvelocity = np.diff(rightgazeY_deg, n=1) * self.framerate;                #


            # For each trial, compute percentage of validity, 
            # Signal to Noise Ratio (SNR) and coefficient of variation (CV)

            self.dataloss   = []                                                                    # to store data loss percentage
            self.snr        = [['LeftGazeX','RightGazeX','LeftGazeY','RightGazeY']]                 # to store SNR
            self.cv         = [['LeftGazeX','RightGazeX','LeftGazeY','RightGazeY']]                 # to store CV

            for trial in range(self.numtrials):                                                     # for each trial
                start = self.trial_ts[2 * trial]                                                    # timestamp start of trial
                end   = self.trial_ts[2 * trial + 1]                                                # timestamp end of trial

                val, idx_start = find_nearest_above(self.timestamps, start)                         # get array index for start of trial
                val, idx_end   = find_nearest_above(self.timestamps, end)                           # get array index for end of trial
                if idx_end is None: idx_end = len(self.timestamps)-1                                # if end of trial was end of experiment

                nsamples = idx_end - idx_start                                                      # number of samples in trial

                lgx = self.leftgazeX[idx_start:idx_end]
                rgx = self.rightgazeX[idx_start:idx_end]
                lgy = self.leftgazeY[idx_start:idx_end]
                rgy = self.rightgazeY[idx_start:idx_end]
                lv  = self.leftvalidity[idx_start:idx_end]
                rv  = self.rightvalidity[idx_start:idx_end]

                # compute percentage of validity
                lv_trial = 100 * (self.leftvalidity[idx_start:idx_end] == 4).sum()/float(nsamples)  # left eye:  % of lost data
                rv_trial = 100 * (self.rightvalidity[idx_start:idx_end] == 4).sum()/float(nsamples) # right eye: % of lost data

                self.dataloss.append([lv_trial, rv_trial])                                          # store % of lost data

                # compute SNR
                lx_snr = scipy.stats.signaltonoise(lgx[lv != 4])
                rx_snr = scipy.stats.signaltonoise(rgx[rv != 4])
                ly_snr = scipy.stats.signaltonoise(lgy[lv != 4])
                ry_snr = scipy.stats.signaltonoise(rgy[rv != 4])
                self.snr.append([lx_snr, rx_snr, ly_snr, ry_snr])

                # compute variation
                lx_cv = scipy.stats.variation(lgx[lv != 4])
                rx_cv = scipy.stats.variation(rgx[rv != 4])
                ly_cv = scipy.stats.variation(lgy[lv != 4])
                ry_cv = scipy.stats.variation(rgy[rv != 4])
                self.snr.append([lx_cv, rx_cv, ly_cv, ry_cv])

                print 'Trial {0} - {1} % of data was lost. SNR: {2}. CV: {3}'.format(trial + 1,      # report data loss, snr and cv
                    "%.1f" % lv_trial, lx_snr, lx_cv)    


def find_nearest_above(array, value):
	# http://stackoverflow.com/questions/17118350/how-to-find-nearest-value-that-is-greater-in-numpy-array
    diff = array - value
    mask = np.ma.less_equal(diff, 0)
    # We need to mask the negative differences and zero
    # since we are looking for values above
    if np.all(mask):
        return None, None # returns None if target is greater than any value
    masked_diff = np.ma.masked_array(diff, mask)

    idx = masked_diff.argmin()
    val = array[idx]
    
    if val < value:     # if there's no value above
        val = -1        # use -1 for val
        idx = 0         # and 0 for idx

    return val, idx