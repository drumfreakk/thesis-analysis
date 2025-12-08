#!/usr/bin/python

import numpy as np
import pandas as pd

import pims
import trackpy as tp
import os

import matplotlib  as mpl 
import matplotlib.pyplot as plt 

from scipy import ndimage
from skimage import morphology, util, filters

@pims.pipeline
def preprocess(img):
    """
    Apply image processing functions to return a binary image
    """
    # Apply thresholds
    adaptive_thresh = filters.threshold_local(img, block_size=301)
    img = img < adaptive_thresh
    # Apply dilation twice to fill up small voids
    for _ in range(2):
        img = ndimage.binary_dilation(img)
    return util.img_as_int(img)


datapath = '.'
prefix = '20251201-3'

rawframes = preprocess(pims.open(os.path.join(datapath, prefix + '.tif')))
plt.imshow(rawframes[0])




plt.show()
