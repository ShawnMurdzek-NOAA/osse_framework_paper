"""
Perform Comparisons Between Real and Simulated Surface Station Observations

Real surface station obs come from the Iowa Environmental Mesonet database:
https://mesonet.agron.iastate.edu/request/download.phtml

This script uses "perfect" station matching. This means that the NR output WAS intentionally
interpolated to the real surface stations used for comparison here.

shawn.s.murdzek@noaa.gov
Date Created: 11 April 2023
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

# Input pickle files
parent_dir = '/work2/noaa/wrfruc/murdzek/src/py_scripts/NR_eval'
pickle_winter_fname = parent_dir + '/sfc_station_compare_winter.pkl'
pickle_spring_fname = parent_dir + '/sfc_station_compare_spring.pkl'

# Parameters for real obs
real_obs_dir = '/work2/noaa/wrfruc/murdzek/real_obs/sfc_stations/winter'
with open('station_list.txt', 'r') as fptr:
    station_ids = fptr.readlines()
    for i in range(len(station_ids)):
        station_ids[i] = station_ids[i].strip()
years = np.arange(1993, 2023)
#startdate = '04290000'
#enddate = '05070000'
startdate = '02010000'
enddate = '02080000'

# Parameters for fake obs
# analysis_times are dt.timedelta objects relative to 0000
fake_obs_dir = '/work2/noaa/wrfruc/murdzek/nature_run_winter/obs/eval_sfc_station/perfect_conv/'
#analysis_days = [dt.datetime(2022, 4, 29) + dt.timedelta(days=i) for i in range(8)]
analysis_days = [dt.datetime(2022, 2, 1) + dt.timedelta(days=i) for i in range(7)]
analysis_times = [dt.timedelta(hours=i) for i in range(24)]

# Maximum time allowed between analysis_times and either the real or fake ob (sec)
max_time_allowed = 450.

# Option to plot ceiling obs as a binary histogram ('binary') or CDF of ceiling height ('hgt')
ceil_plot = 'hgt'

# Type of z-score to use for z-score plots ('regular' or 'modified')
# Also select cutoff value that denotes outliers
zscore = 'regular'
zcutoff = 2

# Output file name (include %s placeholder for season)
out_fname = '../figs/SfcStationComparison%s.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data
#---------------------------------------------------------------------------------------------------

# Read in pickled data
all_data = {}
#for season, pkl in zip(['Winter', 'Spring'], [pickle_winter_fname, pickle_spring_fname]):
for season, pkl in zip(['Winter'], [pickle_winter_fname]):
    with open(pkl, 'rb') as handle:
        all_data[season] = pickle.load(handle)


#---------------------------------------------------------------------------------------------------
# Plot results
#---------------------------------------------------------------------------------------------------

for season in ['Winter']:

    plot_hr = np.array([t.total_seconds() / 3600. for t in all_data[season]['analysis_times']])
    ntimes = len(all_data[season]['analysis_times'])
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))
    plt.subplots_adjust(left=0.06, bottom=0.08, right=0.99, top=0.9, wspace=0.4)
    for i, v in enumerate(['TOB', 'QOB', 'POB', 'UOB', 'VOB']):
        ax = axes[int(i/3), i%3]
        
        pcts = [0, 10, 25, 50, 75, 90, 100]
        var_percentiles = {}
        for p in pcts:
            var_percentiles[p] = np.zeros(ntimes)
            for l in range(ntimes):
                var_percentiles[p][l] = np.nanpercentile(all_data[season]['all_zscores'][v][:, l], p) 
        
        ax.plot(plot_hr, var_percentiles[50], 'k-', lw=2)
        ax.fill_between(plot_hr, var_percentiles[25], var_percentiles[75], color='k', alpha=0.4)
        ax.fill_between(plot_hr, var_percentiles[10], var_percentiles[90], color='k', alpha=0.2)
        ax.plot(plot_hr, var_percentiles[0], 'k-', lw=0.5)
        ax.plot(plot_hr, var_percentiles[100], 'k-', lw=0.5)

        ax.grid()
        ax.axhline(zcutoff, c='r', ls='-', lw=1.5)
        ax.axhline(-zcutoff, c='r', ls='-', lw=1.5)
        ax.set_ylabel('%s standard anomaly' % v, size=14)
        ax.set_xlim([plot_hr.min(), plot_hr.max()])
    for i in range(3):
        if i != 3:
            axes[-1, i].set_xlabel('hour', size=14)
    plt.suptitle('Surface Station Comparison: %s' % season, size=18)
    plt.savefig(out_fname % season)
    plt.close()


"""
End compare_NR_real_sfc_stations.py
"""
