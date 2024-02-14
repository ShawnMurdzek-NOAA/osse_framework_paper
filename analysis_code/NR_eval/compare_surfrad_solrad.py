"""
Compare NR Output to SURFRAD/SOLRAD Observations

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt
import pickle as pkl


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# NR and SURFRAD/SOLRAD directories
NR_dir = '/work2/noaa/wrfruc/murdzek/nature_run_winter/UPP'
obs_dir =  '/work2/noaa/wrfruc/murdzek/real_obs/surfrad_solrad'

# Integration bounds
start_day = dt.datetime(2022, 2, 1, 0)
end_day = dt.datetime(2022, 2, 8, 0)

# Range of years to use from SURFRAD/SOLRAD dataset
obs_start_yr = 2004
obs_end_yr = 2023

# Stations to include
surfrad_stations = []
solrad_stations = []

# Field to integrate
NR_field = 'DSWRF_P0_L1_GLC0'
surfrad_field = 'dw_solar'
solrad_field = 'dw_psp'

# Time interval for integration (s)
integrate_interval = 15*60


#---------------------------------------------------------------------------------------------------
# Read Data
#---------------------------------------------------------------------------------------------------

solrad_cols = []
surfrad_cols = []




"""
End compare_surfrad_solrad.py 
"""
