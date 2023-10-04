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
import seaborn as sns


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input pickle files
parent_dir = '/work2/noaa/wrfruc/murdzek/src/py_scripts/NR_eval'
pickle_winter_fname = parent_dir + '/sfc_station_compare_winter.pkl'
pickle_spring_fname = parent_dir + '/sfc_station_compare_spring.pkl'

# Parameters for real obs
with open('station_list.txt', 'r') as fptr:
    station_ids = fptr.readlines()
    for i in range(len(station_ids)):
        station_ids[i] = station_ids[i].strip()
years = np.arange(1993, 2023)

# Parameters for fake obs
# analysis_times are dt.timedelta objects relative to 0000
analysis_times = [dt.timedelta(hours=i) for i in range(24)]

# Output file name (include %s placeholder for season)
out_fname = '../figs/SfcStationComparison%s.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data
#---------------------------------------------------------------------------------------------------

# Read in pickled data
all_data = {}
for season, pkl in zip(['Winter', 'Spring'], [pickle_winter_fname, pickle_spring_fname]):
    with open(pkl, 'rb') as handle:
        all_data[season] = pickle.load(handle)

zcutoff = 2


#---------------------------------------------------------------------------------------------------
# Plot results
#---------------------------------------------------------------------------------------------------

labels = ['a', 'b', 'c', 'd', 'e', 'f']
var_names = {'TOB':'Temperature', 'QOB':'Specific Humidity', 'POB':'Pressure', 
             'UOB':'U Wind Component', 'VOB':'V Wind Component'}

for season in ['Winter', 'Spring']:

    plot_hr = np.array([t.total_seconds() / 3600. for t in all_data[season]['analysis_times']])
    ntimes = len(all_data[season]['analysis_times'])
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(10, 6))
    #plt.subplots_adjust(left=0.06, bottom=0.08, right=1.08, top=0.88, wspace=0.22, hspace=0.3)
    plt.subplots_adjust(left=0.06, bottom=0.09, right=0.98, top=0.88, wspace=0.2, hspace=0.3)
    ttest_pvalues = {}

    for i, v in enumerate(['TOB', 'QOB', 'POB', 'UOB', 'VOB']):
        ax = axes[int(i/3), i%3]
        if i > 0:
            ax.sharex(axes[0, 0])
            ax.sharey(axes[0, 0])
        
        # Plot standardized anomalies using percentiles
        pcts = [0, 2, 25, 50, 75, 98, 100, 'mean']
        var_percentiles = {}
        for p in pcts:
            var_percentiles[p] = np.zeros(ntimes)
            if p == 'mean':
                for l in range(ntimes):
                    var_percentiles[p][l] = np.nanmean(all_data[season]['all_zscores'][v][:, l]) 
            else:
                for l in range(ntimes):
                    var_percentiles[p][l] = np.nanpercentile(all_data[season]['all_zscores'][v][:, l], p) 
        
        ax.plot(plot_hr, var_percentiles['mean'], 'r-', lw=2)
        ax.fill_between(plot_hr, var_percentiles[25], var_percentiles[75], color='r', alpha=0.4)
        ax.fill_between(plot_hr, var_percentiles[0], var_percentiles[100], color='r', alpha=0.2)
        ax.plot(plot_hr, var_percentiles[0], 'r-', lw=0.25)
        ax.plot(plot_hr, var_percentiles[100], 'r-', lw=0.25)

        # Plot standardized anomalies using histograms
        #bins = np.arange(-3, 3.01, 0.2)
        #bin_ctr = (bins[:-1] + bins[1:]) / 2
        #nhist = all_data[season]['all_zscores'][v].shape[-1]
        #zscore_hist = np.zeros([nhist, len(bins) - 1])
        #for j in range(nhist):
        #    zscore_hist[j, :] = np.histogram(all_data[season]['all_zscores'][v][:, j], bins=bins)[0] 
        #bin_ctr_2d, plot_hr_2d = np.meshgrid(bin_ctr, plot_hr)
        #cax = ax.pcolormesh(plot_hr_2d, bin_ctr_2d, zscore_hist, cmap='Reds', vmin=0, vmax=60)

        # Perform t test
        ttest_pvalues[v[0]] = np.zeros(len(plot_hr))
        for j in range(len(plot_hr)):
            ttest_pvalues[v[0]][j] = ss.ttest_1samp(all_data[season]['all_zscores'][v][:, j], 0,
                                                    nan_policy='omit')[1]

        ax.grid()
        #ax.axhline(zcutoff, c='r', ls='-', lw=1.5)
        #ax.axhline(-zcutoff, c='r', ls='-', lw=1.5)
        ax.axhline(0, c='k', lw=1.5)
        ax.set_title('%s) %s' % (labels[i], var_names[v]), size=16)
        ax.set_xlim([plot_hr.min(), plot_hr.max()])
        ax.set_ylim([-4, 4])

    for i in range(2):
        axes[-1, i].set_xlabel('hour', size=14)
        axes[i, 0].set_ylabel('standardized anomaly', size=14)
    #axes[0, 2].set_xlabel('hour', size=14)
    
    # Add heatmap to sixth axis
    #axes[1, 2].set_axis_off()
    ax = axes[1, 2]
    ttest_df = pd.DataFrame(ttest_pvalues)
    sns.heatmap(ttest_df.T, cbar=True, ax=ax, vmin=0, vmax=0.1, cmap='Blues_r', linecolor='k', 
                linewidths=0.1, cbar_kws={'orientation':'vertical', 'pad':0.02})
    ax.set_title('f) $t$ test $p$-values', size=16)
    ax.set_xlabel('hour', size=14)
    ax.set_ylabel('variable', size=14)
    ax.set_xticks(np.arange(0.5, 24, 5), labels=['%d' % i for i in range(0, 24, 5)])

    #cbar = plt.colorbar(cax, ax=axes, orientation='vertical', aspect=25, pad=0.02)
    #cbar.set_label('counts', size=14)
    plt.suptitle('Surface Station Comparison: %s' % season, size=18)
    plt.savefig(out_fname % season)
    plt.close()


"""
End compare_NR_real_sfc_stations.py
"""
