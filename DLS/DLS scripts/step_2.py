#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
import pprint
from random import randrange


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
	#out = "Sample\tMeasurement\tPeak\tLower width\tUpper width\n"
	xls = pd.ExcelFile(filename)

	time_avg = {}

	time = 0
	out = "Sample\tPeak\tTime\tM\tL\tU\n"
	for sheet in xls.sheet_names:
		print("AAAA",sheet[-1],"\n\n\n\n")
		time += 1
		sample_peaks = {} # sample_name_peak => [[peak1,2,3], [err_lo1,2,3], [err_hi1,2,3]]
		df1 = pd.read_excel(xls, sheet)
		df1 = df1.dropna(how='any')
		print(df1)
		counts = {}
		for index, row in df1.iterrows():
			name = row['Sample'] + '_' + str(row["Measurement"])
			if name not in sample_peaks:
				sample_peaks[name] = [[],[],[]]
			sample_peaks[name][0].append(row["Peak"])
			sample_peaks[name][1].append(row["Lower width"])
			sample_peaks[name][2].append(row["Upper width"])
			counts[row['Sample']] = counts.get(row['Sample'], 0) + 1
#		print(sample_peaks)

		sample_avg = {}
		for key, value in sample_peaks.items():
			mean = np.mean(value[0])
			lowers = []
			uppers = []
			for i in range(len(value[0])):
				lowers.append(value[0][i] - value[1][i])
				uppers.append(value[0][i] + value[2][i])
			sample_avg[key] = [mean, mean - min(lowers), max(uppers) - mean]
		print("\n\n",sample_avg)

		for key, value in sample_avg.items():
		#	if key not in time_avg:
			time_avg[key + '_' + str(time)] = [int(sheet[-1]), [],[[],[]]]
			time_avg[key + '_' + str(time)][1].append(value[0])
			time_avg[key + '_' + str(time)][2][0].append(value[1])
			time_avg[key + '_' + str(time)][2][1].append(value[2])
			#out += key.split('_')[0] + '\t' + key.split('_')[1] + '\t' + str(time) +\
			#		'\t' + str(value[0]) + '\t' + str(value[1]) + '\t' + str(value[2]) + '\n'
			
		#	if len(time_avg[key][0]) < 


#		for index, row in df1.iterrows():
#			if counts[row['Sample']] < 4:
#				for i in range(counts[row['Sample']], 5):
#					#if time == 0:
#					if row['Sample'] + '_' + str(i) not in time_avg:
#						time_avg[row['Sample'] + '_' + str(i)] = [[],[[],[]]]
#					time_avg[row['Sample'] + '_' + str(i)][0].append(0)
#					time_avg[row['Sample'] + '_' + str(i)][1][0].append(0)
#					time_avg[row['Sample'] + '_' + str(i)][1][1].append(0)

#	with open("step2.tsv", "w") as f:
#		f.write(out)
	pprint.pprint(time_avg)
	return(time_avg)

#means = get_means_sheet("Tris trials_2.xlsx")
#means = get_means_sheet("step2.xlsx")
means = get_means_sheet("buffer_2.xlsx")

time_series = [0,3]
# ratio_val => [z-avg_0, z_avg_1]
#data_series = {}
#
##print(means)
#
#for i in time_series:
#	for col in means[i].keys():
#		if i == 0:
#			data_series[col] = [means[i][col]]
#		else:
#			data_series[col].append(means[i][col])
#
#print(data_series)

#for i in 


samples = ["Tris 7.4 NaCl", "Tris 7.4", "Tris 8.4"]
#samples = ["0% fridge", "0,2%", "2%", "20%", "50%", "80%", "0%"]
#samples = ["0% Tris"]
for s in samples:
	for col in means.keys():
		if col.startswith(s):
			plt.errorbar(means[col][0], means[col][1], means[col][2], c='k', fmt='o', capsize=5)
#	plt.errorbar(2,1,0)
#	plt.errorbar(3,2,0)
	
	plt.yscale('log')
	plt.ylim([10**0,10**4])
	plt.xlabel("Time (days)")
	plt.ylabel("Size (d.nm)")
	plt.title(s)

	plt.savefig("pics/overview_" + s + ".png")
	#plt.legend()
	plt.show()
	



