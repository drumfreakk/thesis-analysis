

import sys
sys.path.insert(1, '../')
import standard as std

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors

from scipy import stats

import pims

import pickle

from scripts.aux_functions import *
from scripts.image_analysis import *

from time import time

def analyse_video_sizes(name, data, rate, save, show):
#	std.pprint(data)
	freqs,binends = bin_videos(data['round_sizes'])
	
	# Average the first n, use those to normalise all others
	n = 2
	norm = np.copy(freqs[0])
	for i in range(1,n):
		for j in range(len(freqs[0])):
			norm[j] += freqs[i][j]
	norm = norm/n

	freqs_norm = np.array([f - norm for f in freqs])

	make_vid_plot(np.transpose(freqs_norm), name, binends, rate, save, show)


def bin_videos(data, sizes=None):

	if sizes == None:
		binedges_orig,bincenters = bin_sizes(data)
	else:
		binedges_orig,bincenters = sizes

	binedges = np.copy(binedges_orig)

	binedges[0] -= 1
	binedges[-1] += 1

	freqs = []
	for s in data:
		d = np.bincount(np.digitize(s, binedges))[1:]
		f = d/sum(d)
		while len(f) < len(bincenters):
			f = np.append(f, 0)
		freqs.append(f)

	return (freqs, (binedges_orig[0], binedges_orig[-1]))


def make_vid_plot(freqs, name, sizes, rate, save, show):
	fig, ax = plt.subplots(figsize=(8,8))

	norm_map = mcolors.Normalize(vmin=-0.5, vmax=0.5)
	extent = (-0.5, (rate*len(freqs[0])/60)-0.5,\
			  sizes[1]-0.5, sizes[0]-0.5) # (l, r, b, t)
	
	im = ax.imshow(freqs, cmap='coolwarm', norm=norm_map, interpolation="none", extent=extent)

	if extent[1] >= 60:
		ax.axvline(60, color='m', linestyle='dashed', label="Start temperature change")

	ax.set_xlabel("Time (minutes)")
	ax.set_ylabel("Droplet diameter ($\\mathrm{\\mu m}$)")

	fig.colorbar(im, ax=ax, shrink=0.8, label="Fractional increase in frequency relative to $t=0$")

	create_plot(name, save, show, True)


def video_size_distr(name, file, save, show):
	fname = "saves/video_distr_" + name + ".bin"
	try:
		with open(fname, "rb") as f:
			data,rate = pickle.load(f)
		print("Loaded existing data")
	except:
		vid = pims.PyAVReaderTimed(file)
		rate = 16 * 1 # Do something every 16 frames, or every 1 sec of video at 16 fps, or every 16 seconds in real life (?)
	
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
			pickle.dump((data, rate), f)

	analyse_video_sizes(name, data, rate, save, show)


def combine_video_sizes(title, files, save, show):
	sizes = []
	all_sizes = []
	for file in files: 
		with open(file, "rb") as f:
			data,rate = pickle.load(f)
			data = data['round_sizes']
			sizes.append(data)
			all_sizes += data

	binedges,bincenters = bin_sizes(all_sizes)
	
	# Bin each video individually
	all_freqs = []
	for video in sizes:
		freqs,_ = bin_videos(video, (binedges, bincenters))
		all_freqs.append(freqs)

	# Crop all videos to the same length
	min_len = min([len(i) for i in all_freqs])
	all_freqs = [f[:min_len] for f in all_freqs]

	# Get average frequency per bin
	avg_freq = all_freqs[0]
	for f in all_freqs[1:]:
		for j in range(len(f)):
			avg_freq[j] += f[j]
	avg_freq = np.array([f/3 for f in avg_freq])
	#print(avg_freq[0])

	np.savez("saves/video_combined " + title + ".npz", freqs=avg_freq, rate=rate, binedges=binedges) 
	# Plot that

	# Average the first n, use those to normalise all others
	n = 2
	norm = np.copy(avg_freq[0])
	for f in avg_freq[1:n]:
		for j in range(len(f)):
			norm[j] += f[j]
	norm = norm/n

	freqs_norm = np.array([f - norm for f in avg_freq])

	make_vid_plot(np.transpose(freqs_norm), title, (binedges[0], binedges[-1]), rate, save, show)

def time_stats(savefile):
	data = np.load(savefile)
	avg_freqs = data['freqs']
	rate = data['rate']
	binedges = data['binedges']
	title = savefile[21:-4]
	print(title)

	times = [0,int(3600/rate)] # 0 sec and 1h respectively
	if times[1] >= len(avg_freqs):
		times[1] = len(avg_freqs)-1
	to_check = [avg_freqs[i] for i in times]

	ks = stats.ks_2samp(to_check[0], to_check[1])
	
	print("KS Statistic:     ",ks.statistic)
	print("P-Value:          ",ks.pvalue)
	print("KS Stat location: ",ks.statistic_location)
	print("KS Stat sign:     ",ks.statistic_sign)


	bincenters = 0.5*(binedges[1:]+binedges[:-1])
	width = (binedges[-1]-binedges[0])/(3*len(bincenters))

	fig, ax = plt.subplots()
	ax.bar(bincenters-width/2, to_check[0], width=width, color="b",\
		   label="$t=" + str(round(times[0]*rate/60,1)) + "$ mins") 
	ax.bar(bincenters+width/2, to_check[1], width=width, color="m",\
	       label="$t=" + str(round(times[1]*rate/60,1)) + "$ mins") 
	create_hist(ax, title + " - distribution", True, True, True)




