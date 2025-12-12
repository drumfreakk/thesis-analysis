#!/usr/bin/python

import sys
sys.path.insert(1, '../')
import standard
import standard.tex_friendly

import os

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

import pickle

from aux_functions import *

def combine_pictures(name, path, pictures, save, show):
	sizes = []
	density = 0
	for pic in pictures:
		drops = get_droplets(path, pic, False, True)
		sizes += drops["round_sizes"]
		density += drops["density"]

	d = {"sizes": sizes, "density": density/len(pictures)}
	with open("saves/" + name + ".dump", "wb") as f:
		pickle.dump(d, f)

	print("Mean density:", round(density / len(pictures), 2), "droplets/mm^2 (ignoring focal plane depth)")

	plt.hist(sizes, bins='doane', density=True, label="n = " + str(len(sizes)))
	
	plt.axvline(np.mean(sizes), color='r',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")
	
	create_plot(sizes, name, save, show)



def combine_runs(title, pics, save, show):
	print(pics)
	sizes = []
	densities = []
	for i in pics:
		with open(i, "rb") as f:
			data = pickle.load(f)
			sizes.append(data['sizes'])
			densities.append(data['density'])
	plt.hist(sizes, bins='doane', density=True, label="n = " + str(len(sizes)))
	
	#plt.axvline(np.mean(sizes), color='r',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")

	create_plot(sizes, title, save, show)


### Set the picture parameters

save = True
show = True

if sys.argv[1] == "all":
	# ./main.py all dir
	# Analyze each image individually in dir

	path = sys.argv[2]
	for file in os.listdir(path):
		get_droplets(path, file, save, show)


elif sys.argv[1] == "combine":
	# ./main.py combine <prefix> <title>
	# Analyze each picture starting with prefix in the current dir.
	# Combine the measurements as title

	print("Combining images")
	files = []
	for file in os.listdir():
		if file.startswith(sys.argv[2]):
			files.append(file)
	combine_pictures(sys.argv[3], '.', files, save, show)


elif sys.argv[1] == "custom":
	# ./main.py custom <title> <pictures>
	# Combine all pictures given by pictures (can be a wildcard) under title

	print("Custom")
	title = sys.argv[2]
	pics = sys.argv[3:]
	combine_pictures(title, '.', pics, save, show)


elif sys.argv[1] == "multi":
	# ./main.py multi <title> <saves>
	# Combine multiple saved runs (from custom) under title

	print("Combining multiple runs")
	title = sys.argv[2]
	pics = sys.argv[3:]
	combine_runs(title, pics, save, show)


else:
	# ./main.py <pic>
	# Analyze pic

	get_droplets(sys.argv[1], save, show)
	

