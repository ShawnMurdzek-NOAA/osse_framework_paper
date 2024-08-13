"""
Compare Real and Synthetic Surface Station Observations for 2022

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import scipy.stats as ss
import pickle


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input pickle file (should contain the same number of real-data and synthetic-data obs)
parent_dir = '../analysis_code/NR_eval'
pickle_fname = parent_dir + '/sfc_station_compare_winter_2022.pkl'

# Parameters for real obs
with open('station_list.txt', 'r') as fptr:
    station_ids = fptr.readlines()
    for i in range(len(station_ids)):
        station_ids[i] = station_ids[i].strip()

# Output file name (include %s placeholder for plot type)
out_fname = '../figs/PNGs/SfcStationComparison%s_2022.png'


#---------------------------------------------------------------------------------------------------
# Make Plots
#---------------------------------------------------------------------------------------------------

# Read in pickled data
with open(pickle_fname, 'rb') as handle:
    all_data = pickle.load(handle)

# Parse data into 1D arrays for easier plotting
real_data = {}
fake_data = {}

data_vars = ['TOB', 'QOB', 'POB', 'UOB', 'VOB']
for d in data_vars:
    real_data[d] = []
    fake_data[d] = []

for sid in station_ids:
    for d in data_vars:
        real_data[d] = real_data[d] + list(np.ravel(all_data['real_stations'][sid][d])) 
        fake_data[d] = fake_data[d] + list(np.ravel(all_data['fake_stations'][sid][d])) 

for d in data_vars:
    real_data[d] = np.array(real_data[d])
    fake_data[d] = np.array(fake_data[d])

# Quick QC to remove large negative wind values
real_data['VOB'][real_data['VOB'] < -100] = np.nan

# Make histogram and scatterplots
fig_hist, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 10))
fig_scat, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 10))
for i, d in enumerate(data_vars):

    minval = min([np.nanmin(real_data[d]), np.nanmin(fake_data[d])])
    maxval = max([np.nanmax(real_data[d]), np.nanmax(fake_data[d])])

    # Histogram
    ax_hist = fig_hist.axes[i]
    real_hist = np.histogram(real_data[d], bins=25, range=(0.94*minval, 1.06*maxval))
    fake_hist = np.histogram(fake_data[d], bins=25, range=(0.94*minval, 1.06*maxval))
    bins = 0.5 * (real_hist[1][1:] + real_hist[1][:-1])
    ax_hist.plot(bins, real_hist[0], 'r-', lw=2.5, label='real data')
    ax_hist.plot(bins, fake_hist[0], 'b--', lw=2.5, label='synthetic data')
    ax_hist.set_xlabel(d, size=14)
    ax_hist.set_ylabel('counts', size=14)

    # Scatterplot
    ax_scat = fig_scat.axes[i]
    ax_scat.scatter(real_data[d], fake_data[d], s=2)
    ax_scat.plot([minval, maxval], [minval, maxval], 'k--')
    ax_scat.set_xlabel('real data', size=14)
    ax_scat.set_ylabel('synthetic data', size=14)
    ax_scat.set_title(d, size=16)
    ax_scat.grid()

plt.figure(fig_hist.number)
fig_hist.axes[-1].axis('off')
fig_hist.axes[2].legend()
plt.subplots_adjust(left=0.07, bottom=0.07, right=0.97, top=0.94, hspace=0.25, wspace=0.3)
plt.savefig(out_fname % 'Hist')

plt.figure(fig_scat.number)
fig_scat.axes[-1].axis('off')
plt.subplots_adjust(left=0.07, bottom=0.07, right=0.97, top=0.94, hspace=0.25, wspace=0.3)
plt.savefig(out_fname % 'Scat')


"""
End plot_NR_real_sfc_station_2022.py
"""
