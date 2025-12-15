#!/usr/bin/python

import sys
import os

from scripts.analyse import *

### Set the picture parameters

save = True
show = True

match sys.argv[1]:
	case "time":
		# ./main.py time <rate> <T0> <T1>
		
		rate = float(sys.argv[2])	# deg C / min
		t0 = float(sys.argv[3])		# deg C
		t1 = float(sys.argv[4])		# deg C

		t = t1-t0			# deg C

		rate = rate / 60	# deg C / sec
		rate = rate * 16	# deg C / sec video

		t = t / rate
		
		print(round(t, 1), "sec video")
	
	
	case "combine_pictures":
		# ./main.py combine_pictures <sample> <pictures>
		# Combine all pictures given by pictures (can be a wildcard)
	
		print("Combine pictures")
		title = sys.argv[2]
		pics = sys.argv[3:]
		combine_pictures(title, '.', pics, False, show)
	
	
	case "combine_samples":
		# ./main.py combine_samples <conditions> <sample_saves>
		# Combine multiple saved runs under "conditions"
	
		print("Combining multiple runs")
		title = sys.argv[2]
		pics = sys.argv[3:]
		combine_runs(title, pics, save, show)
	
	case "video":
		# ./main.py video <sample> <pictures>
		# Combine all pictures given by <pictures> (can be a wildcard),
		# and prompt to input the number of shape-changing droplets

		print("Analysing video")
		title = sys.argv[2]
		pics = sys.argv[3:]
		video(title, pics, True, show)
	
	case _:
		# ./main.py <pic>
		# Analyze an individual picture
	
		get_droplets(sys.argv[1], save, show)
		
	
