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
		# Convert a temperature change rate and two temperatures
		# into a time in the video (16x)
		
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
	
		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Combine pictures:", title)
		combine_pictures(title, '.', pics, False, show)
	
	
	case "combine_samples":
		# ./main.py combine_samples <conditions> <sample_saves>
		# Combine multiple saved runs under "conditions"
	
		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Combining multiple runs:", title)
		combine_runs(title, pics, save, show)
	
	case "video":
		# ./main.py video <sample> <pictures>
		# Combine all pictures given by <pictures> (can be a wildcard),
		# and prompt to input the number of shape-changing droplets

		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Analysing video:", title)
		video(title, pics, True, show)

	case "shapechange":
		# ./main.py shapechange <title> <samples>
		# Combine multiple samples of the same conditions into one dataset, samples from video

		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Combining videos:", title)
		combine_vids(title, pics, True, show)

	case "stats_vids":
		# ./main.py stats_vids <title> <saves>
		# Combine different percentage saves from shapechange into one plot
		
		title = sys.argv[2]
		saves = sys.argv[3:]
		print("Stats on videos:", title)
		stats_vids(title, saves, True, show)

	case "single":
		# ./main.py single <pic>
		# Analyze an individual picture
	
		get_droplets(sys.argv[2], sys.argv[3], save, show)
		
	case "help":
		# ./main.py help
		# Show this help
		
		lines = []
		with open(sys.argv[0], "r") as fd:
			lines = [line.rstrip().lstrip() for line in fd]
		printing = False
		for l in lines:
			command = False
			if len(l) > 0:
				if l[0] == "#":
					if l.startswith("# ./main.py"):
						printing = True
						command = True
						print()
					if printing:
						if not command:
							print(end="\t")
						print(l[2:])



