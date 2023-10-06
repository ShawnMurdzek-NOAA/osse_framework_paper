"""
Plot Observation Differences Between Two Prepbufr CSV

This script should ideally be used to compare synthetic obs vs. real obs

Optional command-line arguments:
    argv[1] = Prepbufr file tag
    argv[2] = BUFR time in YYYYMMDDHHMM format
    argv[3] = YAML file with program parameters

shawn.s.murdzek@noaa.gov
Date Created: 14 February 2023
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import datetime as dt
import pandas as pd
import metpy.calc as mc
from metpy.units import units
import sys

import pyDA_utils.bufr as bufr


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input BUFR CSV directories
bufr_dirs = ['/work2/noaa/wrfruc/murdzek/nature_run_winter/obs/perfect_conv/perfect_csv/',
             '/work2/noaa/wrfruc/murdzek/nature_run_spring/obs/perfect_conv/perfect_csv/']

# Prepbufr file tag (e.g., 'rap', 'rap_e', 'rap_p')
bufr_tag = 'rap'

# Range of datetimes to use for the comparison (one for each entry in bufr_dirs)
date_range = [[dt.datetime(2022, 2, 1, 0) + dt.timedelta(hours=i) for i in range(12)],
              [dt.datetime(2022, 4, 29, 12) + dt.timedelta(hours=i) for i in range(12)]]

# Plotting parameters. List of dictionaries (each dictionary is for a separate plot) with the 
# following keys...
#     save_fname: Output file name (include %s placeholders for bufr_tag and start and end dates)
#     subsets: Observation subsets
#     obs_vars: Variables to plot
#     vcoord: Vertical coordinate (POB or ZOB)
plot_param = [{'save_fname':'../figs/ObDiffs3D.pdf',
               'subsets':['AIRCFT', 'AIRCAR', 'ADPUPA'],
               'obs_vars':['TOB', 'QOB', 'WSPD', 'WDIR'],
               'vcoord':'POB'}]

# SIDs to exclude.
# Some aircraft have bad temperature data (e.g., T < -50 degC below 500 hPa), but TQM < 2, so
# the values are still plotted
exclude_sid = ['00000775']
#exclude_sid = []


#---------------------------------------------------------------------------------------------------
# Plot BUFR Observation Differences
#---------------------------------------------------------------------------------------------------

# Dictionary giving quality marker fields for each variable (only plot quality markers 0-2)
qm = {'POB':'PQM',
      'QOB':'QQM',
      'TOB':'TQM',
      'ZOB':'ZQM',
      'UOB':'WQM',
      'VOB':'WQM',
      'PWO':'PWQ',
      'WSPD':'WQM',
      'WDIR':'WQM',
      'TDO':'QQM'}

# Open files
real_ob_dfs = []
sim_ob_dfs = []
for b_dir, dr in zip(bufr_dirs, date_range):
    for d in dr:
        date_str = d.strftime('%Y%m%d%H%M')
        try:
            real_bufr_csv = bufr.bufrCSV('%s/%s.%s.real_red.prepbufr.csv' % (b_dir, date_str, bufr_tag))
        except FileNotFoundError:
            # Skip to next file
            continue
        real_ob_dfs.append(real_bufr_csv.df)
        sim_bufr_csv = bufr.bufrCSV('%s/%s.%s.fake.prepbufr.csv' % (b_dir, date_str, bufr_tag))
        sim_ob_dfs.append(sim_bufr_csv.df)
        meta = sim_bufr_csv.meta
bufr_df_real = pd.concat(real_ob_dfs, ignore_index=True)
bufr_df_sim = pd.concat(sim_ob_dfs, ignore_index=True)

# Remove excluded SIDs
for s in exclude_sid:
    bufr_df_real = bufr_df_real.loc[bufr_df_real['SID'] != s]
    bufr_df_sim = bufr_df_sim.loc[bufr_df_sim['SID'] != s]

# Only retain obs with DHR between 0 and -1 to prevent double-counting
bufr_df_real = bufr_df_real.loc[np.logical_and(bufr_df_real['DHR'] > -1, bufr_df_real['DHR'] <= 0)]
bufr_df_sim = bufr_df_sim.loc[np.logical_and(bufr_df_sim['DHR'] > -1, bufr_df_sim['DHR'] <= 0)]

bufr_df_real.reset_index(inplace=True)
bufr_df_sim.reset_index(inplace=True)

# Match precision of BUFR files
bufr_df_sim = bufr.match_bufr_prec(bufr_df_sim)

# Compute wind speed and direction from U and V components
bufr_df_sim = bufr.compute_wspd_wdir(bufr_df_sim)
bufr_df_real = bufr.compute_wspd_wdir(bufr_df_real)


#---------------------------------------------------------------------------------------------------
# Create Plots
#---------------------------------------------------------------------------------------------------

vnames = {'POB':'Pressure \n(hPa)',
          'TOB':'Temperature \n(K)',
          'QOB':'Specific Humidity \n(mg kg$^{-1}$)',
          'WDIR':'Wind \nDirection ($^{\circ}$)',
          'WSPD':'Wind \nSpeed (m s$^{-1}$)',
          'PWO':'Precipitable Water (mm)'}

dbins = {'TOB':np.linspace(-5, 5, 31),
          'QOB':np.linspace(-4000, 4000, 31),
          'WDIR':np.linspace(-180, 180, 31),
          'WSPD':np.linspace(-9, 9, 31)}

letters = ['a', 'b', 'c', 'd']

for param in plot_param:

    print()
    print('Making plot for', param['subsets'])

    # Bins for vertical plotting. First entry is left-most edge whereas all subsequent entries are 
    # the right edge of the bin. POB is in mb and ZOB is in m
    if param['vcoord'] == 'POB': vbins = np.arange(1050, 95, -10)
    elif param['vcoord'] == 'ZOB': vbins = np.arange(0, 10000, 100)

    # Only retain obs from desired subset
    boo = np.zeros(len(bufr_df_sim))
    for s in param['subsets']:
        boo[bufr_df_sim['subset'] == s] = 1
    ind = np.where(boo)
    subset_sim = bufr_df_sim.loc[ind].copy()
    subset_real = bufr_df_real.loc[ind].copy()

    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(8, 5), sharey=True)
    plt.subplots_adjust(left=0.1, bottom=0.14, right=1.05, top=0.92, hspace=0.4, wspace=0.1)
    for i, v in enumerate(param['obs_vars']):
        print('Plotting %s' % v)
        ax = axes[i]

        # Only plot if the quality marker is <= 2
        if v in qm.keys():
            cond = np.logical_and(subset_sim[qm[v]] <= 2, subset_real[qm[v]] <= 2)
            diff = subset_sim.loc[cond, v] - subset_real.loc[cond, v]
            if param['vcoord'] == 'POB': vert = subset_sim.loc[cond, 'POB'].values
            elif param['vcoord'] == 'ZOB': vert = subset_sim.loc[cond, 'ZOB'].values
            if v == 'WDIR':
                ind_fix = np.logical_or(diff > 180, diff < -180)
                diff[diff > 180] = diff[diff > 180] - 360.
                diff[diff < -180] = 360. + diff[diff < -180]
        else:
            diff = subset_sim[v] - subset_real[v]
            if param['vcoord'] == 'POB': vert = subset_sim.loc[cond, 'POB'].values
            elif param['vcoord'] == 'ZOB': vert = subset_sim.loc[cond, 'ZOB'].values
    
        # Plot differences using a 2D histogram
        nhist = len(vbins) - 1
        diff_hist = np.zeros([len(dbins[v])-1, nhist])
        for j in range(nhist):
            binned_diff = diff[np.logical_and(vert <= vbins[j:(j+2)].max(), 
                               vert > vbins[j:(j+2)].min())]
            diff_hist[:, j] = np.histogram(binned_diff, bins=dbins[v])[0]
        if param['vcoord'] == 'POB': vbin_ctr = np.log10(vbins[:-1] + (0.5 * (vbins[1:] - vbins[:-1])))
        elif param['vcoord'] == 'ZOB': vbin_ctr = vbins[:-1] + (0.5 * (vbins[1:] - vbins[:-1]))
        vbin_ctr_2d, dbin_ctr_2d = np.meshgrid(vbin_ctr, 0.5*(dbins[v][1:] + dbins[v][:-1]))
        cax = ax.pcolormesh(dbin_ctr_2d, vbin_ctr_2d, diff_hist, cmap='Reds', 
                            norm=colors.LogNorm(vmin=1, vmax=2000))
        print(np.nanmax(diff_hist))       
 
        ax.grid()

        if param['vcoord'] == 'POB':
            ax.set_ylim([np.log10(vbins.max()), np.log10(150)])
            ticks = np.array([1000, 850, 700, 500, 400, 300, 200])
            ax.set_yticks(np.log10(ticks))
            ax.set_yticklabels(ticks)
        elif param['vcoord'] == 'ZOB':
            ax.set_ylim([vbins.min(), vbins.max()])
        ax.set_xlabel(vnames[v], size=12)
        ax.text(0.9*np.amin(dbins[v]), np.log10(167), '%s)' % letters[i], size=12, weight='bold',
                backgroundcolor='white')

    axes[0].set_ylabel('pressure (hPa)', size=12)

    cbar = plt.colorbar(cax, ax=axes, orientation='vertical', pad=0.01, aspect=30, extend='max')
    cbar.set_label('counts', size=12)

    plt.suptitle("Differences: Synthetic $-$ Real", size=18)
    plt.savefig(param['save_fname'])
    plt.close()


"""
End plot_ob_diffs_vprof.py  
"""
