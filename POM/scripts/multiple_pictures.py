
import sys
sys.path.insert(1, '../')
import standard as std

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops 

import pickle

from scripts.aux_functions import *
from scripts.image_analysis import *
from scripts.long_video import *

def combine_pictures(name, pictures, save, show):
	sizes = []
	density = 0
	for pic in pictures:
		drops = get_droplets(name + pic.split('/')[-1], pic, False, False)
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

def combine_samples(title, pics, save, show):
	sizes = []
	densities = []

	n = 0

	for i in pics:
		with open(i, "rb") as f:
			data = pickle.load(f)
			sizes.append(data['sizes'])
			densities.append(data['density'])
		if "video.bin" not in i:
			n += 1


	with open("saves/combine_samples " + title + ".bin", "wb") as f:
		pickle.dump({"sizes": sizes, "densities": densities}, f)

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

	all_sizes = np.concat(sizes)
#	all_sizes = []
#	for s in sizes:
#		all_sizes = np.concat([all_sizes, s])
	
	width = (max(all_sizes)-min(all_sizes))/len(bincenters)
	ax.bar(bincenters, means, width=width, yerr=stds,\
		   label="n = " + str(n) + "\n" + str(len(all_sizes)) + " droplets")
	ax.set_ylim(bottom=0)
	
	ax.axvline(np.mean(all_sizes), color='m',  linestyle='dashed', label="Mean = $" + str(round(np.mean(all_sizes))) + " \\mathrm{\\mu m}$")

	create_hist(ax, title, save, show, True)

def compare_samples(saves):
	sizes_from_saves = []
	names = []

	for i in saves:
		names.append(' '.join(i.split('.')[0].split()[1:]))
		with open(i, "rb") as f:
			data = pickle.load(f)
			sizes_from_saves.append(np.concat(data['sizes']))

#	rng = np.random.default_rng()
#	sizes_from_saves = [stats.norm.rvs(size=95) for i in range(2)]
#	sizes_from_saves = [stats.norm.rvs(size=95), stats.uniform.rvs(size=100)]

	for i in range(len(sizes_from_saves)):
		for j in range(i+1, len(sizes_from_saves)):
			ks = stats.ks_2samp(sizes_from_saves[i], sizes_from_saves[j])
		#	ks = stats.ks_2samp(distrs[0], distrs[1])
		
			print(names[i], "vs", names[j])
			#print("KS Statistic:     ",ks.statistic)
			print("P-Value:          ",ks.pvalue)
			#print("KS Stat location: ",ks.statistic_location)
			#print("KS Stat sign:     ",ks.statistic_sign)




