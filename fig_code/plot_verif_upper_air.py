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

import metplus_OSSE_scripts.plotting.metplus_plots as mp
import metplus_OSSE_scripts.plotting.metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Input file information
parent_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_'
seasons = ['winter', 'spring']
input_sims = {'winter':{'real':{'dir':parent_dir + 'pt_obs/app_orion/sims_real_red_data/winter/upper_air/2022020109/output/point_stat',
                                'color':'r',
                                'prefix':'point_stat',
                                'subset':'ADPUPA'},
                        'OSSE':{'dir':parent_dir + 'pt_obs/app_orion/sims_syn_data/winter_2iter/upper_air/2022020109/output/point_stat',
                                'color':'b',
                                'prefix':'point_stat',
                                'subset':'ADPUPA'},
                        'OSSE (grid)':{'dir':parent_dir + 'grid_NR/app_orion/winter_2iter/upper_air/output/GridStat',
                                       'color':'gray',
                                       'prefix':'grid_stat_FV3_TMP_vs_NR_TMP',
                                       'subset':'NR'}
                        },
              'spring':{'real':{'dir':parent_dir + 'pt_obs/app_orion/sims_real_red_data/spring/upper_air/2022042921/output/point_stat',
                                'color':'r',
                                'prefix':'point_stat',
                                'subset':'ADPUPA'},
                        'OSSE':{'dir':parent_dir + 'pt_obs/app_orion/sims_syn_data/spring_2iter/upper_air/2022042921/output/point_stat',
                                'color':'b',
                                'prefix':'point_stat',
                                'subset':'ADPUPA'},
                        'OSSE (grid)':{'dir':parent_dir + 'grid_NR/app_orion/spring_2iter/upper_air/output/GridStat',
                                       'color':'gray',
                                       'prefix':'grid_stat_FV3_TMP_vs_NR_TMP',
                                       'subset':'NR'}
                        }}
#for season in input_sims.keys():
#    del input_sims[season]['OSSE (grid)']

# Other plotting options
plot_options = {'TMP':{'line_type':'sl1l2',
                       'plot_stat':'RMSE',
                       'xlabel':'T RMSE (K)',
                       'plot_param':{'FCST_VAR':'TMP',
                                     'OBTYPE':'ADPUPA'}},
                'SPFH':{'line_type':'sl1l2',
                        'plot_stat':'RMSE',
                        'xlabel':'Q RMSE (kg kg$^{-1}$)',
                        'plot_param':{'FCST_VAR':'SPFH',
                                      'OBTYPE':'ADPUPA'}},
                'UGRD_VGRD':{'line_type':'vl1l2',
                             'plot_stat':'VECT_RMSE',
                             'xlabel':'Wind RMSE (m s$^{-1}$)',
                             'plot_param':{'FCST_VAR':'UGRD_VGRD',
                                           'OBTYPE':'ADPUPA'}}}
toggle_pts = False
ci = True
ci_lvl = 0.95
ci_opt = 'bootstrap'
ci_kw = {'bootstrap_kw':{'n_resamples':10000}}

# Valid times (as datetime objects)
valid_times = {'winter':[dt.datetime(2022, 2, 1, 12) + dt.timedelta(hours=i) for i in range(0, 156, 12)],
               'spring':[dt.datetime(2022, 4, 30, 0) + dt.timedelta(hours=i) for i in range(0, 156, 12)]}

# Forecast lead times (hrs)
fcst_lead = 3

save_fname = '../figs/VerifUAVprof.pdf'


#---------------------------------------------------------------------------------------------------
# Read Data and Create Plot
#---------------------------------------------------------------------------------------------------

fig, axes = plt.subplots(nrows=len(seasons), ncols=3, figsize=(8, 6), sharey=True, sharex='col')
plt.subplots_adjust(left=0.11, bottom=0.09, right=0.99, top=0.92, wspace=0.1, hspace=0.1)

for i, season in enumerate(seasons):
    for j, var in enumerate(['TMP', 'SPFH', 'UGRD_VGRD']):
        print('plotting %s %s' % (season, var))
        if len(seasons) > 1:
            ax = axes[i, j]
        else:
            ax = axes[j]
        _, ax = mp.plot_ua_vprof(input_sims[season], valid_times[season], fcst_lead=fcst_lead, 
                                 line_type=plot_options[var]['line_type'],
                                 plot_param=plot_options[var]['plot_param'], 
                                 plot_stat=plot_options[var]['plot_stat'],
                                 toggle_pts=toggle_pts, verbose=False, ax=ax,
                                 mean_legend=False, ci=ci, ci_lvl=ci_lvl,
                                 ci_opt=ci_opt, ci_kw=ci_kw)
        ax.set_title('')
        if (i != 0) or (j != 1):
            ax.get_legend().remove()
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

        # Adjust x axis of wind RMSE plot so it doesn't overlap with Q RMSE plot
        if j == 2:
            ax.set_xlim([1.6, 6.75])

# Subplot labels
if len(seasons) == 1:
    letters = ['a', 'b', 'c']
else:
    letters = ['a', 'b', 'c', 'd', 'e', 'f']
for i, let in enumerate(letters):
    plt.gcf().text(0.12 + 0.305*(i%3), 0.885 - 0.432*(int(i/3)), '%s)' % let, fontsize=12,
                   fontweight='bold', backgroundcolor='white')

plt.suptitle('Upper-Air Verification: %d$-$hr Forecasts' % fcst_lead, size=18)
plt.savefig(save_fname)
plt.close()


"""
End plot_verif_upper_air.py 
"""
