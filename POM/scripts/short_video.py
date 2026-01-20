

import sys
sys.path.insert(1, '../')
import standard as std

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops 

import pims

import pickle

from scripts.aux_functions import *
from scripts.image_analysis import *

from time import time


def video(title, pics, save, show):
	sizes = []
	n = {"sizes": [], "shapechange": 0}
	s = {"sizes": [], "shapechange": 0}
	density = 0
	for pic in pics:
		drops = get_droplets("Video analysis: " + pic.split("/")[-1], pic, False, True)
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

	with open("saves/stats_vids " + title + ".bin", "wb") as f:
		pickle.dump({"p": p, "mean_n": mean_n, "mean_s": mean_s, "std_n": std_n, "std_s": std_s}, f)
	
	fig, ax = plt.subplots()

	stats_vids_graph(p, mean_n, mean_s, std_n, std_s, ax)
	
	create_plot(title, save, show, False)

def stats_vids_graph(p, mean_n, mean_s, std_n, std_s, ax):

	w = 0.3 * np.array(p)
	if w[0] == 0.0:
		w[0] = 0.15

	ax.bar(p, mean_n, yerr=std_n, label="Nematic", color='m', align='edge', width=-w)
	ax.bar(p, mean_s, yerr=std_s, label="Smectic", color='g', align='edge', width=w)
	
	ax.set_ylabel("\\% shape change")
	ax.set_xlabel("wt\\% Biotin-X-DHPE")

	ax.set_ylim(bottom=0)
	ax.set_xlim(left=-0.3)
	ax.set_xscale('symlog', linthresh=1)

	ax.set_xticks(p, p)

