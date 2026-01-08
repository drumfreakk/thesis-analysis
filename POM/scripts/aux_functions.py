
import sys
sys.path.insert(1, '../')
import standard as std

import matplotlib.pyplot as plt 

import numpy as np

def get_magnification(fname):
	try:
		mag = fname.split('.')[-2].split('-')[-1]
	except:
		mag = input("Magnification? ")
	return mag

def get_scales(magnification):
	match magnification:
		case '5x':
			return (1/2.03, 50)
		case '10x':
			return (1/4.09, 50)
		case '20x':
			return (1/8.17, 50)
		case '40x':
			return (1/16.56, 20)
		case _:
			print("WARNING: No magnification found, guessing pixel size")
			return (1,0)
	#Returns (spacing, length_scalebar_um)
	

def create_hist(ax, title, save, show, legend=True):
	if legend:
		ax.legend()
	ax.set_ylabel("Frequency")
	ax.set_xlabel("Droplet diameter ($\\mathrm{\\mu m}$)")

	create_plot(title, save, show, legend)

def create_plot(title, save, show, legend=True):

	plt.tight_layout()
	plt.title(std.tex_friendly(title))
	
	if save:
		plt.savefig("graphs/" + title + ".png")
	if show:
		plt.show()
	plt.close()


def get_percentage(d):
	return 0 if len(d['sizes']) == 0 else d['shapechange'] / len(d['sizes'])

def bin_sizes(sizes):
	all_sizes = np.concat(sizes)

	binedges = np.histogram_bin_edges(all_sizes,bins='doane')

	bincenters = 0.5*(binedges[1:]+binedges[:-1])
	
	return (binedges, bincenters)

