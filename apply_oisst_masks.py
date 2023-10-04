import numpy as np
import xarray as xr  # Ensure to import xarray

def apply_oisst_masks(ii, jj, d_lat, mask_all):
    d_lat_T = d_lat.to_numpy().T
    mask_all['d_mask'] = (('lat', 'lon'), d_lat_T)
    #d_lat_T_3d = d_lat_T.reshape((1, 720, 1439))
    #mask_all['d_mask'] = (('time', 'lat', 'lon'), d_lat_T_3d)
    
    mask = mask_all['mask']
    mask_o = mask.isel(lon=ii, lat=jj).data
    mask_all['d_mask'] = mask_all['d_mask'].where(mask != 3, np.nan)  # Handle ice-surrounded areas
    
    def mask_with_condition(cond):
        mask_all['d_mask'] = mask_all['d_mask'].where(cond, np.nan)
    
    if mask_o == 4:
        mask_with_condition(mask == 4)
        
    elif mask_o == 5:
        mask_with_condition(mask == 5)
        
    elif mask_o == 6:
       cond = ~( (mask <= 5) | (mask == 7) | (mask == 8) | (mask.lat > 48) | ((mask.lat > 43) & (mask.lon > 351)) )
       mask_with_condition(cond)
       lat_point = mask.lat.isel(lat = jj)
       lon_point = mask.lon.isel(lon = ii)
       
       if 12 < lon_point < 20 and 42.3 < lat_point < 46:
           mask_with_condition(mask == 6)
        
    elif mask_o == 7:
        mask_with_condition((mask == 7) | (mask == 11))
        
    elif mask_o == 8:
        mask_with_condition((mask == 8) | (mask == 9))
        
    elif mask_o == 9:
        mask_with_condition((mask == 7) | (mask == 8) | (mask == 9) | (mask == 11))
        
    elif mask_o == 10:
        mask_with_condition((mask == 10) | (mask == 11))
        
    elif mask_o == 11:
        cond = ~( (mask >= 4) & (mask <= 6) | (mask == 12) )
        mask_with_condition(cond)
        
    elif mask_o == 12:
        cond = ~( (mask >= 9) & (mask <= 11) )
        mask_with_condition(cond)

        
    elif mask_o == 13:
        mask_with_condition((mask == 13) | (mask == 14))
        
    elif mask_o == 14:
        cond = ~( (mask >= 15) & (mask <= 17) | (mask.lon > 283) )
        mask_with_condition(cond)
        
    elif mask_o == 15:
        mask_with_condition((mask != 2) & (mask != 13) & (mask != 14) & (mask != 17) & (mask.lon >= 260) & (mask.lon <= 280))
        
    elif mask_o == 16:
        mask_with_condition((mask != 13) & (mask != 14) & (mask.lon > 260))
        
    elif mask_o == 17:
        mask_with_condition(mask != 15)
        
    return mask_all['d_mask']