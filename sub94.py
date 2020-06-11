import xarray as xr
import numpy as np
from varlist import var_list
import time
import glob

t0 = time.time()

for year in np.arange(1994, 1995):
    
    # select all files from water year excluding final hour (repeat from start of following water year)
    files = sorted(glob.glob('/mnt/wrf_history/vol??/wrf_out/wy_' + str(year) + '/d02/wrfout_d02_*')[:-1])	

    # open multi-file dataset (this function accepts unix wildcards)
    d = xr.open_mfdataset(files, drop_variables=var_list)
    
    d1 = d['T2'][0:5136]
    d2 = d['Q2'][0:5136]
   # d3 = d['SWDOWN'][0:5136]
   # d4 = d['SWNORM'][0:5136]

    e1 = d['T2'][5137:]
    e2 = d['Q2'][5137:]
   # e3 = d['SWDOWN'][5137:]
   # e4 = d['SWNORM'][5137:]

    f1  = xr.concat([d1,e1],dim='Time')
    f2 = xr.concat([d2,e2],dim='Time')
   # f3 = xr.concat([d3,e3],dim='Time')
   # f4 = xr.concat([d4,e4],dim='Time')
    d = xr.merge([f1,f2])

    # Swap time and XTIME
    d = d.swap_dims({'Time':'XTIME'})	
    # Get mean/min/max by day of year for desired variables 
    new_array = d[['T2','Q2']].resample(XTIME = '24H').min(dim = 'XTIME') # create daily means of few variables
    new_array['TMAX'] = d['T2'].resample(XTIME = '24H').max(dim = 'XTIME')

    
   #new_array['TMIN'] = d['T2'].resample(XTIME = '24H').min() # create daily minimum temperature
   # new_array['TMAX'] = d.resample(XTIME = '24H').max(dim = 'XTIME') # create daily maximum temperature
    new_array = new_array.rename({'T2' : 'TMIN'}) # rename T2 as TMEAN
    del new_array['Q2']
    # Adjust some meta data
   # new_array['TMEAN'].attrs = [('description','DAILY MEAN GRID SCALE TEMPERATUTE'), ('units','K')]
    new_array['TMIN'].attrs = [('description','DAILY MINIMUM GRID SCALE TEMPERATURE'), ('units','K')]
    new_array['TMAX'].attrs = [('description','DAILY MAXIMUM GRID SCALE TEMPERATURE'), ('units','K')]
   # new_array['Q2'].attrs = [('description','DAILY MEAN GRID SCALE SPECIFIC HUMIDITY'), ('units','')]
   # new_array['SWDOWN'].attrs = [('description','DAILY MEAN DOWNWARD SHORT WAVE FLUX AT GROUND SURFACE'), ('units','W m^2')]
   # new_array['SWNORM'].attrs = [('description','DAILY MEAN NORMAL SHORT WAVE FLUX AT GROUND SURFACE (SLOPE-DEPENDENT)'), ('units','W m^2')]

    # Write new netcdf file
    new_array.to_netcdf("/mnt/selway/data/data_02/charlie/subsets/test/forLejo/Biome-BGC-WY--" + str(year) + "T2MinMIax.nc")

    del d, new_array
			
t1 = time.time()

print("Total time to create this subset was:", t1 - t0, "seconds.")
