import numpy as np
import xarray as xr
import time

f_grid = xr.open_dataset('./OISST/lsmask.oisst.v2.nc')
lon = f_grid['lon'].values
lat = f_grid['lat'].values

Re = 6371  # Earth's radius in km
res = lon[1] - lon[0]  # Get grid parameters for calculation

lats = np.arange(np.deg2rad(min(lat)), np.deg2rad(max(lat) + res), np.deg2rad(res))
dlon = np.arange(np.deg2rad(min(lon) - max(lon)), np.deg2rad(max(lon) - min(lon) + res), np.deg2rad(res))

lat_mat = np.tile(lats, (len(dlon), 1))
dlon_mat = np.tile(dlon, (len(lats), 1)).T

d = np.zeros((len(lats), len(dlon), len(lats)))

t1 = time.time()

for ilat, lat_val in enumerate(lats):
    d[ilat, :, :] = Re * np.arccos(np.sin(lat_val) * np.sin(lat_mat) + np.cos(lat_val) * np.cos(lat_mat) * np.cos(dlon_mat))

df = xr.DataArray(d, coords=[('lats', lats), ('dlon', dlon), ('lat', lats)])
df.to_netcdf('oisst_distance2.nc')

print("Time elapsed: ", time.time() - t1)