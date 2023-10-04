import xarray
import numpy as np
from apply_oisst_masks import apply_oisst_masks
td_max = 3000 #km
sst = xarray.open_dataset('OISST_25km_monthly_1981-09-01-2023-08-01.nc').sel(time=slice('1982-01-01', '2023-08-01')).sst
sst_an =  xarray.open_dataset('oisst_an_1982-2023.nodetrend.nc').sel(time=slice('1982-01-01', '2023-08-01')).sst_an
f_hw = xarray.open_dataset('oisst_level_1982-2023.nodetrend.nc').sel(time=slice('1982-01-01', '2023-08-01')).level
d = xarray.open_dataset('oisst_distance.nc').__xarray_dataarray_variable__
mask = xarray.open_dataset('oisst_mask.nc')
td=sst.copy()
td = td.where(False)
td.name = "td"
static_mask = (mask.mask > 3) | np.isnan(mask.mask.data)
for ii in range(1440):
    for jj in range(720):
        if static_mask[jj, ii]:
            lon = float(sst_an.lon[ii].data)
            lat = float(sst_an.lat[jj].data)
    
            start_index = d.dlon.size - 1440 - ii 
            end_index = d.dlon.size - ii
            d_lat = d.isel(lats=jj, dlon=slice(start_index, end_index))
            d_lat = apply_oisst_masks(ii, jj, d_lat, mask)
            arr = np.array(f_hw.isel(lon=ii,lat=jj))
            ind = np.where(arr > 0)[0]
            for it in ind:
                sst_norm = sst.isel(lon=ii,lat=jj)[it].data-sst_an.isel(lon=ii,lat=jj)[it].data
                d_tmp=np.array(d_lat)
                mask1 = np.isnan(sst[it].data)
                mask2 = sst[it].data > sst_norm
                mask3 = d_lat.data > 3000
                
                mask1_squeezed = np.squeeze(mask1)
                mask2_squeezed = np.squeeze(mask2)
                mask_combined = np.logical_or(mask1_squeezed, np.logical_or(mask2_squeezed, mask3))
                d_tmp[mask_combined] = np.nan
                
                tdd = np.float32(np.nanmin(d_tmp))
                td.loc[dict(lon=td.lon[ii], lat=td.lat[jj], time=td.time[it])] = tdd
                
td.to_netcdf('oisst_td_result.nc')