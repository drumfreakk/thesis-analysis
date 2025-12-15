#!/usr/bin/python

import sys
import os

from scripts.analyze import *

### Set the picture parameters

save = True
show = True

if sys.argv[1] == "all":
	# ./main.py all dir
	# Analyze each image individually in dir

	path = sys.argv[2]
	for file in os.listdir(path):
		get_droplets(path, file, save, show)


elif sys.argv[1] == "combine_pictures":
	# ./main.py combine_pictures <sample> <pictures>
	# Combine all pictures given by pictures (can be a wildcard)

	print("Custom")
	title = sys.argv[2]
	pics = sys.argv[3:]
	combine_pictures(title, '.', pics, False, show)


elif sys.argv[1] == "combine_samples":
	# ./main.py multi <conditions> <sample_saves>
	# Combine multiple saved runs under "conditions"

	print("Combining multiple runs")
	title = sys.argv[2]
	pics = sys.argv[3:]
	combine_runs(title, pics, save, show)


else:
	# ./main.py <pic>
	# Analyze pic

	get_droplets(sys.argv[1], save, show)
	

