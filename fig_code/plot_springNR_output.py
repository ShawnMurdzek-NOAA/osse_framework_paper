"""
Plot Example Nature Run Output

shawn.s.murdzek@noaa.gov
Date Created: 14 September 2023
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import xarray as xr
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import pyart.graph.cm_colorblind as art_cm

import pyDA_utils.plot_model_data as pmd


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

times = ['1830', '1900', '1930', '2000']
upp_files = ['/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP/20220501/wrfnat_20220501%s.grib2' % t
             for t in times]
subtitles = ['%s) %s UTC' % (abc, t) for abc, t in zip(['a', 'b', 'c', 'd'], times)]

# UPP fields to plot
contf_field = 'REFC_P0_L200_GLC0'
cont_field = 'DPT_P0_L103_GLC0'

# Domain limits
lon = [-107, -100]
lat = [30, 36]

# Single points to plot
lon_pts = []
lat_pts = []

save_fname = '../figs/CIspringNR.png'
#save_fname = '../figs/CIspringNR.pdf'


#---------------------------------------------------------------------------------------------------
# Plot Data
#---------------------------------------------------------------------------------------------------

nrows = 2
ncols = 2
fig = plt.figure(figsize=(10, 10))
    
out_obj = []
for i, (fname, s) in enumerate(zip(upp_files, subtitles)):
    print('plotting %s' % fname)
    ds = xr.open_dataset(fname, engine='pynio')
    # For some reason, using LambertConformal for the projection messes up the filled contour plot,
    # so use PlateCarree.
    out = pmd.PlotOutput([ds], 'upp', fig, nrows, ncols, i+1, proj=ccrs.PlateCarree())
    out.contour(cont_field, ingest_kw={'smooth':True, 'gauss_sigma':5}, 
                cnt_kw={'colors':'gray', 'levels':np.arange(263.15, 320, 4), 'linewidths':0.75})
    out.contourf(contf_field, cbar=False, cntf_kw={'cmap':art_cm.HomeyerRainbow, 
                                                   'levels':np.arange(5, 75, 5)})

    for x, y in zip(lon_pts, lat_pts):
            out.plot(x, y, plt_kw={'markersize':10, 'marker':'*', 'color':'k'})

    out.set_lim(lat[0], lat[1], lon[0], lon[1])
    out.ax.coastlines('10m', edgecolor='k', linewidth=0.75)
    borders = cfeature.NaturalEarthFeature(category='cultural',
                                           scale='10m',
                                           facecolor='none',
                                           name='admin_1_states_provinces')
    out.ax.add_feature(borders, linewidth=0.75, edgecolor='k')
    out.ax.set_title(s, size=16)
    #out.ax_title(size=14)
    out_obj.append(out)

cb_ax = fig.add_axes([0.05, 0.07, 0.9, 0.03])
cbar = plt.colorbar(out_obj[0].cax, cax=cb_ax, orientation='horizontal', aspect=35, pad=0.1)
cbar.set_label('composite reflectivity (dB$Z$)', size=16)
cbar.ax.tick_params(labelsize=12)

plt.subplots_adjust(left=0.02, bottom=0.12, right=0.98, top=0.95, hspace=0.1, wspace=0.05)
plt.savefig(save_fname, dpi=500)
plt.close()


"""
End plot_upp.py
""" 
