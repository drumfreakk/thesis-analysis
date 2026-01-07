
import sys
sys.path.insert(1, '../')
import standard as std

import matplotlib.pyplot as plt 


def get_magnification(fname):
	try:
		mag = fname.split('.')[-2].split('-')[-1]
	except:
		mag = input("Magnification? ")
	return mag

def get_scales(magnification):
	match magnification:
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
	return (spacing, length_scalebar_um)
	

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

