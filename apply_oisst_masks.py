import numpy as np
import xarray as xr  # Ensure to import xarray

def apply_oisst_masks(ii, jj, d_lat, mask_all):
    d_lat_T = d_lat.to_numpy().T
    d_lat_T_3d = d_lat_T.reshape((1, 720, 1440))
    mask_all['d_mask'] = (('time', 'lat', 'lon'), d_lat_T_3d)
    
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
        cond = ((mask != 6) & ((mask.lat <= 43) | (mask.lon <= 351)) & (mask.lat <= 48)) 
        mask_with_condition(cond)
        
    elif mask_o == 7:
        mask_with_condition((mask == 7) | (mask == 11))
        
    elif mask_o == 8:
        mask_with_condition((mask == 8) | (mask == 9))
        
    elif mask_o == 9:
        mask_with_condition((mask == 9) | (mask == 7) | (mask == 8) | (mask == 11))
        
    elif mask_o == 10:
        mask_with_condition((mask == 10) | (mask == 11))
        
    elif mask_o == 11:
        mask_with_condition(~((4 <= mask) & (mask <= 6) | (mask == 12)))
        
    elif mask_o == 12:
        mask_with_condition(mask < 9 | mask > 11)
        
    elif mask_o == 13:
        mask_with_condition((mask == 13) | (mask == 14))
        
    elif mask_o == 14:
        mask_with_condition((mask < 15) | (mask > 17) & (mask.lon <= 283))
        
    elif mask_o == 15:
        mask_with_condition((mask != 13) & (mask != 14) & (mask != 17) & ((mask.lon >= 260) & (mask.lon <= 280)))
        
    elif mask_o == 16:
        mask_with_condition((mask != 13) & (mask != 14) & (mask.lon <= 260))
        
    elif mask_o == 17:
        mask_with_condition(mask != 15)
        
    return mask_all['d_mask']