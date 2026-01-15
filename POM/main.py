#!/usr/bin/python

import sys

from scripts.analyse import *

def show_help():
	lines = []
	with open(sys.argv[0], "r") as fd:
		lines = [line.rstrip().lstrip() for line in fd]
	printing = False
	for l in lines:
		if len(l) > 0:
			if l[0] == "#":
				if l.startswith("# _script_"):
					printing = True
					toprint = "\n" + l[2:].replace("_script_", sys.argv[0])
				else:
					toprint = "\t" + l[2:]
				if printing:
					print(toprint)

### Set the picture parameters

save = True
show = True

if len(sys.argv) < 2:
	show_help()
	exit()

match sys.argv[1]:
	case "time":
		# _script_ time <rate> <T0> <T1>
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
		# _script_ combine_pictures <sample> <pictures>
		# Combine all pictures given by pictures (can be a wildcard)
	
		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Combine pictures:", title)
		combine_pictures(title, pics, True, show)
	
	
	case "combine_samples":
		# _script_ combine_samples <conditions> <sample_saves>
		# Combine multiple saved runs under "conditions"
	
		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Combining multiple runs:", title)
		combine_samples(title, pics, save, show)

	case "compare_samples":
		# _script_ compare_samples <saves>
		# Compare samples from "combine_samples", check if their from the same distribution

		compare_samples(sys.argv[2:])

	case "video":
		# _script_ video <sample> <pictures>
		# Combine all pictures given by <pictures> (can be a wildcard),
		# and prompt to input the number of shape-changing droplets

		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Analysing video:", title)
		video(title, pics, True, show)

	case "shapechange":
		# _script_ shapechange <title> <samples>
		# Combine multiple samples of the same conditions into one dataset, samples from video

		title = sys.argv[2]
		pics = sys.argv[3:]
		print("Combining videos:", title)
		combine_vids(title, pics, True, show)

	case "stats_vids":
		# _script_ stats_vids <title> <saves>
		# Combine different percentage saves from shapechange into one plot
		
		title = sys.argv[2]
		saves = sys.argv[3:]
		print("Stats on videos:", title)
		stats_vids(title, saves, True, show)

	case "critical_sizes":
		# _script_ critical_sizes <title> <shapechange save> <combine_samples save>
		# Determine the smallest droplet sizes that don't fall in to the smallest n % of droplets,
		# where n is the amount of shapechanging droplets

		critical_sizes(sys.argv[2], sys.argv[3], sys.argv[4])


	case "single":
		# _script_ single <title> <filename>
		# Analyze an individual picture
		
		get_droplets(sys.argv[2], sys.argv[3], save, show)

	case "video_size_distr":
		# _script_ video_size_distr <sample name> <video>
		# Extract the droplet size distribution over time from a video.

		video_size_distr(sys.argv[2], sys.argv[3], save, show)

	case "video_sizes":
		# _script_ video_sizes <sample> <saves>
		# Average multiple video size distributions from "video_size_distr"

		combine_video_sizes(sys.argv[2], sys.argv[3:], save, show)

	case "time_stats":
		# _script_ time_stats <savefile>
		# Test if distributions are similar from videos from video_sizes

		time_stats(sys.argv[2])

	case "dif_stats":
		# _script_ dif_stats <file1> <file2>
		# Quickly compare 2 distributions, compare t=0 from the 2 files 
		# Files are from video_sizes
	
		dif_stats(sys.argv[2], sys.argv[3])

	case "surface_tension":
		# _script surface_tension <xlsx>
		# Calculate the effective surface tension per % and per temperature
		# Based on measured fiber radii and literature values of K11 and Omega

		surface_tension(sys.argv[2])

	case _:
		# _script_ help
		# Show this help
		
		show_help()


