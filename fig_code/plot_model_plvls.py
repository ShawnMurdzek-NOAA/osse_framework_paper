"""
Plot Model Pressure Levels for Nature Run and RRFS

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# UPP native-level output files for nature run (NR) and RRFS
NR_output = '/work2/noaa/wrfruc/murdzek/nature_run_spring/UPP/20220430/wrfnat_202204300000_er.grib2'
RRFS_output = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/syn_data_app_orion/spring_2iter/NCO_dirs/ptmp/prod/rrfs.20220429/22/rrfs.t22z.natlev.f002.conus_3km.grib2'

# Output file
save_fname = '../figs/modelDPdist.pdf'


#---------------------------------------------------------------------------------------------------
# Create Plots
#---------------------------------------------------------------------------------------------------

def find_closest_gridpoint(ds, lat, lon):
    """
    Find UPP gridpoint that is closest to the desired (lat, lon) coordinate
    """

    flat_idx = np.argmin((ds['gridlon_0'].values - lon)**2 + (ds['gridlat_0'].values - lat)**2)
    full_idx = np.unravel_index(flat_idx, ds['gridlon_0'].shape)

    return full_idx


def find_gridpoint_with_psfc(ds, psfc):
    """
    Find the UPP gridpoint with surface pressure closest to the desired value
    """

    flat_idx = np.argmin(np.abs(ds['PRES_P0_L1_GLC0'].values - psfc))
    full_idx = np.unravel_index(flat_idx, ds['gridlon_0'].shape)
    psfc = ds['PRES_P0_L1_GLC0'].values[full_idx[0], full_idx[1]]

    return full_idx, psfc


def plot_plvl_dist(ds, ax, y_idx, x_idx, ttl, plt_kw={}, ttl_kw={}, verbose=True, no_xaxis_ticks=True):
    """
    Plot vertical distribution of pressure levels
    """

    p1d = ds['PRES_P0_L105_GLC0'][:, y_idx, x_idx].values
    for p in p1d:
        ax.plot([0, 1], [p*1e-2]*2, **plt_kw)

    # Turn off x-axis ticks and labels
    if no_xaxis_ticks:
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

    # Add title
    p_pbl = 85000
    ax.set_title(f"{ttl}\n{np.sum(p1d >= p_pbl)} levels below {p_pbl*1e-2:.0f} hPa", **ttl_kw)

    if verbose:
        print(f"max p = {np.amax(p1d)}")
        print(f"min p = {np.amin(p1d)}")

    return ax


def plot_dp_dist(ds, ax, y_idx, x_idx, ttl, plt_kw={}, verbose=True):
    """
    Plot vertical distribution of delta-p (distance between pressure levels)
    """

    p1d = ds['PRES_P0_L105_GLC0'][:, y_idx, x_idx].values * 1e-2
    dp = p1d[:-1] - p1d[1:]
    avg_p = 0.5*(p1d[1:] + p1d[:-1])

    ax.plot(dp, avg_p, **plt_kw)

    if verbose:
        print(f"max dp = {np.amax(dp)}")
        print(f"min dp = {np.amin(dp)}")
        print(f"levels below 850 hPa = {np.sum(p1d >= 850)}")

    return ax


if __name__ == '__main__':

    # Make plot
    ds = []
    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(6, 8))
    plt.subplots_adjust(top=0.97, bottom=0.08, right=0.97)
    for fname, ttl, c in zip([NR_output, RRFS_output], ['NR', 'RRFS'], ['r', 'b']):

        print()
        print(f"Making plot for {ttl}")
        ds.append(xr.open_dataset(fname, engine='pynio'))

        idx, psfc = find_gridpoint_with_psfc(ds[-1], 101300)
        print(f"gridpoint index = ({idx[0]}, {idx[1]})")
        print(f"lat = {ds[-1]['gridlat_0'].values[idx[0], idx[1]]}, lon = {ds[-1]['gridlon_0'].values[idx[0], idx[1]]}")
        print(f"psfc = {psfc} Pa")

        #plot_plvl_dist(ds[-1], ax, idx[0], idx[1], ttl, plt_kw={'c':'k', 'lw':0.5}, ttl_kw={'size':18})
        plot_dp_dist(ds[-1], ax, idx[0], idx[1], ttl, plt_kw={'c':c, 'lw':2.5, 'label':ttl})

    # Add annotations
    ax.legend(fontsize=14)
    ax.grid()
    ax.set_xlim(left=0)
    ax.set_ylim([1020, 0])
    ax.set_xlabel('dp (hPa)', size=14)
    ax.set_ylabel('pressure (hPa)', size=14)

    plt.savefig(save_fname)


"""
End plot_model_plvls.py
"""
