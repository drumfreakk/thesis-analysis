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
	"axes.prop_cycle": cycler(color='bgrmcyk'),
	"font.serif": "C059",
	"font.size": 10
})

#print(plt.rcParams.keys())

def tex_friendly(string):
	s = "\\#".join(string.split('#'))
	return "\\%".join(s.split('%'))

def pout(a, line_prefix = "", skip_first_prefix=False):
	out = "" if skip_first_prefix else line_prefix
	
	if isinstance(a, (list,np.ndarray)):
		out += "[\n" + line_prefix
		for i in a:
			out += "\t" + pout(i, '\t', True) + ",\n" + line_prefix
		out += "]"

	elif isinstance(a, dict):
		out += "{\n" + line_prefix
		for k,v in a.items():
			out += "\t" + str(k) + "\t => " + pout(v, "\t    ", True) + ",\n" + line_prefix
		out += "}"

	elif isinstance(a, (float, np.float64)):
		out += str(round(a,3))

	else:
		out += str(a)
	
	return out

def pprint(a, line_prefix=""):
	print(pout(a,line_prefix))




