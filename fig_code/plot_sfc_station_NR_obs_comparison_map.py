"""
Perform Comparisons Between Real and Simulated Surface Station Observations on a Map

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
import cartopy.feature as cfeature
import cartopy.crs as ccrs


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input pickle files
parent_dir = '/work2/noaa/wrfruc/murdzek/src/py_scripts/NR_eval'
pickle_winter_fname = parent_dir + '/sfc_station_compare_winter.pkl'
pickle_spring_fname = parent_dir + '/sfc_station_compare_spring.pkl'

# Surface station information
with open('station_list.txt', 'r') as fptr:
    station_ids = fptr.readlines()
    for i in range(len(station_ids)):
        station_ids[i] = station_ids[i].strip()
sfc_station_sampl_path = '/work2/noaa/wrfruc/murdzek/real_obs/sfc_stations/spring'

# Significance level
sig_level = 0.05

# Output file name (with %s placeholder for the season)
out_fname = '../figs/SfcStationComparisonMap%s.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data
#---------------------------------------------------------------------------------------------------

# Read in pickled data
all_data = {}
for season, pkl in zip(['Winter', 'Spring'], [pickle_winter_fname, pickle_spring_fname]):
    with open(pkl, 'rb') as handle:
        all_data[season] = pickle.load(handle)

# Read in surface station locations
station_lat = np.zeros(len(station_ids))
station_lon = np.zeros(len(station_ids))
for i, s in enumerate(station_ids):
    df = pd.read_csv('%s/%s_202204290000_202205070000.txt' % (sfc_station_sampl_path, s), skiprows=5)
    station_lat[i] = df['lat'].loc[0]
    station_lon[i] = df['lon'].loc[0]


#---------------------------------------------------------------------------------------------------
# Plot results
#---------------------------------------------------------------------------------------------------

labels = ['a', 'b', 'c', 'd', 'e', 'f']
var_names = {'TOB':'Temperature', 'QOB':'Specific Humidity', 'POB':'Pressure',
             'UOB':'U Wind Component', 'VOB':'V Wind Component'}

for season in ['Winter', 'Spring']:

    fig = plt.figure(figsize=(8, 5.5))
    axes = []
    all_pvalue = []
    for i, v in enumerate(['TOB', 'QOB', 'POB', 'UOB', 'VOB']):
        ax = fig.add_subplot(2, 3, i+1, projection=ccrs.LambertConformal())
        station_mean_z = np.zeros(len(station_ids))
        station_autocorr_z = np.zeros(len(station_ids))
        station_adj_n = np.zeros(len(station_ids))
        station_adj_var = np.zeros(len(station_ids))
        station_t = np.zeros(len(station_ids))
        station_pvalue = np.zeros(len(station_ids))
        for j, SID in enumerate(station_ids):
            zscore1d = np.zeros(all_data[season]['fake_stations_z'][SID][v].size)
            ndays = all_data[season]['fake_stations_z'][SID][v].shape[0]
            for k in range(ndays):
                zscore1d[(k*24):((k+1)*24)] = all_data[season]['fake_stations_z'][SID][v][k, :]
            zscore1d = zscore1d[~np.isnan(zscore1d)]
            station_mean_z[j] = np.mean(zscore1d)
            station_autocorr_z[j] = np.corrcoef(zscore1d[1:], zscore1d[:-1])[0, 1]
            station_adj_n[j] = (len(zscore1d)-1) * (1 - station_autocorr_z[j]) / (1 + station_autocorr_z[j])
            station_adj_var[j] = np.var(zscore1d) / station_adj_n[j]
            station_t[j] = station_mean_z[j] / np.sqrt(station_adj_var[j])
            station_pvalue[j] = 2 * (1 - ss.t.cdf(np.abs(station_t[j]), station_adj_n[j])) 

        all_pvalue.append(station_pvalue)

        # Plot results
        sig_ind = station_pvalue <= sig_level
        nonsig_ind = station_pvalue > sig_level
        for ind, m in zip([sig_ind, nonsig_ind], ['*', 'o']):
            cax = ax.scatter(station_lon[ind], station_lat[ind], c=station_mean_z[ind], s=40, 
                             cmap='bwr', vmin=-3, vmax=3, marker=m, linewidths=0.5, edgecolors='k',
                             transform=ccrs.PlateCarree(), alpha=1)
    
        ax.set_title('%s) %s' % (labels[i], var_names[v]), size=14)
        ax.set_extent([-120, -72, 21, 50])
        ax.coastlines('50m', edgecolor='gray', linewidth=0.25)
        borders = cfeature.NaturalEarthFeature(category='cultural',
                                               scale='50m',
                                               facecolor='none',
                                               name='admin_1_states_provinces')
        ax.add_feature(borders, linewidth=0.25, edgecolor='gray')
        lakes = cfeature.NaturalEarthFeature(category='physical',
                                             scale='50m',
                                             facecolor='none',
                                             name='lakes')
        ax.add_feature(lakes, linewidth=0.25, edgecolor='gray')
        #ax.add_feature(cfeature.LAKES)
        #ax.add_feature(cfeature.OCEAN)
        #ax.add_feature(cfeature.LAND)
        axes.append(ax)

    # Final subplot: Histogram of p-values
    ax = fig.add_subplot(2, 3, 6)
    ax.hist(np.ravel(np.array(all_pvalue)), bins=np.arange(0, 1.0001, 0.05), lw=1, edgecolor='k') 
    ax.set_title('f) Histogram of $p$-values', size=14)
    ax.set_xlabel('$t$ test $p$-values', size=12)
    ax.set_ylabel('count', size=12)
    ax.set_xlim([0, 1])
    ax.grid(axis='y')
    axes.append(ax)

    # Explicitly create an axes for the colorbar using the cax keyword. This appears to be a 
    # necessary step whenever a colorbar is used with CartoPy
    cb_ax = fig.add_axes([0.05, 0.1, 0.9, 0.03])
    cbar = plt.colorbar(cax, cax=cb_ax, ax=axes, orientation='horizontal', pad=0.5, aspect=30)
    cbar.set_label('mean standardized anomaly', size=12)

    plt.subplots_adjust(left=0.02, bottom=0.25, right=0.96, top=0.9, wspace=0.25, hspace=0.25)
    plt.suptitle('Surface Station Comparison: %s' % season, size=18)
    plt.savefig(out_fname % season)
    plt.close()


"""
End compare_NR_real_sfc_stations.py
"""
