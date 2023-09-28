import glob
import pandas as pd
import xarray
import time

# input nc file
filePath='./OISST/*.????????.nc'

ds2 = xarray.open_mfdataset(filePath, parallel=True,chunks={'time': '500MB'})

print('Calculate sst monthly mean')
mean_month_sst =ds2["sst"].resample(time='1MS').mean()
pr_mean_done = mean_month_sst.compute()
pr_mean_done = pr_mean_done.where(pr_mean_done <= 100)
startTime = pd.to_datetime(str(pr_mean_done.time.min().data)).strftime('%Y-%m-%d')
endTime = pd.to_datetime(str(pr_mean_done.time.max().data)).strftime('%Y-%m-%d')
pr_mean_done.load().to_netcdf(f"OISST_25km_monthly_{startTime}-{endTime}.nc")

missing_data = pd.to_datetime(['1987-12', '1988-01', '2011-11'], format='%Y-%m')
ndays_ice = 15
ice = ds2.ice.fillna(0)
ice_binary = xarray.where(ice <= 0, 0, 1)
ice_mask = ice_binary.resample(time='1MS').sum(dim='time')
ice_mask = xarray.where(ice_mask > ndays_ice, 1, 0)
for missing_date in missing_data:
    idx = pd.Index(ice_mask.time.values).get_indexer([missing_date], method='nearest')[0]
    surrounding_months = ice_mask.isel(time=slice(max(idx - 1, 0), min(idx + 1, len(ice_mask.time) - 1) + 1))
    ice_mask[idx] = surrounding_months.max(dim='time')
    
startTime = ice_mask.time.min().values
endTime = ice_mask.time.max().values
ice_mask.load().to_netcdf(f"oisst_25km_monthly_ice_mask_{pd.to_datetime(startTime).strftime('%Y-%m')}-{pd.to_datetime(endTime).strftime('%Y-%m')}.nc")