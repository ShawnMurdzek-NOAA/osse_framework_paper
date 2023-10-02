"""
Frequency Histograms Comparing the Nature Run to Observed MRMS Output

This script uses "extracted" netCDF files created by extract_wrfnat_fields.py

6-hr precip amounts are computed by ../misc/compute_precip6hr.py

shawn.s.murdzek@noaa.gov
Date Created: 8 March 2023
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import datetime as dt
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys
import pickle


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input pickle files
parent_dir = '/work2/noaa/wrfruc/murdzek/src/py_scripts/NR_eval'
pickle_winter_fname = parent_dir + '/NR_precip6hr_all_winter.pkl'
pickle_spring_fname = parent_dir + '/NR_precip6hr_all_spring.pkl'

# Times to evaluate (strings, HHMM)
eval_times = ['0000', '1200']

# Output file
out_file = '../figs/NRvsMRMSprecip6hr.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data
#---------------------------------------------------------------------------------------------------

start_time = dt.datetime.now()

# Read in pickled data
all_data = {}
for season, pkl in zip(['winter', 'spring'], [pickle_winter_fname, pickle_spring_fname]):
    with open(pkl, 'rb') as handle:
        all_data[season] = pickle.load(handle)

bins = np.arange(1, 200, 5) # DO NOT CHANGE! This is unique for the pickle file.


#---------------------------------------------------------------------------------------------------   
# Plot results
#---------------------------------------------------------------------------------------------------

fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(8, 6))
plt.subplots_adjust(left=0.09, bottom=0.09, right=0.98, top=0.88, hspace=0.2, wspace=0.05)
bin_ctrs = bins[:-1] + 0.5 * (bins[1] - bins[0])
panel_labels = ['a)', 'b)', 'c)', 'd)']

for i, season in enumerate(['winter', 'spring']):
    for j, t in enumerate(eval_times):
        ax = axes[i, j]

        ax.plot(bin_ctrs, all_data[season]['NR_total_counts'][t] / all_data[season]['NR_total_pts'][t], 
                'b-', linewidth=2.5, label='NR') 

        MRMS_freq_pct = {}
        for pct in [0, 10, 25, 50, 75, 90, 100]:
            MRMS_freq_pct[pct] = np.nanpercentile(all_data[season]['MRMS_freq'][t], pct, axis=1)
    
        #ax.plot(bin_ctrs, MRMS_freq_pct[50], 'r-', linewidth=2.5)
        ax.fill_between(bin_ctrs, MRMS_freq_pct[25], MRMS_freq_pct[75], color='r', alpha=0.35, label='MRMS')
        #ax.fill_between(bin_ctrs, MRMS_freq_pct[10], MRMS_freq_pct[90], color='r', alpha=0.15)
        ax.fill_between(bin_ctrs, MRMS_freq_pct[0], MRMS_freq_pct[100], color='r', alpha=0.15)
        ax.plot(bin_ctrs, MRMS_freq_pct[0], 'r-', linewidth=0.25)
        ax.plot(bin_ctrs, MRMS_freq_pct[100], 'r-', linewidth=0.25)
 
        ax.set_title('%s %s, %s UTC' % (panel_labels[2*i+j], season, t), size=16)
        ax.set_yscale('log')
        ax.set_xlim([0, 80])
        ax.set_ylim([1e-7, 0.1])
        #ax.set_xticks(bin_ctrs)
        ax.grid() 

axes[0, 0].legend(fontsize=14)

for i in range(2):
    axes[-1, i].set_xlabel(all_data['winter']['xlabel'], size=14)
for i in range(2):
    axes[i, 0].set_ylabel('fraction of gridpoints', size=14)

plt.suptitle('6-hr Precipitation Histograms', size=20)
plt.savefig(out_file)
plt.close()

print('elapsed time = %.2f min' % ((dt.datetime.now() - start_time).total_seconds() / 60))


"""
End plot_freq_hist_NR_MRMS.py
"""