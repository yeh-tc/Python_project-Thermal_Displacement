import xarray
import numpy as np
import pandas as pd

sst_an_dt = xarray.open_dataset('oisst_an_1982-2023.nodetrend.nc')
sst_an_dt_level = sst_an_dt.copy()
# Define the threshold value
threshold = 0.9

# Extract climatology
sst_an_dt_clim = sst_an_dt.sel(time=slice('1982-01-01', '2011-12-01'))
variable_name = list(sst_an_dt.data_vars.keys())[0]
mergelist = []
for i in range(1, 13):
    months = [i % 12 + 1, i, (i + 1) % 12 + 1]
    temp = sst_an_dt_clim.sel(time=sst_an_dt_clim.time.dt.month.isin(months))
    j = temp[variable_name]
    #the result of clim is more close to author's result by using xarray quantile function than using np.nanquantile
    jj = j.quantile([threshold], dim='time', skipna=True, method='midpoint') #in matlab, the prctile function will skip nan
    jj = jj.assign_coords(time2=i).rename("sst_an_thr")
    mergelist.append(jj)
    
sst_an_thr = xarray.concat(mergelist, "time2")
for idx, layer in enumerate(sst_an_dt_level.time.data):
    ts = pd.to_datetime(layer)
    layermonth = int(ts.strftime('%m'))
    tem = sst_an_dt_level.sel(time=layer)
    thr = sst_an_thr.sel(time2=layermonth)
    a=tem.sst_an.data>np.squeeze(thr.data, axis=0)
    b=tem.sst_an.data/np.squeeze(thr.data, axis=0) < 2
    c=tem.sst_an.data/np.squeeze(thr.data, axis=0) >= 2
    d=tem.sst_an.data/np.squeeze(thr.data, axis=0) < 3
    e=tem.sst_an.data/np.squeeze(thr.data, axis=0) >= 3
    f=tem.sst_an.data/np.squeeze(thr.data, axis=0) < 4
    Extreme=tem.sst_an.data/np.squeeze(thr.data, axis=0) >= 4
    Moderate=np.logical_and(a, b)
    Strong=np.logical_and(c, d)
    Severe=np.logical_and(e, f)
    sst_an_dt_level.sst_an[idx] = xarray.where(Moderate,1,0)
    sst_an_dt_level.sst_an[idx].data[Strong] = 2
    sst_an_dt_level.sst_an[idx].data[Severe] = 3
    sst_an_dt_level.sst_an[idx].data[Extreme] = 4
    
sst_an_dt_level.load().to_netcdf(f"oisst_level_1982-2023_2023.nodetrend.nc")
sst_an_thr.load().to_netcdf(f"oisst_threshold_1982-2023_2023.nodetrend.nc")