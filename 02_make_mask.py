import xarray
import numpy as np
# load land/sea mask
# change from land=0 sea=1 to land=1 sea=0
lsm = xarray.open_dataset('./OISST/lsmask.oisst.v2.nc')
p = -lsm["lsmask"].data + 1 #this step is following the original author...


ice_mask = xarray.open_dataset('oisst_25km_monthly_ice_mask_1982-01-01-2019-12-31.nc')
ice_mask_avg = ice_mask['ice'].mean('time').data

# mask land as 0
mask = xarray.where(p == 1 , 0 , np.nan)

# mask permanent sea ice as 1
mask[np.logical_and(ice_mask_avg > 0.9, np.isnan(mask))] = 1
# mask seasonal sea ice as 2
mask[np.logical_and(ice_mask_avg > 0, np.isnan(mask))] = 2
# append back to dataset then can use lon and lat condition
lsm['mask']=(('time','lat','lon'),mask)

# Ice-free areas surrounded by sea ice
# mask as 3
# Antarctica
icemask = lsm['mask'].where(lsm['mask'].lat < -63.9,other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Baltic
icemask = lsm['mask'].where((lsm['mask'].lon > 12) & (lsm['mask'].lon < 32) & (lsm['mask'].lat > 53.5) & (lsm['mask'].lat <= 66),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Baltic
icemask = lsm['mask'].where((lsm['mask'].lon > 9.9) & (lsm['mask'].lon < 12) & (lsm['mask'].lat > 53) & (lsm['mask'].lat <= 60),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# White
icemask = lsm['mask'].where((lsm['mask'].lon > 36) & (lsm['mask'].lon < 46) & (lsm['mask'].lat > 63) & (lsm['mask'].lat <= 67),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Svalbard
icemask = lsm['mask'].where((lsm['mask'].lon > 14) & (lsm['mask'].lon < 24) & (lsm['mask'].lat > 77) & (lsm['mask'].lat <= 81),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Russia
icemask = lsm['mask'].where((lsm['mask'].lon > 50) & (lsm['mask'].lon < 190) & (lsm['mask'].lat > 60) & (lsm['mask'].lat <= 88),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Russia
icemask = lsm['mask'].where((lsm['mask'].lon > 136) & (lsm['mask'].lon < 139) & (lsm['mask'].lat > 53) & (lsm['mask'].lat <= 54),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Russia
icemask = lsm['mask'].where((lsm['mask'].lon > 158) & (lsm['mask'].lon < 159) & (lsm['mask'].lat > 52) & (lsm['mask'].lat <= 54),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Russia
icemask = lsm['mask'].where((lsm['mask'].lon > 160) & (lsm['mask'].lon < 163) & (lsm['mask'].lat > 57) & (lsm['mask'].lat <= 60),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Alaska
icemask = lsm['mask'].where((lsm['mask'].lon > 193) & (lsm['mask'].lon < 207.8) & (lsm['mask'].lat > 57) & (lsm['mask'].lat <= 68),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Alaska
icemask = lsm['mask'].where((lsm['mask'].lon > 207) & (lsm['mask'].lon < 213) & (lsm['mask'].lat > 60) & (lsm['mask'].lat <= 62),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Canada/Greenland
icemask = lsm['mask'].where((lsm['mask'].lon > 228) & (lsm['mask'].lon < 320) & (lsm['mask'].lat > 62.5) & (lsm['mask'].lat <= 85),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Canada
icemask = lsm['mask'].where((lsm['mask'].lon > 267) & (lsm['mask'].lon < 284) & (lsm['mask'].lat > 51) & (lsm['mask'].lat <= 63),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Greenland
icemask = lsm['mask'].where((lsm['mask'].lon > 333) & (lsm['mask'].lon < 341) & (lsm['mask'].lat > 70) & (lsm['mask'].lat <= 84),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Iceland
icemask = lsm['mask'].where((lsm['mask'].lon > 338) & (lsm['mask'].lon < 345) & (lsm['mask'].lat > 64.5) & (lsm['mask'].lat <= 68),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Great Lakes
icemask = lsm['mask'].where((lsm['mask'].lon > 267) & (lsm['mask'].lon < 285) & (lsm['mask'].lat > 41) & (lsm['mask'].lat <= 50),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# NW Atlantic
icemask = lsm['mask'].where((lsm['mask'].lon > 290) & (lsm['mask'].lon < 297) & (lsm['mask'].lat > 45) & (lsm['mask'].lat <= 50),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# NW Atlantic
icemask = lsm['mask'].where((lsm['mask'].lon > 302) & (lsm['mask'].lon < 307) & (lsm['mask'].lat > 47) & (lsm['mask'].lat <= 54),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 3
# Caspian Sea
icemask = lsm['mask'].where((lsm['mask'].lon >= 46) & (lsm['mask'].lon <= 56) & (lsm['mask'].lat >= 36) & (lsm['mask'].lat <= 48),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 4
# Black Sea
icemask = lsm['mask'].where((lsm['mask'].lon >= 26.8) & (lsm['mask'].lon <= 42) & (lsm['mask'].lat >= 40) & (lsm['mask'].lat <= 48),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 5
# Mediterranean Sea
icemask = lsm['mask'].where((lsm['mask'].lon <= 26.7) & (lsm['mask'].lat >= 30) & (lsm['mask'].lat <= 46),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 6
icemask = lsm['mask'].where((lsm['mask'].lon >= 26) & (lsm['mask'].lon <= 37) & (lsm['mask'].lat >= 30.5) & (lsm['mask'].lat <= 39.5),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 6
icemask = lsm['mask'].where((lsm['mask'].lon >= 354) & (lsm['mask'].lat >= 33) & (lsm['mask'].lat <= 41),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 6
# Red Sea
icemask = lsm['mask'].where((lsm['mask'].lon >= 32) & (lsm['mask'].lon <= 43) & (lsm['mask'].lat >= 12.5) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 7
# Persian Gulf
icemask = lsm['mask'].where((lsm['mask'].lon >= 46) & (lsm['mask'].lon < 56) & (lsm['mask'].lat >= 23) & (lsm['mask'].lat <= 13),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 8
# Northern Arabian Sea
icemask = lsm['mask'].where((lsm['mask'].lon >= 45) & (lsm['mask'].lon < 75) & (lsm['mask'].lat >= 14) & (lsm['mask'].lat <= 28),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 9
# Northern Bay of Bengal
icemask = lsm['mask'].where((lsm['mask'].lon >= 77) & (lsm['mask'].lon < 99) & (lsm['mask'].lat >= 14) & (lsm['mask'].lat <= 25),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 10
# Equatorial Indian Ocean
icemask = lsm['mask'].where((lsm['mask'].lon >= 37) & (lsm['mask'].lon < 99) & (lsm['mask'].lat >= -5) & (lsm['mask'].lat <= 15),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 11
icemask = lsm['mask'].where((lsm['mask'].lon >= 99) & (lsm['mask'].lon <= 100) & (lsm['mask'].lat >= -5) & (lsm['mask'].lat < 8),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 11
icemask = lsm['mask'].where((lsm['mask'].lon > 100) & (lsm['mask'].lon <= 101) & (lsm['mask'].lat >= -5) & (lsm['mask'].lat < 6.7),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 11
icemask = lsm['mask'].where((lsm['mask'].lon > 101) & (lsm['mask'].lon <= 104) & (lsm['mask'].lat >= -5) & (lsm['mask'].lat < -2),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 11
# South China Sea
icemask = lsm['mask'].where((lsm['mask'].lon >= 98) & (lsm['mask'].lon < 120) & (lsm['mask'].lat >= -5) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 12
# Northern Gulf of California
icemask = lsm['mask'].where((lsm['mask'].lon >= 244.5) & (lsm['mask'].lon < 248) & (lsm['mask'].lat >= 29.7) & (lsm['mask'].lat <= 32),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 13
icemask = lsm['mask'].where((lsm['mask'].lon >= 245.5) & (lsm['mask'].lon < 249) & (lsm['mask'].lat >= 29.4) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 13
icemask = lsm['mask'].where((lsm['mask'].lon >= 246) & (lsm['mask'].lon < 249) & (lsm['mask'].lat >= 28.9) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 13
icemask = lsm['mask'].where((lsm['mask'].lon >= 246.5) & (lsm['mask'].lon < 252) & (lsm['mask'].lat >= 27) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 13
icemask = lsm['mask'].where((lsm['mask'].lon >= 247.8) & (lsm['mask'].lon < 252) & (lsm['mask'].lat >= 26.4) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 13
icemask = lsm['mask'].where((lsm['mask'].lon >= 248.2) & (lsm['mask'].lon < 252) & (lsm['mask'].lat >= 25) & (lsm['mask'].lat <= 30),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 13
# Eastern Tropical Pacific
icemask = lsm['mask'].where((lsm['mask'].lon >= 245) & (lsm['mask'].lon < 260) & (lsm['mask'].lat >= 0) & (lsm['mask'].lat <= 25),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 255) & (lsm['mask'].lon < 262) & (lsm['mask'].lat >= 0) & (lsm['mask'].lat <= 20),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 261) & (lsm['mask'].lon < 270) & (lsm['mask'].lat >= 0) & (lsm['mask'].lat <= 17),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 269) & (lsm['mask'].lon < 275.7) & (lsm['mask'].lat >= 0) & (lsm['mask'].lat <= 14),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 269) & (lsm['mask'].lon < 282.8) & (lsm['mask'].lat >= 0) & (lsm['mask'].lat <= 7.4),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 269) & (lsm['mask'].lon < 282) & (lsm['mask'].lat >= 0) & (lsm['mask'].lat <= 8.5),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 275) & (lsm['mask'].lon < 277) & (lsm['mask'].lat >= 8.4) & (lsm['mask'].lat <= 9.5),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 280) & (lsm['mask'].lon < 281.6) & (lsm['mask'].lat >= 8.4) & (lsm['mask'].lat <= 9),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
icemask = lsm['mask'].where((lsm['mask'].lon >= 245) & (lsm['mask'].lon < 295) & (lsm['mask'].lat >= -30) & (lsm['mask'].lat <= 0),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 14
# Northern Gulf of Mexico
icemask = lsm['mask'].where((lsm['mask'].lon >= 260) & (lsm['mask'].lon < 278.5) & (lsm['mask'].lat >= 27) & (lsm['mask'].lat <= 31),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 15
# Western Tropical Atlantic
icemask = lsm['mask'].where((lsm['mask'].lon >= 260) & (lsm['mask'].lon < 315) & (lsm['mask'].lat >= -10) & (lsm['mask'].lat <= 27),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 16
# US East Coast
icemask = lsm['mask'].where((lsm['mask'].lon >= 278.5) & (lsm['mask'].lon < 315) & (lsm['mask'].lat >= 27) & (lsm['mask'].lat <= 47),other=50).data
lsm['mask'].data[np.logical_and(icemask != 50, np.isnan(lsm['mask'].data))] = 17

lsm.load().to_netcdf(f"oisst_mask.nc")