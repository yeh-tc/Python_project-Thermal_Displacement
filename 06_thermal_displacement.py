#text described below are copy from M. Jacox 2020 matlab thermal_displacement.m
# =======================================================
# Calculate horizontal displacement of surface isotherms during
# marine heatwaves
#
#   thermal_displacement(threshold,period,is_detrend,ilims,jlims)
#
# Input:
#   threshold:  SSTa percentile to use for heatwave definition (e.g., 90)
#   period:     'historical' or 'future'
#   is_detrend: 1 to use detrended SST anomalies
#   ilims:      longitude indices to calculate. Full grid is [1 1440]
#   jlims:      latitude indices to calculate. Full grid is [1 720]
#   rcp:        RCP scenario as numeric input (26, 45, or 85)
#               Only required if period is 'future'
#
# Calculating thermal displacements is slow
# Large areas will take a long time to analyze
# =======================================================

import xarray
import numpy as np
import psycopg2
from apply_oisst_masks import apply_oisst_masks
import pandas as pd
from psycopg2.extensions import register_adapter, AsIs
import time
# CALCULATE THERMAL DISPLACEMENT
# Set maximum displacement at distance greater than the largest calculated
# displacements
td_max = 3000 #km
# Load previously calculated SST and heatwave data

#sst
oisst = xarray.load_dataset('OISST_25km_monthly_1981-09-01-2022-06-01.nc')
oisst = oisst.sel(time=slice('1982', '2022')).load()
sst = oisst.sst

#sst anomaly
f_an = xarray.load_dataset('oisst_an_1982-2022.nc')
sst_an = f_an.__xarray_dataarray_variable__


#is heatwave or not file
f_hw = xarray.load_dataset('oisst_mhw_90perc_1982-2019_detrendedof1982_2019.nc')
ishw = f_hw.__xarray_dataarray_variable__

#Load oisst grid distances
d = xarray.load_dataset('oisst_distance.nc').__xarray_dataarray_variable__

#Load oisst masks
mask_all = xarray.load_dataset('oisst_mask.nc')
mask= mask_all.mask

td=sst
#把全部變成nan
td=td.where(td>100)
td.name = "td"
#def addapt_numpy_float32(numpy_float32):
#        return AsIs(numpy_float32)
#register_adapter(np.float32, addapt_numpy_float32)
t1=time.time()
for ii in range(1440):
    for jj in range(720):
        if np.isnan(mask.isel(lon=ii,lat=jj).data) or mask.isel(lon=ii,lat=jj) > 3:
            print(f'ii={ii} jj={jj}')
            # Extract grid distances for this lat/lon
            #這個distance 是特定的點(ii,jj)到各個grid的距離
            d_lat = d.isel(lats = jj, dlon = slice(2879-1440-ii,2879-ii))
            
            # Apply masks for special cases
            d_lat = apply_oisst_masks(ii,jj,d_lat,mask_all)
            #找這個cell所有時間是否為heatwave的資料
            arr = np.array(ishw.isel(lon=ii,lat=jj))
            #如果是1 等於是heatwave
            #ind列出這個cell 有heatwave的月份
            ind = np.where(arr == 1)[0]
            for it in ind:
                #sst_an是比背景平均多出來的溫度(用sst-sst_clim)
                #sst_norm 如果不是heatwave 這個cell應該的溫度
                sst_norm = sst.isel(lon=ii,lat=jj)[it].data-sst_an.isel(lon=ii,lat=jj)[it].data
                #為了下方 filter 轉成 ndarray
                d_tmp=np.array(d_lat)
                #不納入找距離的cell
                #在有heatwave的特定年&月份，全部cell中原本 sst 就 nan(mask1)
                #在有heatwave的特定年&月份，全部cell中其 sst 大於這格的 sst_norm的溫度 因為我們要找的是sst_norm溫度(mask2)
                #距離大於預設的最大距離3000km
                mask1 = np.isnan(sst[it].data)
                mask2 = sst[it].data > sst_norm
                mask3 = d_lat.data > 3000
                d_tmp[np.where(np.logical_or(mask1,mask2))] = np.nan
                d_tmp[np.where(mask3)]=np.nan
                if np.isnan(d_tmp).all():
                    td_fail.isel(lon=ii,lat=jj)[it] = 1
                    td.isel(lon=ii,lat=jj)[it] =np.nan
                    td_ind.isel(lon=ii,lat=jj)[it] =np.nan
                else:
                    td.isel(lon=ii,lat=jj)[it] = np.float32(np.nanmin(d_tmp))
                    td_ind.isel(lon=ii,lat=jj)[it] = np.nanargmin(d_tmp[0])
                    
                 
