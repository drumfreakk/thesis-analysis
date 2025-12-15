
import sys
sys.path.insert(1, '../')
import standard
from standard import tex_friendly

import matplotlib.pyplot as plt 


def get_magnification(fname):
	return fname.split('.')[-2].split('-')[-1]

def create_hist(ax, title, save, show, legend=True):
	if legend:
		ax.legend()
	ax.set_ylabel("Frequency")
	ax.set_xlabel("Diameter ($\\mathrm{\\mu m}$)")

	create_plot(title, save, show, legend)

def create_plot(title, save, show, legend=True):

	plt.tight_layout()
	plt.title(tex_friendly(title))
	
	if save:
		plt.savefig("graphs/" + title + ".png")
	if show:
		plt.show()
	plt.close()
