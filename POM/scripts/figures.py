
import sys
sys.path.insert(1, '../')
import standard as std

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.cm as cm

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops 

import pims

import pickle

from scripts.aux_functions import *
from scripts.multiple_pictures import *
from scripts.short_video import *
from scripts.misc_stats import *

def bdhpe_variation_figure(percentages, shapechange, IFT):
	print(percentages)
	print(shapechange)
	print(IFT)
	
	distrs = []
	for percent in percentages:
		with open(percent, "rb") as f:
			distrs.append(pickle.load(f))	

	with open(shapechange, "rb") as f:
		shapechange = pickle.load(f)
	n = 1

	fig, axs = plt.subplots(2,4, figsize=(7*n,5*n))
	
	combine_samples_graph(distrs[0]['sizes'], 0, axs[0,0])
	combine_samples_graph(distrs[1]['sizes'], 0, axs[1,0])
	combine_samples_graph(distrs[2]['sizes'], 0, axs[0,1])
	combine_samples_graph(distrs[3]['sizes'], 0, axs[1,1])

	axs[0,1].sharex(axs[1,1])
	axs[1,0].sharex(axs[0,1])
	axs[0,0].sharex(axs[1,0])

#	axs[0,0].set_xlabel(None)
#	axs[0,1].set_xlabel(None)
#	axs[0,1].set_ylabel(None)
#	axs[1,1].set_ylabel(None)

	stats_vids_graph(shapechange['p'], shapechange['mean_n'], shapechange['mean_s'],\
					 shapechange['std_n'], shapechange['std_s'], axs[0,2])

	surface_tension_graph(IFT, axs[1,2])

#	axs[2,1].plot([1,2,3,4], [2,4,6,8])

	axs[1,0].set_title("\\textbf{a b c d e f}")
#top=0.985,
#bottom=0.09,
#left=0.08,
#right=0.99,
#hspace=0.3,
#wspace=0.35

	create_plot("shapechange-fig", True, True, False)

def time_figure(nothing, pbs, na):
	
	fig, axs = plt.subplots(2,3, width_ratios=[1,1,1], figsize=(7, 5))

	data = np.load(nothing)
	combine_video_graph(data['freqs'], "title", data['binedges'], data['rate'], fig, axs[0,0], False, True)
	time_stats_graph(nothing, axs[1,0], False)
	
	data = np.load(pbs)
	combine_video_graph(data['freqs'], "title", data['binedges'], data['rate'], fig, axs[0,1], False, True)
	time_stats_graph(pbs, axs[1,1], False)

	data = np.load(na)
	norm, cmap = combine_video_graph(data['freqs'], "title", data['binedges'], data['rate'], fig, axs[0,2], False, True)
	time_stats_graph(na, axs[1,2], False)

	axs[0,0].set_aspect('auto')
	axs[0,1].set_aspect('auto')
	axs[0,2].set_aspect('auto')

	axs[0,1].set_ylabel(None)
	axs[0,2].set_ylabel(None)
	axs[1,1].set_ylabel(None)
	axs[1,2].set_ylabel(None)

#	axs[0,1].sharey(axs[0,2])
#	axs[0,0].sharey(axs[0,1])
	create_plot("Time", True, True, False)

	plt.close()
	fig,ax= plt.subplots()
	#fraction = 0.046 * ((extent[2]-extent[3])/(extent[1]-extent[0]))
	fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), label="Fractional increase in frequency", cax=ax, orientation='horizontal')
	plt.show()

#top=0.99,
#bottom=0.1,
#left=0.085,
#right=0.985,
#hspace=0.322,
#wspace=0.307



