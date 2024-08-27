"""
Plot NR Mask

Command-Line Inputs
-------------------
argv[1] : NR mask .npy file
argv[2] : MRMS mask .npy file

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import sys
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

NR_upp_fname = '/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP/20220501/wrfprs_202205010800_er.grib2'
NR_mask_fname = sys.argv[1]

MRMS_fname = '/work2/noaa/wrfruc/murdzek/real_obs/mrms/2015/20150429-180012.MRMS_MergedReflectivityQCComposite_00.50_20150429-180012.grib2'
MRMS_mask_fname = sys.argv[2]


#---------------------------------------------------------------------------------------------------
# Plot NR and MRMS Masks
#---------------------------------------------------------------------------------------------------

for fname, mask_name, lat_name, lon_name in zip([NR_upp_fname, MRMS_fname],
                                                [NR_mask_fname, MRMS_mask_fname],
                                                ['gridlat_0', 'lat_0'],
                                                ['gridlon_0', 'lon_0']):

    # Read in data
    mask = np.load(mask_name)
    ds = xr.open_dataset(fname, engine='pynio')

    # Make plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertConformal())
    ax.contourf(ds[lon_name].values, ds[lat_name].values, mask, np.arange(0, 1.1, 0.5), 
                cmap='Reds', transform=ccrs.PlateCarree())

    # Add annotations
    ax.coastlines('50m', lw=1)
    borders = cfeature.NaturalEarthFeature(category='cultural',
                                           scale='50m',
                                           facecolor='none',
                                           name='admin_1_states_provinces')
    ax.add_feature(borders, lw=0.5)

    plt.savefig(f"{mask_name[:-4]}.png")


"""
End plot_NR_MRMS_mask.py
"""
