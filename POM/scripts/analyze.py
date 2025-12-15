
import sys
sys.path.insert(1, '../')
import standard as std

import os

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops 

import pickle

from scripts.aux_functions import *

def get_droplets(path, name, save=False, show=True):
	print("Processing", name)
	
	if name.split('.')[-1] not in ['tif', 'png']:
		print("\tNot an image, quitting")
		return {"round": [], "elongated": [], "round_sizes": [], "density": np.nan}
		return

	# Assume the pixel spacing is isotropic
	# The spacing is in um/px
	match get_magnification(name):
		case '5x':
			spacing = 1/2.03
			length_scalebar_um = 50
		case '10x':
			spacing = 1/4.09
			length_scalebar_um = 50
		case '20x':
			spacing = 1/8.17
			length_scalebar_um = 50
		case '40x':
			spacing = 1/16.56
			length_scalebar_um = 20
		case _:
			spacing = 1
			length_scalebar_um = 0
			print("WARNING: No magnification found, guessing pixel size")
		
	### Load and threshold the picture
	
	img_original = ski.io.imread(os.path.join(path, name))
	img_gray = ski.color.rgb2gray(ski.util.img_as_int(img_original))
	
	threshold = ski.filters.threshold_yen(img_gray)
	img_thresh = img_gray >= threshold
	
	
	
	### Identify the droplets
	
	# Label elements on the picture
	black = ski.util.dtype_limits(img_thresh)[0]
	label_image = label(img_thresh, background=black)
	
	fig, axs = plt.subplots(ncols=1, nrows=2, figsize=(12, 12), height_ratios=[3,1])
	axs[0].imshow(img_original)
	
	length_scalebar = length_scalebar_um/spacing
	scalebar = mpatches.Rectangle((50, img_thresh.shape[0] - 100),\
								  length_scalebar, 50, color='white')
	axs[0].add_patch(scalebar)
	axs[0].text(50, img_thresh.shape[0] - 120,\
				"\\boldmath$" + str(length_scalebar_um) + " \\mathrm{\\mu m}$",\
				color='white', size='large')
	
	
	round_droplets = []
	elongated_droplets = []
	
	# Analyze each droplet
	for region in regionprops(label_image, intensity_image=img_gray, spacing=(spacing,spacing)):
		# Skip regions smaller than 50 square pixels
		if region.area < 50 * spacing**2:
			continue
		
		# Skip regions smaller than 2 um^2
		if region.area < 2:
			continue
	
		# Skip regions close to the edge of the image
		if region.bbox[0] < 10 or\
		   region.bbox[1] < 10 or\
		   region.bbox[2] > img_thresh.shape[0] - 10 or\
		   region.bbox[3] > img_thresh.shape[1] - 10:
		   continue
	
		if region.eccentricity > 0.7:
			elongated_droplets.append(region)
	#		print(round(region.area_filled,2), '\t', round(region.intensity_mean,2))
		else:
			round_droplets.append(region)
	#		print('\t', round(region.equivalent_diameter_area,3))
	
	
	### Display the droplet outlines
	
	for region in round_droplets:
		minr, minc, maxr, maxc = region.bbox
		color = 'red'
		
		circ = mpatches.Circle((region.centroid[1]/spacing, region.centroid[0]/spacing),\
								radius=region.equivalent_diameter_area/(2*spacing),\
								fill=False, edgecolor=color, linewidth=1)
		axs[0].add_patch(circ)
	
	#	axs[0].text(minc, minr-2, round(region.area_filled,2), color=color)
	
	for region in elongated_droplets:
		minr, minc, maxr, maxc = region.bbox
	
		color = 'green'
		rect = mpatches.Rectangle((minc-1, minr-1), maxc - minc, maxr - minr,
									  fill=False, edgecolor=color, linewidth=1)
		axs[0].add_patch(rect)
		
	#	axs[0].text(minc, minr-2, round(region.area_filled,2), color=color)
	
	density = (len(elongated_droplets) + len(round_droplets))* 10**6 / \
		  	  (img_gray.shape[0]*img_gray.shape[1]*spacing**2)

	print("Average droplet density:", density, "droplets / mm^2 (ignoring focal plane depth)\n")

	sizes = []
	for drop in round_droplets:
		sizes.append(drop.equivalent_diameter_area)
	
	
	### Show the picture
	
	prefix = name.split('.')[0]
	
	axs[0].set_axis_off()
	
	axs[1].hist(sizes, bins='doane', density=True, label="n = " + str(len(sizes)))
	axs[1].axvline(np.mean(sizes), color='r',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")
	
	create_hist(axs[1], prefix, save, show, True)

	return {"round": round_droplets, "elongated": elongated_droplets,\
			"round_sizes": sizes, "density": density}


def combine_pictures(name, path, pictures, save, show):
	sizes = []
	density = 0
	for pic in pictures:
		drops = get_droplets(path, pic, False, False)
		sizes += drops["round_sizes"]
		density += drops["density"]

	d = {"sizes": sizes, "density": density/len(pictures)}
	with open("saves/" + name + ".bin", "wb") as f:
		pickle.dump(d, f)

	print("Mean density:", round(density / len(pictures), 2), "droplets/mm^2 (ignoring focal plane depth)")

	fig, ax = plt.subplots()
	ax.hist(sizes, bins='doane', density=True, label="n = " + str(len(sizes)))
	
	ax.axvline(np.mean(sizes), color='r',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")
	
	create_hist(ax, name, save, show)

def combine_runs(title, pics, save, show):
	sizes = []
	densities = []
	for i in pics:
		with open(i, "rb") as f:
			data = pickle.load(f)
			sizes.append(data['sizes'])
			densities.append(data['density'])
	
	all_sizes = []
	for i in range(len(sizes)):
		all_sizes += sizes[i]

	_,binedges = np.histogram(all_sizes,bins='doane')
	bincenters = 0.5*(binedges[1:]+binedges[:-1])

	# [ [bin_0 #1, #2, #3], [bin_1 #1, #2, #3], ...]
	# more strictly frequency per bin
	mean_per_bin = [[0 for j in sizes] for i in bincenters]

	for i in range(len(sizes)):
		d = np.digitize(sizes[i], binedges)
		for j in range(len(d)):
			if d[j]-1 == len(mean_per_bin):
				d[j] = d[j]-1
			mean_per_bin[d[j]-1][i] += sizes[i][j]
		for k in range(len(mean_per_bin)):
			mean_per_bin[k][i] = mean_per_bin[k][i]/len(d)

	means = np.asarray([np.mean(i) for i in mean_per_bin])
	s = sum(means)
	means = means/s

	stds  = np.asarray([np.std(i) for i in mean_per_bin])/s

	fig, ax = plt.subplots()

	width = (max(all_sizes)-min(all_sizes))/len(bincenters)
	ax.bar(bincenters, means, width=width, yerr=stds,\
		   label="n = " + str(len(sizes)) + "\n" + str(len(all_sizes)) + " droplets")
	ax.set_ylim(bottom=0)
	
	ax.axvline(np.mean(all_sizes), color='r',  linestyle='dashed', label="Mean = $" + str(round(np.mean(all_sizes))) + " \\mathrm{\\mu m}$")

	create_hist(ax, title, save, show, True)


