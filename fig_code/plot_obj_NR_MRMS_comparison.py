"""
Object-Based Comparison of MRMS and NR Composite Reflectivity Objects 

This plotting script uses output from py_scripts/NR_eval/frequency_histograms.py

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input pickle files
parent_dir = '/work2/noaa/wrfruc/murdzek/src/py_scripts/NR_eval'
pickle_winter_fname = parent_dir + '/NR_cref_obj_30dbz_9minsize_all_winter.pkl'
pickle_spring_fname = parent_dir + '/NR_cref_obj_30dbz_9minsize_all_spring.pkl'

# Evaluation time (UTC)
eval_time = '0000'

# Output file
out_file = '../figs/NRvsMRMSobjRef.pdf'


#---------------------------------------------------------------------------------------------------
# Extract Data
#---------------------------------------------------------------------------------------------------

start_time = dt.datetime.now()

# Read in pickled data
all_obj = {}
for season, pkl in zip(['winter', 'spring'], [pickle_winter_fname, pickle_spring_fname]):
    with open(pkl, 'rb') as handle:
        all_obj[season] = pickle.load(handle)

min_size = all_obj['winter']['min_size']
ref_thres = all_obj['winter']['ref_thres']


#---------------------------------------------------------------------------------------------------
# Create Plots
#---------------------------------------------------------------------------------------------------

print()
print('Making plots...')

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 5), sharex='col', sharey='col')
plt.subplots_adjust(left=0.05, bottom=0.13, right=0.98, top=0.9, hspace=0.1, wspace=0.37)
labelsize = 14

panel_labels = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)']
for i, season in enumerate(['winter', 'spring']):

    # First subplot: Number of objects
    ax = axes[i, 0]
    nobj_MRMS = [len(sublist) for sublist in all_obj[season]['MRMS_obj'][eval_time]['size']]
    bplot = ax.boxplot(nobj_MRMS, vert=False, patch_artist=True, medianprops=dict(color='black'),
                       boxprops=dict(facecolor=[1,0,0,0.35]))
    ax.plot(len(all_obj[season]['NR_obj'][eval_time]['size']), 1, 'b*', markersize=20)
    ax.grid(axis='x')
    ax.yaxis.set_tick_params(labelleft=False)
    ax.set_yticks([])
    ax.set_ylabel(season, size=18)
    ax.set_ylim([0.85, 1.15])
    ax.text(4900, 1.12, panel_labels[3*i], size=14, fontweight='bold')

    # Second and third subplots: Histograms
    for j, (var, bins, xscale, xlim) in enumerate(zip(['size', 'max_dbz'], 
                                                      [np.linspace(min_size, 1000, 200), np.arange(ref_thres, 85, 5)],
                                                      ['log', 'linear'],
                                                      [[9, 500], [30, 75]])):
        ax = axes[i, j+1]
        bin_ctrs = 0.5 * (bins[1:] + bins[:-1])

        NR_fraction = (np.histogram(all_obj[season]['NR_obj'][eval_time][var], bins=bins)[0] / 
                       len(all_obj[season]['NR_obj'][eval_time][var])) 
        ax.plot(bin_ctrs, NR_fraction, 'b-', linewidth=2)

        MRMS_fraction = np.zeros([all_obj[season]['nMRMS'], len(bin_ctrs)])
        for k in range(all_obj[season]['nMRMS']):
            MRMS_fraction[k, :] = (np.histogram(all_obj[season]['MRMS_obj'][eval_time][var][k], bins=bins)[0] / 
                                   len(all_obj[season]['MRMS_obj'][eval_time][var][k]))
        MRMS_frac_pct = {}
        for pct in [0, 10, 25, 50, 75, 90, 100]:
            MRMS_frac_pct[pct] = np.nanpercentile(MRMS_fraction, pct, axis=0)
        #ax.plot(bin_ctrs, MRMS_frac_pct[50], 'r-', linewidth=2.5)
        ax.fill_between(bin_ctrs, MRMS_frac_pct[25], MRMS_frac_pct[75], color='r', alpha=0.35)
        #ax.fill_between(bin_ctrs, MRMS_frac_pct[10], MRMS_frac_pct[90], color='r', alpha=0.15)
        ax.fill_between(bin_ctrs, MRMS_frac_pct[0], MRMS_frac_pct[100], color='r', alpha=0.15)
        ax.plot(bin_ctrs, MRMS_frac_pct[0], 'r-', linewidth=0.25)
        ax.plot(bin_ctrs, MRMS_frac_pct[100], 'r-', linewidth=0.25)

        ax.set_xscale(xscale)
        ax.set_xlim(xlim)
        ax.set_yscale('log')
        ax.set_ylim([0.001, 1])
        ax.grid()
        if var == 'size':
            ax.text(300, 0.5, panel_labels[3*i+j+1], size=14, fontweight='bold')
        elif var == 'max_dbz':
            ax.text(70, 0.5, panel_labels[3*i+j+1], size=14, fontweight='bold')

        # Only set y-axis labels for the object size plots
        if var == 'size':
            ax.set_ylabel('fraction', size=labelsize)
        else:
            ax.set_ylabel('fraction', size=labelsize)
            #ax.yaxis.set_tick_params(labelleft=False)   

# Adjust left edge of x-axis for histograms. Do this last w/ the spring period, otherwise the
# right edge is not set far enough to the right
axes[1, 0].set_xlim(left=0)

for i, xlabel in enumerate(['number of objects', 'object size (grid boxes)', 
                           'max reflectivity (dB$Z$)']):
    axes[-1, i].set_xlabel(xlabel, size=labelsize)

plt.suptitle('Reflectivity Objects: %s UTC' % eval_time, size=18)
plt.savefig(out_file)
plt.close()

print('elapsed time = %.2f min' % ((dt.datetime.now() - start_time).total_seconds() / 60))


"""
End plot_obj_NR_MRMS_comparison.py
"""
