#################
#### IMPORTS ####
#################
from selectData_lib import *

#################
#### MAIN ####
#################
def main():

	#################
	#### Set-up starting parameters ####
	#################

	path = select_data()
	print path

	#################
	#### Get Data ####
	#################

	ds = DataStruct(path) 											# create new DataStruct instance using path to datafile

	#data = ds.leftgazeXvelocity[ds.leftgazeXvelocity != -1]			# get relevant data
	
	#################
	#### Summarize data ####
	#################

		#################
		#### Generate press time series ####
		#################

		#################
		#### Summarize and visualize time series pre-clean-up ####
		#################

		#################
		#### Clean-up gaps and overlaps ####
		#################

		#################
		#### Summarize and visualize time series post-clean-up ####
		#################

		#################
		#### Derive new variables ####
		#################

if __name__ == '__main__':
	main()