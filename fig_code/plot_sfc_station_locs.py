"""
Plot Surface Station Locations

shawn.s.murdzek@noaa.gov
Date Created: 1 March 2023
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import matplotlib.pyplot as plt


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Surface station files
station_files = []
path = '/work2/noaa/wrfruc/murdzek/real_obs/sfc_stations/spring'
with open('station_list.txt', 'r') as fptr:
    station_names = fptr.readlines()
for s in station_names:
    station_files.append('%s/%s_202204290000_202205070000.txt' % (path, s.strip()))

# Output file
out_fname = '../figs/SfcStationLocs.pdf'


#---------------------------------------------------------------------------------------------------
# Plot Surface Station Locations
#---------------------------------------------------------------------------------------------------

proj = ccrs.PlateCarree()
proj = ccrs.LambertConformal()

fig = plt.figure(figsize=(9.5, 6))
ax = fig.add_subplot(1, 1, 1, projection=proj)
for f, s in zip(station_files, station_names):
    df = pd.read_csv(f, skiprows=5)
    ax.plot(df['lon'].loc[0], df['lat'].loc[0], c='k', marker='o', markersize=8, transform=ccrs.PlateCarree())
    #ax.text(df['lon'].loc[0]+0.5, df['lat'].loc[0]+0.5, s, fontweight='bold', 
    #        transform=ccrs.PlateCarree())

ax.set_extent([-120, -72, 21, 50])
ax.set_title('Surface Station Locations', size=18)
ax.coastlines('50m', edgecolor='gray')
borders = cfeature.NaturalEarthFeature(category='cultural',
                                       scale='50m',
                                       facecolor='none',
                                       name='admin_1_states_provinces')
ax.add_feature(borders, linewidth=0.5, edgecolor='gray')
#lakes = cfeature.NaturalEarthFeature(category='physical',
#                                     scale='50m',
#                                     facecolor='dodgerblue',
#                                     name='lakes')
#ax.add_feature(lakes, linewidth=0.5, edgecolor='k')
ax.add_feature(cfeature.LAKES)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.LAND)

plt.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.94)
plt.savefig(out_fname)
plt.close()


"""
End plot_sfc_station_locs.py
"""
