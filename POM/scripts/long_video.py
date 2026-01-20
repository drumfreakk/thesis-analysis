

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

	fig, ax = plt.subplots(figsize=(8,8))
	make_vid_plot(np.transpose(freqs_norm), name, binends, rate, save, show, fig, ax)
	create_plot(name, save, show, False)


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

	# t = 0 and t = 1h = 3600 s = 225
	raw = [[], []]
	for s in sizes:
		raw[0] += s[0]
		raw[1] += s[225]

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

	np.savez("saves/video_combined " + title + ".npz", freqs=avg_freq, rate=rate, binedges=binedges, t0=raw[0], t1=raw[1]) 

	# Plot that
	fig, ax = plt.subplots(figsize=(8,8))
	combine_video_graph(avg_freq, title, binedges, rate, fig, ax)
	create_plot(title, save, show, False)


def combine_video_graph(avg_freq, title, binedges, rate, fig, ax, colorbar=True, cutoff=False):
	# Average the first n, use those to normalise all others
	n = 2
	norm = np.copy(avg_freq[0])
	for f in avg_freq[1:n]:
		for j in range(len(f)):
			norm[j] += f[j]
	norm = norm/n

	freqs_norm = np.array([f - norm for f in avg_freq])

	return make_vid_plot(np.transpose(freqs_norm), title, (binedges[0], binedges[-1]), rate, True, True, fig, ax, colorbar, cutoff)
	

def make_vid_plot(freqs, name, sizes, rate, save, show, fig, ax, colorbar=True, cutoff=False):

	norm_map = mcolors.Normalize(vmin=-0.5, vmax=0.5)
	cmap = 'coolwarm'

	if cutoff:
		fnew = []
		for f in freqs:
			fnew.append(f[:int(3600/rate)+2])
		freqs = np.array(fnew)
	
	extent = (-0.5, (rate*len(freqs[0])/60)-0.5,\
			  sizes[1]-0.5, sizes[0]-0.5) # (l, r, b, t)


	im = ax.imshow(freqs, cmap=cmap, norm=norm_map, interpolation="none", extent=extent)

	if extent[1] >= 60 and not cutoff:
		ax.axvline(60, color='m', linestyle='dashed', label="Start temperature change")

	ax.set_xlabel("Time (minutes)")
	ax.set_ylabel("Droplet diameter ($\\mathrm{\\mu m}$)")

	fraction = 0.046 * ((extent[2]-extent[3])/(extent[1]-extent[0]))
	if colorbar:
		fig.colorbar(im, fraction=fraction, label="Fractional increase in frequency")

	return (norm_map, cmap)


def time_stats(savefile):
	data = np.load(savefile)
	title = savefile[21:-4]
	print(title)

	ks = stats.ks_2samp(data['t0'], data['t1'])
	
	print("KS Statistic:     ",ks.statistic)
	print("P-Value:          ",ks.pvalue)
	print("KS Stat location: ",ks.statistic_location)
	print("KS Stat sign:     ",ks.statistic_sign)
	
	fig, ax = plt.subplots()

	time_stats_graph(savefile, ax, True)
	

def time_stats_graph(savefile, ax, plot=True):
	data = np.load(savefile)
	avg_freqs = data['freqs']
	rate = data['rate']
	binedges = data['binedges']
	title = savefile[21:-4]
	
	times = [0,int(3600/rate)] # 0 sec and 1h respectively
	if times[1] >= len(avg_freqs):
		times[1] = len(avg_freqs)-1
	to_check = [avg_freqs[i] for i in times]

	bincenters = 0.5*(binedges[1:]+binedges[:-1])
	width = (binedges[-1]-binedges[0])/(2.2*len(bincenters))

	ax.bar(bincenters-width/2, to_check[0], width=width, color="b", linewidth=0,\
		   label="$t=" + str(round(times[0]*rate/60,1)) + "$ mins") 
	ax.bar(bincenters+width/2, to_check[1], width=width, color="m", linewidth=0,\
	       label="$t=" + str(round(times[1]*rate/60,1)) + "$ mins") 
	create_hist(ax, title + " - distribution", True, True, False, plot=plot)

def dif_stats(file1, file2):
	data1 = np.load(file1)
	avg_freqs1 = data1['freqs'][0]
	data2 = np.load(file2)
	avg_freqs2 = data2['freqs'][0]
#	rate1 = data1['rate']
#	binedges = data['binedges']
#	title = savefile[21:-4]

#	times = [0,int(3600/rate)] # 0 sec and 1h respectively
#	if times[1] >= len(avg_freqs):
#		times[1] = len(avg_freqs)-1
#	to_check = [avg_freqs[i] for i in times]

	ks = stats.ks_2samp(avg_freqs1, avg_freqs2)

	print("KS Statistic:     ",ks.statistic)
	print("P-Value:          ",ks.pvalue)
	print("KS Stat location: ",ks.statistic_location)
	print("KS Stat sign:     ",ks.statistic_sign)
	


