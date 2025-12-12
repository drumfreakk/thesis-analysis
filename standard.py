import matplotlib  as mpl 
import matplotlib.pyplot as plt 


mpl.style.use("classic")
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif"
})

def tex_friendly(string):
	s = "\\#".join(string.split('#'))
	return "\\%".join(s.split('%'))

