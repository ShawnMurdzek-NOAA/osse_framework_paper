"""
Plot Observation Differences Between Two Prepbufr CSV

This script should ideally be used to compare synthetic obs vs. real obs

Optional command-line arguments:
    argv[1] = Prepbufr file tag
    argv[2] = BUFR time in YYYYMMDDHHMM format
    argv[3] = YAML file with program parameters

shawn.s.murdzek@noaa.gov
Date Created: 7 February 2023
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import pandas as pd
import xarray as xr
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

# Dataset names
name1 = 'Sim Obs'
name2 = 'Real Obs'

# Option to perform an elevation adjustment for P and T
elv_adjust_prs = True
elv_adjust_T = True

# Output file name
save_fname = '../figs/ObDiffs2D.pdf'

# Observation subsets
subsets = ['SFCSHP', 'ADPSFC', 'MSONET', 'GPSIPW']

# Variables to plot
obs_vars = ['TOB', 'QOB', 'POB', 'WDIR', 'WSPD', 'PWO']

# Domain to examine ('all', 'easternUS', 'westernUS')
domain = 'all'


#---------------------------------------------------------------------------------------------------
# Read in Data
#---------------------------------------------------------------------------------------------------

# Dictionary giving quality marker fields for each variable (only plot quality markers 0-2)
qm = {'POB':'PQM',
      'QOB':'QQM',
      'TOB':'TQM',
      'ZOB':'ZQM',
      'UOB':'WQM',
      'VOB':'WQM',
      'PWO':'PWQ',
      'WDIR':'WQM',
      'WSPD':'WQM'}

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
print('Done opening files')

# Only retain obs with DHR between 0 and -1 to prevent double-counting
# UNLESS ob is from GPSIPW, in which case keep all obs b/c DHR is always -1 for these obs
bufr_df_real = bufr_df_real.loc[np.logical_or(np.logical_and(bufr_df_real['DHR'] > -1, bufr_df_real['DHR'] <= 0),
                                              bufr_df_real['subset'] == 'GPSIPW')]
bufr_df_sim = bufr_df_sim.loc[np.logical_or(np.logical_and(bufr_df_sim['DHR'] > -1, bufr_df_sim['DHR'] <= 0),
                                            bufr_df_sim['subset'] == 'GPSIPW')]

bufr_df_real.reset_index(inplace=True, drop=True)
bufr_df_sim.reset_index(inplace=True, drop=True)

# Only retain obs from desired subset
boo = np.zeros(len(bufr_df_sim))
for s in subsets:
    boo[bufr_df_sim['subset'] == s] = 1
ind = np.where(boo)
bufr_df_sim = bufr_df_sim.loc[ind]
bufr_df_real = bufr_df_real.loc[ind]

# Only retain obs from desired domain
if domain == 'easternUS':
    bufr_df_real = bufr_df_real.loc[bufr_df_real['XOB'] >= 260]
    bufr_df_sim = bufr_df_sim.loc[bufr_df_sim['XOB'] >= 260]
elif domain == 'westernUS':
    bufr_df_real = bufr_df_real.loc[bufr_df_real['XOB'] < 260]
    bufr_df_sim = bufr_df_sim.loc[bufr_df_sim['XOB'] < 260]

bufr_df_real.reset_index(inplace=True, drop=True)
bufr_df_sim.reset_index(inplace=True, drop=True)
print('Done subsetting obs')

# Perform pressure and temperature adjustment
g = 9.81
Rd = 287.04
lr = 0.0065  # Based on US Standard Atmosphere, see Part 4, Table I from https://ntrs.nasa.gov/citations/19770009539
if elv_adjust_prs or elv_adjust_T:
    elv_diff = bufr_df_real['ELV'].values - bufr_df_sim['ELV'].values
    Tind = np.where(~np.isnan(bufr_df_sim['TOB']))[0]
    if elv_adjust_prs:
        # Use hydrostatic balance for the adjustment
        bufr_df_sim['POB_original'] = bufr_df_sim['POB'].copy()
        bufr_df_sim.loc[Tind, 'POB'] = (bufr_df_sim['POB'][Tind] *
                                        np.exp(-g * elv_diff[Tind] / (Rd * (bufr_df_sim['TOB'][Tind] + 273.15))))
    if elv_adjust_T:
        # Adjust based on a specified lapse rate
        bufr_df_sim['TOB_original'] = bufr_df_sim['TOB'].copy()
        bufr_df_sim.loc[Tind, 'TOB'] = bufr_df_sim['TOB'][Tind] - (lr * elv_diff[Tind])
    print('Done performing prs and/or T adjustment')

# Apply rounding so precision in simulated obs matches real obs
bufr_df_sim = bufr.match_bufr_prec(bufr_df_sim)
print('Done adjusting precision')

# Compute wind speed and direction from U and V components
bufr_df_sim = bufr.compute_wspd_wdir(bufr_df_sim)
bufr_df_real = bufr.compute_wspd_wdir(bufr_df_real)
print('Done computing WSPD and WDIR')


#---------------------------------------------------------------------------------------------------
# Create Plot
#---------------------------------------------------------------------------------------------------

# Dictionary with full variable names
vnames = {'POB':'Pressure (hPa)',
          'TOB':'Temperature (K)',
          'QOB':'Specific Humidity (mg kg$^{-1}$)',
          'WDIR':'Wind Direction ($^{\circ}$)',
          'WSPD':'Wind Speed (m s$^{-1}$)',
          'PWO':'Precipitable Water (mm)'}

nbins = {'POB':30,
         'TOB':25,
         'QOB':30,
         'WDIR':30,
         'WSPD':30,
         'PWO':24}

rng = {'POB':(-12, 12),
       'TOB':(-5, 5),
       'QOB':(-4000, 4000),
       'WDIR':(-180, 180),
       'WSPD':(-9, 9),
       'PWO':(-6, 6)}

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(9, 6))
plt.subplots_adjust(left=0.1, bottom=0.09, right=0.98, top=0.91, hspace=0.3, wspace=0.45)

letters = ['a', 'b', 'c', 'd', 'e', 'f']
for i, (v, l) in enumerate(zip(obs_vars, letters)):
    print('Plotting %s' % v)

    ax = axes[int(i/3), i%3]

    # Only plot if the quality marker is <= 2
    if v in qm.keys():
        cond = np.logical_and(bufr_df_sim[qm[v]] <= 2, bufr_df_real[qm[v]] <= 2)
        field1 = bufr_df_sim.loc[cond, v]
        field2 = bufr_df_real.loc[cond, v]
        diff = (field1 - field2).values
        if v == 'WDIR':
            ind_fix = np.logical_or(diff > 180, diff < -180)
            diff[diff > 180] = diff[diff > 180] - 360.
            diff[diff < -180] = 360. + diff[diff < -180]
    else:
        field1 = bufr_df_sim[v]
        field2 = bufr_df_real[v]
        diff = (field1 - field2).values

    # Skip this variable if there is no data
    if len(field1) == 0:
        continue

    # Plot differences
    dlim = np.nanpercentile(np.abs(diff), 99)
    hist_out = ax.hist(diff, bins=nbins[v], range=rng[v], lw=0.3, edgecolor='k')
    ax.set_xlabel(vnames[v], size=13)
    ax.set_ylabel('counts', size=13)
    ax.grid()
    ax.text(rng[v][0], 0.95*np.amax(hist_out[0]), '%s)' % l, size=11, fontweight='bold', 
            backgroundcolor='white')

#for i in range(2):
#    axes[i, 0].set_ylabel('counts', size=12)
plt.suptitle('Differences: Synthetic $-$ Real', size=20)
plt.savefig(save_fname)
plt.close()


"""
End plot_ob_diffs_2d.py  
"""
