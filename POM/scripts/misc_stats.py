
import sys
sys.path.insert(1, '../')
import standard as std

import numpy as np

import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

from scipy import ndimage

import skimage as ski
from skimage.measure import label, regionprops 

import pickle

from scripts.aux_functions import *
from scripts.image_analysis import *
from scripts.long_video import *

def critical_sizes(name, shapechange, sizes_save):
	print(name)
	with open(shapechange, "rb") as f:
		data = pickle.load(f)
		n = data['nematic']
	
	with open(sizes_save, "rb") as f:
		sizes = pickle.load(f)['sizes']

	avg_n = np.asarray([get_percentage(n_s) for n_s in n])
	shapechange_p = np.mean(avg_n)

	sizes = np.sort(np.concat(sizes))

	critical_point = int(shapechange_p * len(sizes))
	print("Critical size:", sizes[-critical_point])

