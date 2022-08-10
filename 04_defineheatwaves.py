######
# define heatwaves
# this code is for 'historical' and detrend anomalies before calculating heatwaves
######
import xarray
import numpy as np
import pandas as pd
threshold = 0.9
##
sst_an_dt = xarray.load_dataset('oisst_an_1982-2019.nc')

# Find monthly heatwave thresholds for each point
# Use 3-month running window, similar to Hobday et al. 11-day running
# window for daily MHW definition
mergelist=[]
for i in range(1,13):
    if i ==1:
        a=12
        b=i
        c=i+1
        
    elif i==12:
        a=i-1
        b=i
        c=1
    else:
        a=i-1
        b=i
        c=i+1
    temp = sst_an_dt.sel(time=sst_an_dt.time.dt.month.isin([a,b,c]))
    j = temp.__xarray_dataarray_variable__
    jj = j.quantile([threshold], dim='time', skipna=False)
    jj.coords['time2'] = i
    jj.name = "sst_an_thr"
    mergelist.append(jj)
sst_an_thr = xarray.concat([w for w in mergelist],"time2")

# Define heatwave periods
# 用每個月的 anomaly 去跟每個月的thresold(大於90%)比
# 比threshold大 就標記 1
for idx,layer in enumerate(sst_an_dt.time.data):
    ts = pd.to_datetime(layer)
    layermon = int(ts.strftime('%m'))
    tem = sst_an_dt.sel(time=layer)
    thr = sst_an_thr.sel(time2=layermon)
    sst_an_dt.__xarray_dataarray_variable__[idx] = xarray.where((sst_an_dt.__xarray_dataarray_variable__[0].data >= np.squeeze(thr.data, axis=0)),1,0)
sst_an_dt.load().to_netcdf("oisst_mhw_90perc_1982-2019_detrended.nc")