
import sys
sys.path.insert(1, '../../')
import standard

import os

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops


def get_magnification(fname):
	return fname.split('.')[-2].split('-')[-1]

def tex_friendly(string):
	s = "\\#".join(string.split('#'))
	return "\\%".join(s.split('%'))

def create_plot(sizes, title, save, show):

	plt.legend()
	plt.ylabel("Frequency")
	plt.xlabel("Diameter ($\\mathrm{\\mu m}$)")
	
	plt.tight_layout()
	plt.title(tex_friendly(title))
	
	if save:
		plt.savefig("out/" + title + ".pdf", dpi=600)
	if show:
		plt.show()
	plt.close()

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

	print("Average droplet density:", density, "droplets / mm^2 (ignoring focal plane depth)")

	sizes = []
	for drop in round_droplets:
		sizes.append(drop.equivalent_diameter_area)
	
	
	### Show the picture
	
	
	axs[0].set_axis_off()
	
	axs[1].hist(sizes, bins='doane', density=True, label="n = " + str(len(sizes)))
	axs[1].set_ylabel("Frequency")
	axs[1].set_xlabel("Diameter ($\\mathrm{\\mu m}$)")
	
	
	axs[1].axvline(np.mean(sizes), color='r',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")

	plt.legend()
	plt.tight_layout()
	prefix = name.split('.')[0]
	plt.title(tex_friendly(prefix))
	if save:
		plt.savefig("out/" + prefix + ".pdf", dpi=600)
	if show:
		plt.show()
	plt.close()

	return {"round": round_droplets, "elongated": elongated_droplets,\
			"round_sizes": sizes, "density": density}
	
