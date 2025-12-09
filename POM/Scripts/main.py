#!/usr/bin/python

import numpy as np

import os

import matplotlib  as mpl 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops

import aux_functions

### Set the picture parameters

datapath = '.'
#prefix = '20251201-7-40x' # Uncrossed, hard
prefix = '20251201-3-20x' # Easy
#prefix = '20251126-3-1-10x' # Shape change
#prefix = '20251205-5-20x' # Small shape change, uncrossed


# Assume the pixel spacing is isotropic
# The spacing is in um/px
match prefix.split('-')[-1]:
	case '5x':
		spacing = 1/2.03
	case '10x':
		spacing = 1/4.09
	case '20x':
		spacing = 1/8.17
	case '40x':
		spacing = 1/16.56
	case _:
		spacing = 1
		print("No magnification found, guessing pixel size")
	


### Load and threshold the picture

img_original = ski.io.imread(os.path.join(datapath, prefix + '.tif'))
img_gray = ski.color.rgb2gray(ski.util.img_as_int(img_original))

print("Loaded image")

threshold = ski.filters.threshold_yen(img_gray)
img_thresh = img_gray >= threshold
print("Thresholded image")



### Identify the droplets

# Label elements on the picture
black = ski.util.dtype_limits(img_thresh)[0]
label_image = label(img_thresh, background=black)

fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(12, 12))
ax.imshow(img_original)

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

	print(round(region.area_filled,1), '\t', round(region.eccentricity,2))

	if region.eccentricity > 0.7:
		elongated_droplets.append(region)
	else:
		round_droplets.append(region)
		print('\t', round(region.equivalent_diameter_area,3))

elongated_droplets, new_round = aux_functions.merge_nearby_regions(elongated_droplets)
round_droplets += new_round

### Display the droplet outlines

for region in round_droplets:
	minr, minc, maxr, maxc = region.bbox
	color = 'red'
	
	circ = mpatches.Circle((region.centroid[1]/spacing, region.centroid[0]/spacing),\
							radius=region.equivalent_diameter_area/(2*spacing),\
							fill=False, edgecolor=color, linewidth=1)
	ax.add_patch(circ)

	ax.text(minc, minr-2, round(region.area_filled,2), color=color)

for region in elongated_droplets:
	minr, minc, maxr, maxc = region.bbox

	color = 'green'
	rect = mpatches.Rectangle((minc-1, minr-1), maxc - minc, maxr - minr,
								  fill=False, edgecolor=color, linewidth=1)
	ax.add_patch(rect)
	
	ax.text(minc, minr-2, round(region.area_filled,2), color=color)


### Show the picture

ax.set_axis_off()
plt.tight_layout()
plt.show()
