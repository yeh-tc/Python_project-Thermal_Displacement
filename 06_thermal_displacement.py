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
import apply_oisst_masks
import datetime
import pandas as pd
from psycopg2.extensions import register_adapter, AsIs
from multiprocessing import Pool
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
#其實也可以不用td 可以用sst就好
td=sst
#把全部變成nan
td=td.where(td>100)
td.name = "td"

#sst anomaly
f_an = xarray.load_dataset('oisst_an_1982-2022.nc')
sst_an = f_an.__xarray_dataarray_variable__


#is heatwave or not file
f_hw = xarray.load_dataset('oisst_mhw_90perc_1982-2022_detrended.nc')
ishw = f_hw.__xarray_dataarray_variable__

#Load oisst grid distances
d = xarray.load_dataset('oisst_distance.nc').__xarray_dataarray_variable__

#Load oisst masks
mask_all = xarray.load_dataset('oisst_mask.nc')
mask= mask_all.mask

def cal_td(ii):
    #為了寫進資料庫
    #psycopg2不接受 numpy float32
    def addapt_numpy_float32(numpy_float32):
        return AsIs(numpy_float32)
    register_adapter(np.float32, addapt_numpy_float32)
    for jj in range(720):
            if np.isnan(mask.isel(lon=ii,lat=jj).data) or mask.isel(lon=ii,lat=jj) > 3:
                print(f'ii={ii} jj={jj}')
                d_lat = d.isel(lats = jj, dlon = slice(2879-1440-ii,2879-ii))
                d_lat = apply_oisst_masks(ii,jj,d_lat,mask_all)
                arr = np.array(ishw.isel(lon=ii,lat=jj))
                ind = np.where(arr == 1)[0]
                for it in ind:
                    sst_norm = sst.isel(lon=ii,lat=jj)[it].data-sst_an.isel(lon=ii,lat=jj)[it].data
                    d_tmp=np.array(d_lat)
                    mask1 = np.isnan(sst[it].data)
                    mask2 = sst[it].data > sst_norm
                    mask3 = d_lat.data > 3000
                    d_tmp[np.where(np.logical_or(mask1,mask2))] = np.nan
                    d_tmp[np.where(mask3)]=np.nan
                    if np.isnan(d_tmp).all():
                        print('nan')
                        #td.isel(lon=ii,lat=jj)[it] =np.nan
                    else:
                        #td.isel(lon=ii,lat=jj)[it] = np.float32(np.nanmin(d_tmp))
                        lon = float(td.lon[ii].data)
                        lat = float(td.lat[jj].data)
                        tdd = np.float32(np.nanmin(d_tmp))
                        x = pd.to_datetime(td.time[it].values).date()
                        conn = psycopg2.connect(database="postgres", user="postgres", password=*****, host="127.0.0.1", port="5432")
                        cursor = conn.cursor()
                        sql = "INSERT INTO td (lat, lon, distance,date) VALUES (%s, %s, %s, %s);" # Note: no quotes
                        data = (lat,lon,tdd, x)
                        #print(data)
                        
                        
                        cursor.execute(sql,data)
                        conn.commit()
                        cursor.close()


t1=time.time()
#import multiprocessing
#cpus = multiprocessing.cpu_count()
pool = Pool(7)
pool.map(cal_td, range(1440))
t2=time.time()
print(t2-t1)