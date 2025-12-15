#!/usr/bin/python3

import sys
sys.path.insert(1, '../')
import standard
from standard import tex_friendly

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy
import sys

mpl.rc('image', cmap='gray')

def generate_plots(filename):
	xls = pd.ExcelFile(filename)
	
	for sheet in xls.sheet_names:
		used_cols = "I:L"
		if sheet=="PBS 8.4":
			used_cols = "I:K"

		intensity_df = pd.read_excel(xls, sheet, index_col=0, usecols=used_cols, skiprows=12)
		intensity_df = intensity_df.dropna(how='any')
		
		correlogram_df = pd.read_excel(xls, sheet, index_col=0, usecols="A:D")
		correlogram_df = correlogram_df.dropna(how='any')

		temp_means = []
		for col in intensity_df.columns:
			peaks_index, _ = scipy.signal.find_peaks(intensity_df[col])
			peaks = [intensity_df.index[i] for i in peaks_index]
			temp_means.append(peaks)
#		print(temp_means)
	

		fig, ax = plt.subplots()
#		ax.set_cmap("gnuplot2")
		ax.plot(intensity_df)	

		ax.set_xlim([10**0,10**4])
		ax.set_xscale('log')
		fig.suptitle(filename.split(".")[0] + " " + tex_friendly(sheet))
		ax.set_xlabel("Size (d.nm)")
		ax.set_ylabel("Intensity (\\%)")

		sub_ax = ax.inset_axes([0.74, 0.73, 0.24, 0.24])
		sub_ax.plot(correlogram_df)
		sub_ax.set_xscale('log')
		
		ylim = sub_ax.get_ylim()
		if ylim[1] <= 1.1:
			y_up = 1
		elif ylim[1] <= 1.6:
			y_up = 1.5
		elif ylim[1] <= 2.1:
			y_up = 2
		else:
			y_up = 2.5
		sub_ax.set_ylim([0, y_up])
		sub_ax.xaxis.set_ticks([10**0, 10**2, 10**4, 10**6])
		sub_ax.set_xlabel("Lag time ($\\mathrm{\\mu s}$)")
		sub_ax.set_ylabel("Correlation")

		plt.savefig("graphs/" + filename.split(".")[0] + " - " + sheet + ".png")
#		plt.show()
		plt.close()

if len(sys.argv) != 2:
	print("Use a proper argument")
else:
	generate_plots(sys.argv[1])



