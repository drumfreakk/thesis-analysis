#!/usr/bin/python

import sys
sys.path.insert(1, '../../')
import standard

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
		drops = get_droplets(path, pic, False, False)
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
	path = sys.argv[2]
	for file in os.listdir(path):
		get_droplets(path, file, save, show)
elif sys.argv[1] == "combine":
	print("Combining images")
	files = []
	for file in os.listdir():
		if file.startswith(sys.argv[2]):
			files.append(file)
	combine_pictures(sys.argv[3], '.', files, save, show)
elif sys.argv[1] == "custom":
	print("Custom")
	title = sys.argv[2]
	pics = sys.argv[3:]
	combine_pictures(title, '.', pics, save, show)
elif sys.argv[1] == "dumps":
	print("Combining multiple runs")
	title = sys.argv[2]
	pics = sys.argv[3:]
	combine_runs(title, pics, save, show)
else:
	get_droplets(sys.argv[1], save, show)
	
		


#prefix = '20251201-7-40x' # Uncrossed, hard
#prefix = '20251201-3-20x' # Easy
#prefix = '20251126-3-1-10x' # Shape change
#prefix = '20251205-5-20x' # Small shape change, uncrossed
#prefix = '20251126-1-1-5x' # Many drops. To be clear, 5x is a guess


