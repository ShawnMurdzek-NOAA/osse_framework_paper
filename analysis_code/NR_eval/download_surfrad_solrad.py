"""
Download SURFRAD and SOLRAD Data

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import datetime as dt
import os


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Website hosting SURFRAD and SOLRAD data
surfrad_web = 'https://gml.noaa.gov/aftp/data/radiation/surfrad/'
solrad_web = 'https://gml.noaa.gov/aftp/data/radiation/solrad/'

# SURFRAD and SOLRAD stations
surfrad_stations = ['bon', 'dra', 'fpk', 'gwn', 'psu', 'sxf', 'tbl']
solrad_stations = ['abq', 'bis', 'hnx', 'msn', 'slc', 'sea', 'ste']

# Start and end years
start_year = 1995
end_year = 2023

# Days to download
download_days = ([dt.datetime(start_year, 2, i) for i in range(1, 8)] + 
                 [dt.datetime(start_year, 4, 29) + dt.timedelta(days=i) for i in range(8)])

# Directory to save data to
save_dir = '/work2/noaa/wrfruc/murdzek/real_obs/surfrad_solrad'


#---------------------------------------------------------------------------------------------------
# Download Data
#---------------------------------------------------------------------------------------------------

# Make subdirectories in save_dir
for dataset, stations in zip(['surfrad', 'solrad'], [surfrad_stations, solrad_stations]):
    for s in stations:
        os.system('mkdir -p {d}/{data}/{station}'.format(d=save_dir, data=dataset, station=s)) 

# Download data
for year in range(start_year, end_year+1):
    print('downloading for {year}'.format(year=year))
    for date in download_days:
        jday = dt.datetime(year, date.month, date.day).strftime('%j')
        for dataset, stations, remote_parent in zip(['surfrad', 'solrad'], 
                                                    [surfrad_stations, solrad_stations],
                                                    [surfrad_web, solrad_web]): 
            for st in stations:
                fname = '{st}{yr}{jday}.dat'.format(st=st, yr=str(year)[2:], jday=jday)
                remote_dir = '{parent}/{st}/{year}'.format(parent=remote_parent, st=st, year=year)
                local_dir = '{parent}/{data}/{st}/'.format(parent=save_dir, data=dataset, st=st)
                os.system('wget --no-check-certificate {rdir}/{fname}'.format(rdir=remote_dir, fname=fname))
                os.system('mv ./{fname} {ldir}/{fname}'.format(ldir=local_dir, fname=fname))
        

"""
End download_surfrad_solrad.py
"""
