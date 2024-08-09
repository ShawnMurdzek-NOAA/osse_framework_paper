"""
"Candlestick" Plots Showing Observation Impacts From Data Denial Experiments

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os
import pandas as pd

import metplus_OSSE_scripts.plotting.metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Directories containing METplus output
met_dir = {'real':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_real_red_data',
           'OSSE':'/work2/noaa/wrfruc/murdzek/RRFS_OSSE/metplus_verif_pt_obs/app_orion/sims_syn_data'}

# Valid times
valid_times = {'winter':[dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(160)],
               'spring':[dt.datetime(2022, 4, 29, 21) + dt.timedelta(hours=i) for i in range(160)]}

# Verifying observations
verif_obs = {'sfc':'ADPSFC', 'upper_air':'ADPUPA'}

# Experiments
experiments = {'ctrl':'', 'no aircraft':'_no_aircft', 'no raob':'_no_raob', 'no sfc':'_no_sfc'}

# Forecast lengths
fcst_lead = [0, 1, 3, 6]

# Vertical layer for averaging upper-air verification (hPa)
vert_min = 700
vert_max = 1000

# Variables and line_types

# Full upper-air verif (1000 - 100 hPa)
#var_dict = {'TMP':{'line_type':'sl1l2', 'name':'temperature', 'stat':'RMSE', 'units':'K', 
#                   'lim_upper_air':[-0.05, 0.4], 'lim_sfc':[-0.02, 1.4]}, 
#            'SPFH':{'line_type':'sl1l2', 'name':'specific humidity', 'stat':'RMSE', 'units':'kg kg$^{-1}$', 
#                    'lim_upper_air':[-0.5e-4, 3.10e-4], 'lim_sfc':[-0.2e-4, 4.5e-4]},
#            'UGRD_VGRD':{'line_type':'vl1l2', 'name':'wind', 'stat':'VECT_RMSE', 'units':'m s$^{-1}$', 
#                         'lim_upper_air':[-0.2, 2.4], 'lim_sfc':[-0.1, 0.95]}}

# Lower troposphere verif (1000 - 700 hPa)
var_dict = {'TMP':{'line_type':'sl1l2', 'name':'temperature', 'stat':'RMSE', 'units':'K', 
                   'lim_upper_air':[-0.08, 0.37], 'lim_sfc':[-0.02, 1.4]}, 
            'SPFH':{'line_type':'sl1l2', 'name':'specific humidity', 'stat':'RMSE', 'units':'kg kg$^{-1}$', 
                    'lim_upper_air':[-0.8e-4, 3.90e-4], 'lim_sfc':[-0.2e-4, 4.5e-4]},
            'UGRD_VGRD':{'line_type':'vl1l2', 'name':'wind', 'stat':'VECT_RMSE', 'units':'m s$^{-1}$', 
                         'lim_upper_air':[-0.6, 1.5], 'lim_sfc':[-0.1, 0.95]}}

# Confidence interval level
ci_lvl = 0.95
ci_opt = 'bootstrap'
ci_kw = {'bootstrap_kw':{'n_resamples':10000}}

# Option to add annotations
add_annot = True

# Output file name (with %s placeholder for verification type)
save_fname = '../figs/CandlestickLowerAtm%s.pdf'


#---------------------------------------------------------------------------------------------------
# Read in Data
#---------------------------------------------------------------------------------------------------

stats = {}
for v in verif_obs.keys():
    stats[v] = {}
    for dataset in met_dir.keys():
        stats[v][dataset] = {}
        for s in valid_times.keys():
            print('extracting data for %s %s %s' % (v, dataset, s))
            stats[v][dataset][s] = {}
            for exp in experiments.keys():
                stats[v][dataset][s][exp] = {}
                if dataset == 'OSSE':
                    data_dir = '{parent}/{s}_2iter{e}/{v}/{t}/output/point_stat'.format(parent=met_dir[dataset], 
                                                                                        s=s, e=experiments[exp], 
                                                                                        v=v, t=valid_times[s][0].strftime('%Y%m%d%H'))
                elif dataset == 'real':
                    data_dir = '{parent}/{s}{e}/{v}/{t}/output/point_stat'.format(parent=met_dir[dataset], 
                                                                                  s=s, e=experiments[exp], 
                                                                                  v=v, t=valid_times[s][0].strftime('%Y%m%d%H'))
                for fl in fcst_lead:
                    stats[v][dataset][s][exp][fl] = {}
                    for varname in var_dict.keys():
                        stats[v][dataset][s][exp][fl][varname] = {}

                        fnames = ['%s/point_stat_%02d0000L_%sV_%s.txt' %
                                  (data_dir, fl, t.strftime('%Y%m%d_%H%M%S'), var_dict[varname]['line_type']) 
                                  for t in valid_times[s]]
                        if v == 'sfc':
                            tmp = mt.read_ascii(fnames, verbose=False)
                        elif v == 'upper_air':
                            # Average in vertical first
                            tmp_df_list = []
                            for f in fnames:
                                if os.path.isfile(f):
                                    df = mt.read_ascii([f], verbose=False)
                                    tmp_df_list.append(mt.compute_stats_vert_avg(df, vmin=vert_min, vmax=vert_max, 
                                                                                 line_type=var_dict[varname]['line_type'])) 
                                else:
                                    continue
                            tmp = pd.concat(tmp_df_list)

                        red_df = tmp.loc[(tmp['FCST_VAR'] == varname) &
                                         (tmp['OBTYPE'] == verif_obs[v])].copy()
                        red_df = mt.compute_stats(red_df, line_type=var_dict[varname]['line_type'])
                        if exp == 'ctrl':
                            stats[v][dataset][s][exp][fl][varname]['all_data'] = red_df[var_dict[varname]['stat']].values
                        else:
                            stats[v][dataset][s][exp][fl][varname]['all_data'] = (red_df[var_dict[varname]['stat']].values -
                                                                                  stats[v][dataset][s]['ctrl'][fl][varname]['all_data'])
                            # Take temporal average
                            stats[v][dataset][s][exp][fl][varname]['mean'] = np.mean(stats[v][dataset][s][exp][fl][varname]['all_data'])
                            ci_out = mt.confidence_interval_mean(stats[v][dataset][s][exp][fl][varname]['all_data'], level=ci_lvl,
                                                                 option=ci_opt, ci_kw=ci_kw)
                            stats[v][dataset][s][exp][fl][varname]['ci_low'] = ci_out[0]
                            stats[v][dataset][s][exp][fl][varname]['ci_high'] = ci_out[1]
                

#---------------------------------------------------------------------------------------------------
# Plot Data
#---------------------------------------------------------------------------------------------------

bar_hgt = 0.9/len(fcst_lead) 

for v in verif_obs.keys():
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(8, 7), sharex='col', sharey=True)
    plt.subplots_adjust(left=0.17, bottom=0.1, right=0.99, top=0.94, hspace=0.1, wspace=0.1)
    for j, dataset in enumerate(met_dir.keys()):
        for k, varname in enumerate(var_dict.keys()):
            ax = axes[j, k]
            for off1, s in zip([0, 4], valid_times.keys()):
                for off2, c, exp in zip([1, 2, 3], ['c', 'r', 'gray'], list(experiments.keys())[1:]):
                    for off3, fl in zip([-0.45 + 0.5*bar_hgt + bar_hgt*n for n in range(len(fcst_lead))], fcst_lead): 
                        ax.barh(off1+off2+off3, 
                                stats[v][dataset][s][exp][fl][varname]['mean'],
                                color=c, edgecolor='k', height=bar_hgt)
                        ax.plot([stats[v][dataset][s][exp][fl][varname]['ci_low'],
                                 stats[v][dataset][s][exp][fl][varname]['ci_high']],
                                [off1+off2+off3, off1+off2+off3], 'k-', lw=1.5)
            ax.grid(axis='x')
            if add_annot:
                ax.axhline(4, ls='--', c='k')
            ax.set_xlim(var_dict[varname]['lim_%s' % v])
            if j == 1:
                ax.set_xlabel('%s (%s)' % (var_dict[varname]['name'], var_dict[varname]['units']), size=14)
            if k == 0:
                ax.set_yticks([1, 2, 3, 5, 6, 7], labels=list(experiments.keys())[1:]*2, size=12)

        plt.gcf().text(0.01, 0.72 - 0.45*j, dataset, fontsize=16, backgroundcolor='white', 
                       rotation='vertical')

    # Subplot labels and other text
    letters = ['a', 'b', 'c', 'd', 'e', 'f']
    for j, let in enumerate(letters):
        xloc = 0.3925 + 0.2815*(j%3)
        plt.gcf().text(xloc, 0.91 - 0.44*(int(j/3)), '%s)' % let, fontsize=12,
                       fontweight='bold', backgroundcolor='white')
        if add_annot:
            for k, season in enumerate(valid_times.keys()):
                plt.gcf().text(xloc, 0.6 - 0.44*(int(j/3)) + 0.2*k, season, fontsize=12, 
                               backgroundcolor='white', rotation='vertical')

    if v == 'sfc':
        plt.suptitle('Surface RMSE Differences (Exp $-$ Ctrl)', size=18)
        plt.savefig(save_fname % 'Sfc')
    elif v == 'upper_air':
        plt.suptitle('Upper-Air RMSE Differences (Exp $-$ Ctrl)', size=18)
        plt.savefig(save_fname % 'UA')
    plt.close()


"""
End plot_data_denial_verif.py
"""
