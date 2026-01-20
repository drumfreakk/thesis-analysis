
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

import pandas as pd

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

def K11(T):
	# Values from Peddireddy, supp. info
	# Measured values from a screenshot, not the nicest way to do it but it gets values at least
	
	K11_px = {34: 322, 35: 297, 36: 266, 37:234, 38: 192, 39: 149}
	# 0-12 = 565 px -> ~47 px/pN
	K11 = {}
	
	for k,v in K11_px.items():
		K11[k] = v * 12/565
	
	if T not in K11.keys():
		return 0
	return K11

def Omega(T):
	# Values from Peddireddy, supp. info
	# Measured values from a screenshot, not the nicest way to do it but it gets values at least

	# Omega = 2 + beta * arctan(sqrt(beta - 1)) / sqrt(beta - 1)
	# beta = K33 / K11

	beta_px = {34: 577, 35: 409, 36: 398, 37: 327, 38: 304, 39: 300}
	# 0.4-1.8: 769 px

	beta = {}

	for k,v in beta_px.items():
		beta[k] = v * 1.4/769 + 0.4

	if T not in beta.keys():
		return 0

	if beta[T] <= 1:
		Omega = 3
	else:
		Omega = 2 + beta[T] * np.arctan(np.sqrt(beta[T] - 1)) / np.sqrt(beta[T] - 1)
	
	return Omega


def laplace_pressure():
	fig,ax = plt.subplots()
	print(0.5 + 0.5 * np.sqrt((3-2)/3))
	T = [34,35,36,37,38,39]
	ratio = [0.5 + 0.5 * np.sqrt((Omega(t) - 2)/Omega(t)) for t in T]
	inv = [1/r for r in ratio]
	ax.plot(T, ratio, label="$\gamma_d / \gamma_f$")
	ax.plot(T, inv, label="$\gamma_f / \gamma_d$")
	create_plot("aaa", False, True, True)

def surface_tension(filename):
	fig, ax = plt.subplots()

	surface_tension_graph(filename, ax)

	create_plot("Surface Tension or something", True, True, True)	


def surface_tension_graph(filename, ax):
	xls = pd.ExcelFile(filename)
	i = 0

	markers = ["D", "o", "s", "v"] 
	colors = ["m", "b", "y", "g"]

	for sheet in np.sort(xls.sheet_names):
		df = pd.read_excel(xls, sheet, header=0, usecols=["Temperature (C)", "Fibre radius (um)"])
		
		# rf = - Omega * K11 / gamma_eff
		# gamma_eff = - Omega * K11 / rf
		res = []
		for row in df.itertuples(index=False):
			res.append(- Omega(row._0) * K11(row._0) / row._1)
		df['Surface tension'] = res

		dfhigh = df[df["Temperature (C)"] > 33]
		temps = dfhigh.groupby('Temperature (C)')
		means = temps.mean()

		ax.errorbar(means.index, means["Surface tension"], yerr=temps.std()["Surface tension"],\
					 color=colors[i], marker=markers[i], linestyle=':', label=sheet)

		i += 1
	
	xlim = ax.get_xlim()
	ax.set_xlim(xlim[0]-0.5, xlim[1]+0.5)

	ax.set_xlabel("Temperature ($^\\circ$C)")
	ax.set_ylabel("IFT ($\\mathrm{\\mu N/m}$)")


