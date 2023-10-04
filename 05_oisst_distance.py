import pandas as pd
import xarray
import numpy as np
import time
from numpy.linalg import multi_dot
##text described below are copy from M. Jacox 2020 matlab
##Create matrix of distances between points on the OISST grid
##For each latitude, a grid of 2879 x 720 distances is created
##The matrix is subset as necessary in thermal_displacement.m
f_grid = xarray.open_dataset('./OISST/lsmask.oisst.v2.nc')
lon = np.array(f_grid['lon'])
lat = np.array(f_grid['lat'])

# Earth's radius in km
Re = 6371
#Get grid parameters for calculation
res = lon[2] - lon[1]
lats = np.deg2rad(np.arange(min(lat),max(lat)+res,res))
dlon = np.deg2rad(np.arange(min(lon)-max(lon),max(lon)-min(lon)+res,res))
lat_mat = np.tile(lats, (len(dlon), 1))
dlon_mat = np.tile(dlon,(len(lats),1)).T
#Loop through each latitude and calculate distance to all other points
t1=time.time()
d=np.zeros((len(lats),len(dlon),len(lats)))
for ilat in range(len(lats)):
    d[ilat,:,:] = np.real(np.array(Re).dot(np.arccos(np.array(np.sin(lats[ilat])).dot(np.sin(lat_mat))+np.array(np.cos(lats[ilat])).dot(np.cos(lat_mat))*np.cos(dlon_mat))))
    
df = xarray.DataArray(d, coords=[('lats', lats), ('dlon', dlon),('lat',lats)])
df.to_netcdf('oisst_distance.nc')