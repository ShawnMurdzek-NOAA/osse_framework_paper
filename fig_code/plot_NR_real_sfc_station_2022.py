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

# Option to plot difference histogram
diff = True

# Output file name (include %s placeholder for plot type)
out_fname = '../figs/PNGs/SfcStationComparison%s_2022.png'


#---------------------------------------------------------------------------------------------------
# Make Plots
#---------------------------------------------------------------------------------------------------

# Read in pickled data
with open(pickle_fname, 'rb') as handle:
    all_data = pickle.load(handle)

# Define variables and labels
data_vars = ['TOB', 'QOB', 'POB', 'UOB', 'VOB']
labels = {'TOB':'Temperature ($^{\circ}$C)',
          'QOB':'Specific Humidity (g kg$^{-1}$)',
          'POB':'Pressure (hPa)',
          'UOB':'U Wind (m s$^{-1}$)',
          'VOB':'V Wind (m s$^{-1}$)'}
sub_labels = ['a)', 'b)', 'c)', 'd)', 'e)']

# Parse data into 1D arrays for easier plotting
real_data = {}
fake_data = {}
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

# Convert QOB to g/kg
real_data['QOB'] = real_data['QOB'] * 1e-3
fake_data['QOB'] = fake_data['QOB'] * 1e-3

# Make histogram and scatterplots
fig_hist, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 6))
fig_scat, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 6))
for i, d in enumerate(data_vars):

    minval = min([np.nanmin(real_data[d]), np.nanmin(fake_data[d])])
    maxval = max([np.nanmax(real_data[d]), np.nanmax(fake_data[d])])

    # Histogram
    ax_hist = fig_hist.axes[i]
    if diff:
        ob_diff = fake_data[d] - real_data[d]
        ax_hist.hist(ob_diff, bins=40, color='dodgerblue', edgecolor='k',
                     range=(np.nanpercentile(ob_diff, 0.5), np.nanpercentile(ob_diff, 99.5)))
        ax_hist.set_xlabel(labels[d], size=12)
    else:
        real_hist = np.histogram(real_data[d], bins=25, range=(0.94*minval, 1.06*maxval))
        fake_hist = np.histogram(fake_data[d], bins=25, range=(0.94*minval, 1.06*maxval))
        bins = 0.5 * (real_hist[1][1:] + real_hist[1][:-1])
        ax_hist.plot(bins, real_hist[0], 'r-', lw=2.5, label='real data')
        ax_hist.plot(bins, fake_hist[0], 'b--', lw=2.5, label='synthetic data')
        ax_hist.set_xlabel(d, size=12)
    ax_hist.text(0.03, 0.92, sub_labels[i], size=12, fontweight='bold', transform=ax_hist.transAxes)

    # Scatterplot
    ax_scat = fig_scat.axes[i]
    ax_scat.scatter(real_data[d], fake_data[d], s=2, color='b')
    ax_scat.plot([minval, maxval], [minval, maxval], 'k--')
    ax_scat.set_xlabel('real data', size=12)
    ax_scat.set_ylabel('synthetic data', size=12)
    ax_scat.set_title(f"{sub_labels[i]} {labels[d]}", size=16)
    ax_scat.grid()

plt.figure(fig_hist.number)
fig_hist.axes[-1].axis('off')
for i in [0, 3]:
    fig_hist.axes[i].set_ylabel('counts', size=12)
if not diff: fig_hist.axes[2].legend()
plt.subplots_adjust(left=0.08, bottom=0.1, right=0.98, top=0.92, hspace=0.3, wspace=0.25)
plt.suptitle('Winter 2022 Surface Station Differences (synthetic $-$ real)', size=16)
plt.savefig(out_fname % 'Hist')

plt.figure(fig_scat.number)
fig_scat.axes[-1].axis('off')
plt.subplots_adjust(left=0.07, bottom=0.07, right=0.97, top=0.94, hspace=0.25, wspace=0.3)
plt.savefig(out_fname % 'Scat')


"""
End plot_NR_real_sfc_station_2022.py
"""
