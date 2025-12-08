#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy

def exponential(x, a, b):
	return a * np.exp(b*x)


def weighted_avg(values, weights):
#	print(values*weights)
#	print(weights)
	return (values * weights).sum() / weights.sum()


def get_avg(df, column_name, cutoff_low, cutoff_high):
	df1 = df.loc[cutoff_low:cutoff_high]
	return weighted_avg(values=df1.index, weights=df1[column_name])

def get_means_sheet(filename):
	out = "Sample\tMeasurement\tPeak\tLower width\tUpper width\n"
	mean_vals = {}
	
	xls = pd.ExcelFile(filename)
	
	for sheet in xls.sheet_names:
		used_cols = "I:L"
		if sheet=="PBS 8.4":
			used_cols = "I:K"

		df1 = pd.read_excel(xls, sheet, index_col=0, usecols=used_cols, skiprows=12)
		df1 = df1.dropna(how='any')
		print(sheet)
		print(df1)
#		print(df1.to_string())
#		plot = df1.mean(axis=1).plot()
#		plot.set_xscale('log')
#		plt.show()
#		if filename == "day_0.xlsx":
#			cutoff=[0,10**3]
#			if sheet == "50%":
#				cutoff=[0,10**2,10**3]
#			if sheet == "80%":
#				cutoff=[0,25,10**3]
#		if filename == "day_1.xlsx":
#			cutoff=[0,10**4]
#			if sheet == "0%":
#				cutoff=[0,200,2.3*10**3]
#			if sheet == "2%":
#				cutoff=[0,200,10**4]
#			if sheet == "20%":
#				cutoff=[0,10,200,10**4]
#			if sheet == "50%":
#				cutoff=[0,210,2.3*10**3, 10**4]
#			if sheet == "80%":
#				cutoff=[0,24,10**3]
#			if sheet == "0,2%":
#				cutoff=[0,200,10**4]
#		if filename == "day_4.xlsx":
#			cutoff=[0,10**4]
			
		popt, _ = scipy.optimize.curve_fit(exponential, np.arange(len(df1.index)), df1.index, [0.46, 0.14])

#		for i in range(len(cutoff) - 1):
		#avgs = []

# These should be moved out of the loop
		#col means sample concentration + peak #
		means = {} # col => []  series in time
		errs = {} # col => [[],[]]   [0] are the lower errors, [1] the upper
		#print(cutoff, i)

		#Here its all still in the same sample
		temp_means = []
		temp_errs = [[],[]]
		for col in df1.columns:
			peaks_index, _ = scipy.signal.find_peaks(df1[col])
			widths = scipy.signal.peak_widths(df1[col], peaks_index)
			peaks = [df1.index[i] for i in peaks_index]
			lower_width = [peaks[i] - exponential(widths[2][i], popt[0], popt[1])\
							for i in range(len(widths[2]))]
			upper_width = [exponential(widths[3][i], popt[0], popt[1]) - peaks[i]\
							for i in range(len(widths[3]))]
		#	print("COL", col)
			temp_means.append(peaks)
			temp_errs[0].append(lower_width)
			temp_errs[1].append(upper_width)
			for i in range(len(peaks)):
				out += sheet + "\t" + col + "\t"
				out += str(peaks[i]) + "\t"
				out += str(lower_width[i]) + "\t"
				out += str(upper_width[i]) + "\n"
	#	print(temp_means)
	#	print(temp_errs)
	#	print(out)
#		max_peaks = 0
#		min_peaks = 1000
#		for i in range(len(temp_means)):
#			if len(temp_means[i]) > max_peaks:
#				max_peaks = len(temp_means[i])
#			if len(temp_means[i]) < min_peaks:
#				min_peaks = len(temp_means[i])
#		
#		mean = [[] for i in range(max_peaks)] # [peaks [single peak, values]]
#		errs = [[[],[]] for i in range(max_peaks)] # [peaks [single peak, values [lower],[upper]]]
#
#		for i in range(len(temp_means)):
#			if i == 0:
#				for j in range(len(temp_means[0])):
#					mean[j].append(temp_means[0])
#					errs[j][0].append(temp_errs[0][0])
#					errs[j][1].append(temp_errs[1][0])
#			else:
#				if 

#				avgs.append(get_avg(df1, col, cutoff[i], cutoff[i+1]))
#			
#			if filename == "day_1.xlsx" and sheet=="2%" and i == 0:
#				avg = sum(avgs[1:])/len(avgs[1:])
#			elif filename == "day_1.xlsx" and sheet=="20%" and i == 0:
#				avg = avgs[1]
#			else:
#				avg = sum(avgs)/len(avgs)
#			
#			mean_vals[sheet + "_" + str(i)] = avg
#		#	print(mean_vals)
#		if len(cutoff) < 4:
#			for i in range(len(cutoff)-1, 4):
#				mean_vals[sheet + "_" + str(i)] = avg
#		#	print("ADDED", mean_vals)
		plot = df1.plot()
		plot.set_xlim([10**0,10**4])
		plot.set_xscale('log')
		plot.set_title(filename.split(".")[0] + " " + sheet)
		plot.set_xlabel("Size (d.nm)")
		plot.set_ylabel("Intensity (%)")
		plot.get_legend().remove()
		plt.savefig("pics/" + filename.split(".")[0] + "_" + sheet + ".png")
		plt.show()
		plt.close()
	with open(filename + ".tsv", "w") as f:
		f.write(out)
	print(out)
	return mean_vals

get_means_sheet("Buffer permutations.xlsx")

#means = {}
#means[0] = get_means_sheet("day_0.xlsx")
#means[1] = get_means_sheet("day_1.xlsx")
#means[2] = get_means_sheet("day_4.xlsx")
#
#time_series = [0,1]
## ratio_val => [z-avg_0, z_avg_1]
#data_series = {}
#
##print(means)
#
#for i in time_series:
#	for col in means[i].keys():
#		if i == 0:
#			data_series[col] = [means[i][col]]
#		else:
#			#data_series[col].append(means[i][col])
#
#print(data_series)
#
#for col in means[i].keys():
#	c = 'k'
#	if col.startswith("0% fridge"):
#		c = 'k'
#	elif col.startswith("0,2%"):
#		c = 'g'
#	elif col.startswith("2%"):
#		c = 'r'
#	elif col.startswith("20%"):
#		c = 'c'
#	elif col.startswith("50%"):
#		c = 'm'
#	elif col.startswith("80%"):
#		c = 'y'
#	elif col.startswith("0%"):
#		c = 'b'
#	
#	if col.endswith("_0"):
#		plt.semilogy(time_series, data_series[col], label=col, color=c)
#	else:
#		plt.semilogy(time_series, data_series[col], color=c)
#
#plt.xlabel("Time (days)")
#plt.ylabel("Size (d.nm)")
#
#plt.legend()
#plt.show()
#



