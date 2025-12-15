import matplotlib  as mpl 
import matplotlib.pyplot as plt 

import numpy as np

from cycler import cycler

mpl.style.use("classic")
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
	"figure.facecolor": "1.0",
	"savefig.dpi": 600,
	"axes.prop_cycle": cycler(color='bgrmcyk')
})

#print(plt.rcParams.keys())

def tex_friendly(string):
	s = "\\#".join(string.split('#'))
	return "\\%".join(s.split('%'))

def pout(a, line_prefix = ""):
	if isinstance(a, (list,np.ndarray)):
		out = line_prefix + "[\n" + line_prefix
		for i in a:
			out += "\t" + pout(i, '\t') + ",\n" + line_prefix
		out += "]"
	elif isinstance(a, (float, np.float64)):
		out = line_prefix + str(round(a,3))
	else:
		out = line_prefix + str(a)
	return out

def pprint(a):
	print(pout(a))




