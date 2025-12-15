import matplotlib  as mpl 
import matplotlib.pyplot as plt 

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

