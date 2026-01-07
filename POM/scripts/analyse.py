
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

import pims

import pickle

from scripts.aux_functions import *

def get_droplets(path, name, save=False, show=True):
	print("Processing", name)
	
	if name.split('.')[-1] not in ['tif', 'png']:
		print("\tNot an image, quitting")
		return {"round": [], "elongated": [], "round_sizes": [], "density": np.nan}
		return

	### Load and threshold the picture
	
	img_original = ski.io.imread(os.path.join(path, name))
	
	return droplet_analysis(name.split('.')[0], img_original, get_magnification(name), save, show)

def droplet_analysis(name, img_original, magnification, save, show):
	# Assume the pixel spacing is isotropic
	# The spacing is in um/px
	spacing, length_scalebar_um = get_scales(magnification)

	img_gray = ski.color.rgb2gray(ski.util.img_as_int(img_original))
	
	threshold = ski.filters.threshold_yen(img_gray)
	img_thresh = img_gray >= threshold
	
	
	
	### Identify the droplets
	
	# Label elements on the picture
	black = ski.util.dtype_limits(img_thresh)[0]
	label_image = label(img_thresh, background=black)
	
	if save or show:
		fig, axs = plt.subplots(ncols=1, nrows=2, figsize=(12, 12), height_ratios=[3,1])
		axs[0].imshow(img_original)
		
		length_scalebar = length_scalebar_um/spacing
		scalebar = mpatches.Rectangle((50, img_thresh.shape[0] - 100),\
									  length_scalebar, 50, color='white')
		axs[0].add_patch(scalebar)
		axs[0].text(50, img_thresh.shape[0] - 120,\
					"\\boldmath$" + str(length_scalebar_um) + " \\mathrm{\\mu m}$",\
					color='white', size='large')
	
		axs[0].text(3000,3500, "Spherical droplets", color='m', size='large')
		axs[0].text(3000,3600, "Weirdly shaped or shape-changing droplets", color='g', size='large')
	
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

	if save or show:
		for region in round_droplets:
			minr, minc, maxr, maxc = region.bbox
			color = 'm'
			
			circ = mpatches.Circle((region.centroid[1]/spacing, region.centroid[0]/spacing),\
									radius=region.equivalent_diameter_area/(2*spacing),\
									fill=False, edgecolor=color, linewidth=1)
			axs[0].add_patch(circ)
		
		#	axs[0].text(minc, minr-2, round(region.area_filled,2), color=color)
		
		for region in elongated_droplets:
			minr, minc, maxr, maxc = region.bbox
		
			color = 'g'
			rect = mpatches.Rectangle((minc-1, minr-1), maxc - minc, maxr - minr,
										  fill=False, edgecolor=color, linewidth=1)
			axs[0].add_patch(rect)
			
		#	axs[0].text(minc, minr-2, round(region.area_filled,2), color=color)
	
	density = (len(elongated_droplets) + len(round_droplets))* 10**6 / \
		  	  (img_gray.shape[0]*img_gray.shape[1]*spacing**2)

	print("Average droplet density:", round(density,2), "droplets / mm^2 (ignoring focal plane depth)\n")

	sizes = []
	for drop in round_droplets:
		sizes.append(drop.equivalent_diameter_area)
	
	
	### Show the picture
	if save or show:	
		axs[0].set_axis_off()
		
		axs[1].hist(sizes, bins='doane', density=True, label="n = " + str(len(sizes)))
		axs[1].axvline(np.mean(sizes), color='m',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")
		
		create_hist(axs[1], name, save, show, True)

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
	
	ax.axvline(np.mean(sizes), color='m',  linestyle='dashed', label="Mean = $" + str(round(np.mean(sizes))) + " \\mathrm{\\mu m}$")
	
	create_hist(ax, name, save, show)

def combine_runs(title, pics, save, show):
	sizes = []
	densities = []
	for i in pics:
		with open(i, "rb") as f:
			data = pickle.load(f)
			sizes.append(data['sizes'])
			densities.append(data['density'])
	
	binedges,bincenters = bin_sizes(sizes)

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
	
	ax.axvline(np.mean(all_sizes), color='m',  linestyle='dashed', label="Mean = $" + str(round(np.mean(all_sizes))) + " \\mathrm{\\mu m}$")

	create_hist(ax, title, save, show, True)


def video(title, pics, save, show):
	sizes = []
	n = {"sizes": [], "shapechange": 0}
	s = {"sizes": [], "shapechange": 0}
	density = 0
	for pic in pics:
		drops = get_droplets('.', pic, False, True)
		sizes += drops["round_sizes"]
		density += drops["density"]

		a = True
		while a:
			i = input("Number of smectic, nematic shape-changing droplets: ").split(",")
			if len(i) != 2:
				print("bad split")
				continue
			try:
				s_c = int(i[0])
				n_c = int(i[1])
			except ValueError:
				print("bad conversion")
				continue
			a = False

		print(s_c, "smectic &", n_c, "nematic\n")

		if n_c != 0:
			n['sizes'] += drops['round_sizes']
			n['shapechange'] += n_c
		if s_c != 0:
			s['sizes'] += drops['round_sizes']
			s['shapechange'] += s_c
			

	print(len(sizes), "droplets, with", round(n['shapechange']*100/len(sizes),1), "% shape-changing")

	d = {"sizes": sizes, "density": density/len(pics), "nematic": n, "smectic": s}

	with open("saves/" + title + " video.bin", "wb") as f:
		pickle.dump(d, f)

def combine_vids(title, saves, save, show):
	
	n = []
	s = []

	for save in saves:
		with open(save, "rb") as f:
			data = pickle.load(f)
#			print("\n",save)
#			std.pprint(data)
			n.append(data['nematic'])
			s.append(data['smectic'])
	
	avg_n = [get_percentage(i) for i in n]
	avg_s = [get_percentage(i) for i in s]

	std.pprint(avg_n, title + " nematic ")
	std.pprint(avg_s, title + " smectic ")

	with open("saves/" + "shapechange " + title + ".bin", "wb") as f:
		pickle.dump({"nematic": n, "smectic": s}, f)

def stats_vids(title, saves, save, show):
	n = []
	s = []
	p = []
	
	for save in saves:
		with open(save, "rb") as f:
			data = pickle.load(f)
			n.append(data['nematic'])
			s.append(data['smectic'])
			p.append(int(save.split(' ')[1].split("wt")[0]))
#			if p[-1] == 0.0:
#				p[-1] = 0.1



	avg_n = [np.asarray([get_percentage(i) for i in n_s]) for n_s in n]
	avg_s = [np.asarray([get_percentage(i) for i in s_s]) for s_s in s]
	
	mean_n = [np.mean(i)*100 for i in avg_n]
	mean_s = [np.mean(i)*100 for i in avg_s]
	std_n  = [np.std(i) *100 for i in avg_n]
	std_s  = [np.std(i) *100 for i in avg_s]

	fig, ax = plt.subplots()

	w = 0.2 * np.array(p)
	if w[0] == 0.0:
		w[0] = 0.25

	ax.bar(p, mean_n, yerr=std_n, width=w, label="Nematic", color='m')
	ax.bar(p, mean_s, yerr=std_s, width=w, label="Smectic", color='g')
	
	ax.set_ylabel("\\% of droplets which are shape-changing")
	ax.set_xlabel("wt\\% Biotin-X-DHPE")

	ax.set_ylim(bottom=0)
	ax.set_xlim(left=-0.1)
	ax.set_xscale('symlog')

	ax.set_xticks(p, p)

	ax.legend()
	
	create_plot(title, save, show, True)


def bin_sizes(sizes):
	all_sizes = []
	for i in range(len(sizes)):
		all_sizes += sizes[i]

	binedges = np.histogram_bin_edges(all_sizes,bins='doane')

	bincenters = 0.5*(binedges[1:]+binedges[:-1])
	
	return (binedges, bincenters)


def video_sizes(name, file, save, show):
	fname = "saves/video_distr_" + name + ".bin"
	try:
		with open(fname, "rb") as f:
			data = pickle.load(f)
		print("Loaded existing data")
	except:
		vid = pims.ImageIOReader(file)
	
		rate = 16 * 1 # Do something every 16 frames, or every 1 sec at 16 fps
	
		data = {"index": [], "round": [], "elongated": [], "round_sizes": [], "density": []}
	
		for i in range(0,len(vid), rate):
			print(i, "secs =", round(i/60,1), "mins")
			droplets = droplet_analysis(name, vid[i], get_magnification(file), False, False)
#			data['round'].append(droplets['round'])
#			data['elongated'].append(droplets['elongated'])
			data['round_sizes'].append(droplets['round_sizes'])
			data['density'].append(droplets['density'])
			data['index'].append(i)

		with open(fname, "wb") as f:
			pickle.dump(data, f)

#	std.pprint(data)

	fig, ax = plt.subplots()

	binedges,bincenters = bin_sizes(data['round_sizes'])
	
	binedges[0] -= 1
	binedges[-1] += 1

	freqs = []
	for s in data['round_sizes']:
		d = np.bincount(np.digitize(s, binedges))[1:]
		f = d/sum(d)
		while len(f) < len(bincenters):
			f = np.append(f, 0)
		freqs.append(f)

	# Average the first n, use those to normalise all others
	n = 2
	norm = np.copy(freqs[0])
	for i in range(1,2):
		for j in range(len(freqs[0])):
			norm[j] += freqs[i][j]
	norm = norm/n

	freqs_norm = np.array([f - norm for f in freqs])

	max_f = 0
	min_f = 1000

	for f in freqs_norm:
		for y in f:
			if y < min_f:
				min_f = y
			if y > max_f:
				max_f = y
	print(min_f, max_f)

	im = ax.imshow(np.transpose(freqs_norm), interpolation="none")
#	scalebar = mpatches.Rectangle((2, 2), 5, 5, color=im.cmap(im.norm(min_f)))
#	ax.add_patch(scalebar)
#	scalebar2 = mpatches.Rectangle((7, 2), 5, 5, color=im.cmap(im.norm(max_f)))
#	ax.add_patch(scalebar2)

	ax.set_xlabel("Time (s/16)")
	ax.set_ylabel("Droplet diameter ($\\mathrm{\\mu m}$)")

	create_plot(name, save, show, False)


def combine_video_sizes(title, files, save, show):
	sizes = []
	for file in files: 
		with open(file, "rb") as f:
			sizes.append(pickle.load(f)['round_sizes'])
	
	binedges,bincenters = bin_sizes(np.concat(sizes))
	






