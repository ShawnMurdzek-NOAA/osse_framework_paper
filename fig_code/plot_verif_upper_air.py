"""
Plot Verticle Profiles for Upper-Air Verification

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

import metplus_OSSE_scripts.utils.metplus_plots as mp
import metplus_OSSE_scripts.utils.metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input file information
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/'
input_sims = {'winter':{'real':{'dir':parent_dir + 'real_red_sims/winter_updated/upper_air/output/point_stat',
                                'color':'r'},
                        'OSSE':{'dir':parent_dir + 'syn_data_sims/winter_updated/upper_air/output/point_stat',
                                'color':'b'}},
              'spring':{'real':{'dir':parent_dir + 'real_red_sims/spring/upper_air/output/point_stat',
                                'color':'r'},
                        'OSSE':{'dir':parent_dir + 'syn_data_sims/spring/upper_air/output/point_stat',
                                'color':'b'}}}
ob_subset = 'ADPUPA'

# Other plotting options
plot_options = {'TMP':{'line_type':'sl1l2',
                       'plot_stat':'RMSE',
                       'xlabel':'T RMSE (K)'},
                'SPFH':{'line_type':'sl1l2',
                        'plot_stat':'RMSE',
                        'xlabel':'Q RMSE (kg kg$^{-1}$)'},
                'UGRD_VGRD':{'line_type':'vl1l2',
                             'plot_stat':'VECT_RMSE',
                             'xlabel':'Wind RMSE (m s$^{-1}$)'}}
toggle_pts = True

# Valid times (as datetime objects)
valid_times = {'winter':[dt.datetime(2022, 2, 1, 12) + dt.timedelta(hours=i) for i in range(0, 156, 12)],
               'spring':[dt.datetime(2022, 4, 30, 0) + dt.timedelta(hours=i) for i in range(0, 156, 12)]}

# Forecast lead times (hrs)
fcst_lead = 3

save_fname = '../figs/VerifUAVprof.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 6), sharey=True, sharex='col')
plt.subplots_adjust(left=0.11, bottom=0.09, right=0.99, top=0.92, wspace=0.1, hspace=0.1)

for i, season in enumerate(['winter', 'spring']):
    for j, var in enumerate(['TMP', 'SPFH', 'UGRD_VGRD']):
        print('plotting %s %s' % (season, var))
        ax = axes[i, j]
        _, ax = mp.plot_ua_vprof(input_sims[season], valid_times[season], fcst_lead=fcst_lead, 
                                 line_type=plot_options[var]['line_type'],
                                 plot_var=var, 
                                 plot_stat=plot_options[var]['plot_stat'],
                                 ob_subset=ob_subset, toggle_pts=toggle_pts, verbose=False, ax=ax,
                                 mean_legend=False)
        ax.set_title('')
        if (i != 0) or (j != 0):
            ax.get_legend().remove()
        else:
            ax.legend(loc='center right')
        if i == 0:
            ax.set_xlabel('')
        else:
            ax.set_xlabel(plot_options[var]['xlabel'], size=14)
        if j == 0:
           ax.set_ylabel('%s\npressure (hPa)' % season, size=14)
        else:
            ax.set_ylabel('')
        #if j == 1:
        #   ax.ticklabel_format(axis='x', style='sci', scilimits=(0,0)) 

# Subplot labels
letters = ['a', 'b', 'c', 'd', 'e', 'f']
for i, let in enumerate(letters):
    plt.gcf().text(0.12 + 0.305*(i%3), 0.885 - 0.432*(int(i/3)), '%s)' % let, fontsize=12,
                   fontweight='bold', backgroundcolor='white')

plt.suptitle('Upper-Air Verification', size=18)
plt.savefig(save_fname)
plt.close()


"""
End plot_verif_upper_air.py 
"""
