import xarray
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# load land/sea mask
# change from land=0 sea=1 to land=1 sea=0
lsm = xarray.open_dataset('./OISST/lsmask.oisst.v2.nc')
p = -lsm["lsmask"] + 1
ice_mask = xarray.open_dataset('oisst_25km_monthly_ice_mask_1981-09-2023-08.nc')
# If it's land, set to 0
mask = xarray.where(p == 1 , 0 , np.nan)

# Load the ice mask and calculate the average over time
ice_mask_avg = ice_mask['ice'].mean(dim='time',keepdims=True)

# Set permanent sea ice as 1
mask = mask.where(~((ice_mask_avg > 0.9) & np.isnan(mask)), 1)

# Set seasonal sea ice as 2
mask = mask.where(~((ice_mask_avg > 0) & np.isnan(mask)), 2)

# Define a function to mask a specific area within given longitude and latitude range with a value
def mask_area(mask, lon_range, lat_range, value):
    mask_cond = (
        (mask.lon >= lon_range[0])
        & (mask.lon <= lon_range[1])
        & (mask.lat >= lat_range[0])
        & (mask.lat <= lat_range[1])
        & np.isnan(mask)
    )
    mask = mask.where(~mask_cond, value)
    return mask
#Ice-free areas surrounded by sea ice
mask = mask_area(mask, [0, 360], [-90, -63.9], 3) #Antarctica
mask = mask_area(mask, [12, 32], [53.5, 66], 3) #Baltic
mask = mask_area(mask, [9.9, 12], [53, 60], 3) #Baltic
mask = mask_area(mask, [36, 46], [63, 67], 3) #White
mask = mask_area(mask, [14, 24], [77, 81], 3) #Svalbard
mask = mask_area(mask, [50, 190], [60, 88], 3) #Russia
mask = mask_area(mask, [136, 139], [53, 54], 3) #Russia
mask = mask_area(mask, [158, 159], [52, 54], 3) #Russia
mask = mask_area(mask, [160, 163], [57, 60], 3) #Russia
mask = mask_area(mask, [193, 207.8], [57, 68], 3) #Alaska
mask = mask_area(mask, [207, 213], [60, 62], 3) #Alaska
mask = mask_area(mask, [228, 320], [62.5, 85], 3) #Canada/Greenland
mask = mask_area(mask, [267, 284], [51, 63], 3) #Canada
mask = mask_area(mask, [333, 341], [70, 84], 3) #Greenland
mask = mask_area(mask, [338, 345], [64.5, 68], 3) #Iceland
mask = mask_area(mask, [267, 285], [41, 50], 3) #Great Lakes
mask = mask_area(mask, [290, 297], [45, 50], 3) #NW Atlantic
mask = mask_area(mask, [302, 307], [47, 54], 3) #NW Atlantic
#Caspian Sea
mask = mask_area(mask, [46, 56], [36, 48], 4)
#Black Sea
mask = mask_area(mask, [26.8, 42], [40, 48], 5)
#Mediterranean Sea
mask = mask_area(mask, [0, 26.7], [30, 46], 6)
mask = mask_area(mask, [26, 37], [30.5, 39.5], 6)
mask = mask_area(mask, [354, 360], [33, 41], 6)
#Red Sea
mask = mask_area(mask, [32, 43], [12.5, 30], 7)
#Persian Gulf
mask = mask_area(mask, [46, 56], [23, 31], 8)
#Northern Arabian Sea
mask = mask_area(mask, [45, 75], [14, 28], 9)
#Northern Bay of Bengal
mask = mask_area(mask, [77, 99], [14, 25], 10)
#Equatorial Indian Ocean
mask = mask_area(mask, [37, 99], [-5, 15], 11)
mask = mask_area(mask, [99, 100], [-5, 8], 11)
mask = mask_area(mask, [100, 101], [-5, 6.7], 11)
mask = mask_area(mask, [101, 104], [-5, -2], 11)
#South China Sea
mask = mask_area(mask, [98, 120], [-5, 30], 12)
#Northern Gulf of California
mask = mask_area(mask, [244.5, 248], [29.7, 32], 13)
mask = mask_area(mask, [245.5, 249], [29.4, 30], 13)
mask = mask_area(mask, [246, 249], [28.9, 30], 13)
mask = mask_area(mask, [246.5, 252], [27, 30], 13)
mask = mask_area(mask, [247.8, 252], [26.4, 30], 13)
mask = mask_area(mask, [248.2, 252], [25, 30], 13)
#Eastern Tropical Pacific
mask = mask_area(mask, [245, 260], [0, 25], 14)
mask = mask_area(mask, [255, 262], [0, 20], 14)
mask = mask_area(mask, [261, 270], [0, 17], 14)
mask = mask_area(mask, [269, 275.7], [0, 14], 14)
mask = mask_area(mask, [269, 282.8], [0, 7.4], 14)
mask = mask_area(mask, [269, 282], [0, 8.5], 14)
mask = mask_area(mask, [275, 277], [8.4, 9.5], 14)
mask = mask_area(mask, [280, 281.6], [8.4, 9], 14)
mask = mask_area(mask, [245, 295], [-30, 0], 14)
#Northern Gulf of Mexico
mask = mask_area(mask, [260, 278.5], [27, 31], 15)
#Western Tropical Atlantic
mask = mask_area(mask, [260, 315], [-10, 27], 16)
#US East Coast
mask = mask_area(mask, [278.5, 315], [27, 47], 17)

import matplotlib.pyplot as plt
import numpy as np
# After specifying all the mask areas, continue with plotting and setting colormap
#plt.figure()
#plt.pcolormesh(mask.lon, mask.lat, mask.squeeze().data, shading='auto', cmap='jet')
#plt.colorbar(label='Mask Value')
#plt.title('Mask Plot')
#plt.show()
mask_2d=mask.squeeze()
mask_2d.name='mask'
mask_2d.load().to_netcdf(f"oisst_mask.nc")