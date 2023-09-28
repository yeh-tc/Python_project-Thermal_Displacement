import xarray
import numpy as np

def custom_mean(da: xarray.DataArray):
    return xarray.apply_ufunc(
        lambda x: np.nan if np.isnan(x).any() else np.mean(x),
        da,
        input_core_dims=[['time']],
        vectorize=True
    )

years= [1982,2022]
clim_years=[1982,2011]

oisst_data = xarray.open_dataset('OISST_25km_monthly_1981-09-01-2023-08-01.nc')
ice_mask_data = xarray.open_dataset('oisst_25km_monthly_ice_mask_1981-09-2023-08.nc')
lsm = xarray.open_dataset('../OISST/lsmask.oisst.v2.nc')
lsm = -lsm["lsmask"] + 1

lsm = lsm.where(~((lsm.lon >= 267) & (lsm.lon < 285) & (lsm.lat >= 41) & (lsm.lat <= 50)), 1)  # Great lakes
lsm = lsm.where(~((lsm.lon >= 269.5) & (lsm.lon < 270.5) & (lsm.lat >= 30) & (lsm.lat <= 31)), 1)  # Lake Ponchartrain

for i in range(oisst_data.sst.time.size):
    current_time_slice = oisst_data.sst.isel(time=i)
    ice_mask_slice = ice_mask_data.ice.isel(time=i) 
    
    # Apply masks
    masked_data = current_time_slice.where(lsm == 0, np.nan)  # Apply land mask
    masked_data = masked_data.where(ice_mask_slice == 0, np.nan)  # Apply ice mask
    masked_data = masked_data.squeeze(drop=True)
    
    # Assign the masked data back to the original dataset
    oisst_data.sst[i, :, :] = masked_data
    

# Calculate climatology
#original in Matlab, using mean function(will consider nan and return nan)
#sst_clim = oisst_data.sel(time=slice(str(clim_years[0]), str(clim_years[1]))).groupby('time.month').mean('time')
sst_clim = oisst_data.sel(time=slice(str(clim_years[0]), str(clim_years[1]))).groupby('time.month').apply(custom_mean)
# Calculate anomaly
sst_an = oisst_data.groupby('time.month') - sst_clim
#sst_an
sst_an=sst_an.rename({'sst':'sst_an'})
sst_an.load().to_netcdf(f"oisst_an_1982-2023.nodetrend.nc")