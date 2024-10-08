"""
Perform Comparisons Between Real and Simulated Surface Station Observations on a Map

Real surface station obs come from the Iowa Environmental Mesonet database:
https://mesonet.agron.iastate.edu/request/download.phtml

This script uses "perfect" station matching. This means that the NR output WAS intentionally
interpolated to the real surface stations used for comparison here.

This script uses a pickle file generated by ../analysis_code/NR_eval/compare_NR_real_sfc_stations_perfect_matching.py

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
parent_dir = '../analysis_code/NR_eval'
pickle_winter_fname = parent_dir + '/sfc_station_ceil_exp2_compare_winter.pkl'
pickle_spring_fname = parent_dir + '/sfc_station_ceil_exp2_compare_spring.pkl'

# Surface station information
with open('station_list.txt', 'r') as fptr:
    station_ids = fptr.readlines()
    for i in range(len(station_ids)):
        station_ids[i] = station_ids[i].strip()
sfc_station_sampl_path = '/work2/noaa/wrfruc/murdzek/real_obs/sfc_stations/spring'

# Output file name
out_fname = '../figs/SfcStationComparisonCeil.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data
#---------------------------------------------------------------------------------------------------

# Read in pickled data
all_data = {}
for season, pkl in zip(['Winter', 'Spring'], [pickle_winter_fname, pickle_spring_fname]):
    with open(pkl, 'rb') as handle:
        all_data[season] = pickle.load(handle)

# Read in surface station locations
station_lat = {}
station_lon = {}
for i, s in enumerate(station_ids):
    df = pd.read_csv('%s/%s_202204290000_202205070000.txt' % (sfc_station_sampl_path, s), skiprows=5)
    station_lat[s] = df['lat'].loc[0]
    station_lon[s] = df['lon'].loc[0]

ceil_thres = [0.1524, 0.3048, 0.9144] # DO NOT CHANGE! This is unique to the pickle file
ceil_thres_ft = [500, 1000, 3000]
nthres = len(ceil_thres)


#---------------------------------------------------------------------------------------------------
# Plot results
#---------------------------------------------------------------------------------------------------

labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

fig = plt.figure(figsize=(8, 5))
axes = []
for i, season in enumerate(['Winter', 'Spring']):

    for j, thres in enumerate(ceil_thres_ft):
        ax_num = 1+j+3*i
        print(ax_num)
        ax = fig.add_subplot(2, nthres, ax_num, projection=ccrs.LambertConformal())
        for SID in station_ids:
            rank = all_data[season]['fake_station_rank'][SID]['ceil'][j]
            if (rank == 1) or (rank == 0):
                m = '*'
            else:
                m = 'o'
            cax = ax.scatter(station_lon[SID], station_lat[SID], 
                             c=rank, s=40, 
                             cmap='bwr', vmin=0, vmax=1, marker=m, linewidths=0.5, edgecolors='k',
                             transform=ccrs.PlateCarree(), alpha=1)
 
        ax.set_title('%s) %s, %s ft' % (labels[ax_num-1], season, thres), size=14)
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
 
# Explicitly create an axes for the colorbar using the cax keyword. This appears to be a 
# necessary step whenever a colorbar is used with CartoPy
cb_ax = fig.add_axes([0.05, 0.1, 0.9, 0.03])
cbar = plt.colorbar(cax, cax=cb_ax, ax=axes, orientation='horizontal', pad=0.5, aspect=25)
cbar.set_label('NR rank (decimal)', size=12)

plt.subplots_adjust(left=0.02, bottom=0.15, right=0.98, top=0.88, wspace=0.05, hspace=0.18)
plt.suptitle('Surface Station Ceiling Frequency Comparison', size=18)
plt.savefig(out_fname)
plt.close()


"""
End compare_NR_real_sfc_stations.py
"""
