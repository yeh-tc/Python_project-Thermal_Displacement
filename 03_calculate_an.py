import datetime
import xarray
import numpy as np
# ranges of years to be analyzed
year_start ='1982'
year_end = '2022'
# range of years to use for climatology
clim_years_start = '1982'
clim_years_end = '2011'
#####
# load sst data and ice mask
#####
oisst = xarray.open_dataset('OISST_25km_monthly_1981-09-01-2022-06-01.nc')
ice_mask = xarray.open_dataset('oisst_25km_monthly_ice_mask_1981-09-01-2022-06-01.nc')
oisst = oisst.sel(time=slice(year_start, year_end)).load()
icemask = ice_mask.sel(time=slice(year_start, year_end)).load()
# load land/sea mask
# change from land=0 sea=1 to land=1 sea=0
lsm = xarray.open_dataset('./OISST/lsmask.oisst.v2.nc')
p = -lsm["lsmask"].data + 1
# append back to dataset then can use lon and lat condition
lsm['mask']=(('time','lat','lon'),p)
# treat some water bodies as land
# Great lakes
temp=lsm['mask'].where((lsm['mask'].lon >= 267) & (lsm['mask'].lon < 285) & (lsm['mask'].lat >= 41) & (lsm['mask'].lat <= 50),other=50).data
lsm['mask'].data[temp != 50] = 1
# Lake Ponchartrain
temp=lsm['mask'].where((lsm['mask'].lon >= 269.5) & (lsm['mask'].lon < 270.5) & (lsm['mask'].lat >= 30) & (lsm['mask'].lat <= 31),other=50).data
lsm['mask'].data[temp != 50] = 1
# apply land mask amd ice mask
for i in range(oisst.sst.time.size):
    oisst.sst[i].where(lsm['mask']!=1,np.nan)
    oisst.sst[i].where(icemask['ice'][i]!=1,np.nan)
# calculate anomalies
oisst_clim = oisst.sel(time=slice(clim_years_start, clim_years_end)).load()
sst_anom = oisst.sst.groupby('time.month') - oisst_clim.sst.groupby('time.month').mean(dim='time')
#detrend function
def detrend_dim(da, dim, deg=1):
    # detrend along a single dimension
    p = da.polyfit(dim=dim, deg=deg)
    fit = xarray.polyval(da[dim], p.polyfit_coefficients)
    return da - fit
de_sst_anom = detrend_dim(sst_anom,'time',1)
de_sst_anom.load().to_netcdf(f"oisst_an_{year_start}-{year_end}.nc")
