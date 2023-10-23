import time
import xarray
import psycopg2
import configparser
import pandas as pd
import numpy as np
from datetime import datetime
from psycopg2.extensions import register_adapter, AsIs
from multiprocessing import Pool,cpu_count
from apply_oisst_masks_new import apply_oisst_masks


config = configparser.ConfigParser()
config.read('config.ini')


now = datetime.now()
MonthNow = int(now.strftime('%m'))
YearNow = int(now.strftime('%Y'))
if (MonthNow > 1):
    MonthStr = str(MonthNow - 1).zfill(2)
else:
    MonthStr = '12'

t0=time.time()
MonthStr = str(MonthNow).zfill(2)

filePath = f'../OISST/*.{YearNow}{MonthStr}*.nc'
print(MonthNow,YearNow)
print(filePath)
ds = xarray.open_mfdataset(filePath, parallel=True,chunks={'time': '500MB'})
mean_month_sst =ds["sst"].resample(time='1MS').mean()
pr_mean_done = mean_month_sst.compute()
pr_mean_done = pr_mean_done.where(pr_mean_done <= 100)
ndays_ice = 15
ice = ds.ice.fillna(0)
ice_binary = xarray.where(ice <= 0, 0, 1)
ice_mask = ice_binary.resample(time='1MS').sum(dim='time')
ice_mask = xarray.where(ice_mask > ndays_ice, 1, 0)
sst_clim = xarray.open_dataset('oisst_sst_clim_1982-2011.nc')
lsm = xarray.open_dataset('../OISST/lsmask.oisst.v2.nc')
lsm = -lsm["lsmask"] + 1
lsm = lsm.where(~((lsm.lon >= 267) & (lsm.lon < 285) & (lsm.lat >= 41) & (lsm.lat <= 50)), 1)  # Great lakes
lsm = lsm.where(~((lsm.lon >= 269.5) & (lsm.lon < 270.5) & (lsm.lat >= 30) & (lsm.lat <= 31)), 1)  # Lake Ponchartrain
for i in range(pr_mean_done.time.size):
    current_time_slice = pr_mean_done.isel(time=i)
    ice_mask_slice = ice_mask.isel(time=i) 
    
    # Apply masks
    masked_data = current_time_slice.where(lsm == 0, np.nan)  # Apply land mask
    masked_data = masked_data.where(ice_mask_slice == 0, np.nan)  # Apply ice mask
    masked_data = masked_data.squeeze(drop=True)
    
    # Assign the masked data back to the original dataset
    pr_mean_done[i, :, :] = masked_data

# Calculate anomaly
month_now=pd.to_datetime(pr_mean_done.time).month[0]
sst_an = pr_mean_done- sst_clim.sel(month=month_now)
sst_an=sst_an.rename({'sst':'sst_an'})

#threshold
sst_an_dt_level = sst_an.copy()
sst_an_thr= xarray.open_dataset('oisst_threshold_1982-2023.nodetrend.nc')
tem = sst_an_dt_level
thr = sst_an_thr.sel(time2=month_now)
a=tem.sst_an.data>np.squeeze(thr.sst_an_thr.data, axis=0)
b=tem.sst_an.data/np.squeeze(thr.sst_an_thr.data, axis=0) < 2
c=tem.sst_an.data/np.squeeze(thr.sst_an_thr.data, axis=0) >= 2
d=tem.sst_an.data/np.squeeze(thr.sst_an_thr.data, axis=0) < 3
e=tem.sst_an.data/np.squeeze(thr.sst_an_thr.data, axis=0) >= 3
f=tem.sst_an.data/np.squeeze(thr.sst_an_thr.data, axis=0) < 4
Extreme=tem.sst_an.data/np.squeeze(thr.sst_an_thr.data, axis=0) >= 4
Moderate=np.logical_and(a, b)
Strong=np.logical_and(c, d)
Severe=np.logical_and(e, f)
sst_an_dt_level["sst_an"].data = xarray.where(Moderate,1,0)
sst_an_dt_level["sst_an"].data[Strong] = 2
sst_an_dt_level["sst_an"].data[Severe] = 3
sst_an_dt_level["sst_an"].data[Extreme] = 4

sst_an_dt_level=sst_an_dt_level.rename({'sst_an':'level'})

#calculate thermal displacement

d = xarray.open_dataset('oisst_distance.nc').__xarray_dataarray_variable__
mask = xarray.open_dataset('oisst_mask.nc')
sst_an =  sst_an.sst_an
f_hw = sst_an_dt_level.level
sst = pr_mean_done
static_mask = (mask.mask > 3) | np.isnan(mask.mask.data)
td_max = 3000 #km
td=pr_mean_done.copy()
td = td.where(False)
td.name = "td"
t1=time.time()
def process_chunk(ii_range):
    results = {}

    for ii in ii_range:
        for jj in range(720):
            if static_mask[jj, ii]:
                lon = float(sst_an.lon[ii].data)
                lat = float(sst_an.lat[jj].data)
                start_index = d.dlon.size - 1440 - ii 
                end_index = d.dlon.size - ii
                d_lat = d.isel(lats=jj, dlon=slice(start_index, end_index))
                d_lat = apply_oisst_masks(ii, jj, d_lat, mask)
                if f_hw.isel(lon=ii, lat=jj) > 0:
                    sst_norm = sst.isel(lon=ii, lat=jj).data - sst_an.isel(lon=ii, lat=jj).data
                    d_tmp = np.array(d_lat)
                    mask1 = np.isnan(sst.data)
                    mask2 = sst.data > sst_norm
                    mask3 = d_lat.data > 3000
                    mask1_squeezed = np.squeeze(mask1)
                    mask2_squeezed = np.squeeze(mask2)
                    mask_combined = np.logical_or(mask1_squeezed, np.logical_or(mask2_squeezed, mask3))
                    d_tmp[mask_combined] = np.nan
                    if np.isnan(d_tmp).all():
                        results[(lon, lat)] = np.nan
                    else:
                        results[(lon, lat)] = np.float32(np.nanmin(d_tmp))
    return results

# Splitting work for processors
num_processes = cpu_count()
ranges = np.array_split(range(1440), num_processes)
print('processes')
with Pool(processes=num_processes) as pool:
    result_list = pool.map(process_chunk, ranges)

for single_process_result in result_list:
    for (lon, lat), value in single_process_result.items():
        td.loc[dict(lon=lon, lat=lat)] = value
t2=time.time()
print(f'{YearNow}{MonthStr} one month td finish in {(t2-t1)/60}')


df_Grid=pd.read_csv('Gid.csv')
date = str(sst_an.time.values[0])[:10]
print(date)
gid_lookup = {(row['lat'], row['lon']): row['gid'] for _, row in df_Grid.iterrows()}
print('finish looking up')

sst_data = sst.data[0,0]
f_hw_data = f_hw.data[0,0]
sst_an_data = sst_an.data[0,0]
sst_an_data_rounded = np.around(sst_an_data, 4)
ice_data = ice_mask.data[0,0]
ice_data_np = ice_data.compute()
td_data = td.data[0,0]
td_data_64 = td_data.astype(np.float64)
tdd_rounded = np.around(td_data_64, 4)

print('prepare data for database')

records=[]
for ii in range(1440):
    for jj in range(720):
        lat=sst_an.lat[jj].data.item()
        lon=sst_an.lon[ii].data.item()
        anomaly=sst_an_data_rounded[jj, ii].item()
        #date
        ice=ice_data_np[jj, ii].item()
        level=f_hw_data[jj, ii].item()
        if ice == 1:
            level=-1
        tdd=tdd_rounded[jj, ii].item()
        gid=int(gid_lookup.get((lat, lon)))
        result = tuple([lat,lon,anomaly,date,level,tdd,gid])
        records.append(result)

print(f'Insert data to database')

t3=time.time()
def addapt_numpy_float32(numpy_float32):
        return AsIs(numpy_float32)
register_adapter(np.float32, addapt_numpy_float32)
conn = psycopg2.connect(
database=config['postgresql']['database'],
user=config['postgresql']['user'],
password=config['postgresql']['password'],
host=config['postgresql']['host'],
port=config['postgresql']['port']
)

cursor = conn.cursor()
args = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s)", i).decode('utf-8') for i in records )
sql = 'INSERT INTO sst_anomaly_without_detrend (lat, lon, sst_anomaly,date,level,td,gid) VALUES '+ args
cursor.execute(sql)
conn.commit()
cursor.close()

t4=time.time()
print(f' finished postgres part in {t4-t3} s')
print(f' Totall progress in {(t4-t0)/60} min')