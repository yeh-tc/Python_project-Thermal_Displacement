def apply_oisst_masks(ii,jj,d_lat,mask_all):
    #
    #text described below are copy from M. Jacox 2020 matlab apply_oisst_masks.m
    #====================================================
    #Inputs:
    #   ii: longitude index on OISST grid
    #   jj: latitude index on OISST grid
    #   d:  matrix of distances to all other OISST grid cells
    #       from point (ii,jj). Dimensions are [lon lat]
    #   mask: mask defining regions, created by make_oisst_masks.m (here is 02_make_mask.py)
    #          Dimensions are [lon lat]
    #   lat:  Matrix of OISST latitudes
    #   lon:  Matrix of OISST longitudes
    #
    #Output:
    #    d_mask: matrix of distances with unavailable locations masked out
    #
    # This function limits the locations that are classified
    # as available for thermal displacements (e.g., for heatwaves
    # in the Caspian Sea the thermal displacement cannot be outside
    # the Caspian Sea.
    #
    # Exclusions are mostly based on the mask created in
    # make_oisst_masks.m. As is the case for that script, this one
    # could be modified to change which regions are considered
    # accessible from any given location. 
    #
    # Masks applied are below, with numbers referring to regions in 
    # the mask file
    #
    # 4: Caspian Sea
    #   only 4
    #
    # 5: Black Sea
    #   only 5
    #
    # 6: Mediterranean Sea
    #   exclude 2-5,7-8, >48N, >43N & >351
    #   For northern Adriatic, only Med Sea
    # 
    # 7: Red Sea
    #   only 7,11
    #
    # 8: Persian Gulf
    #   only 8,9
    #
    # 9: Northern Arabian Sea
    #   only 7,8,9,11
    # 
    # 10: Northern Bay of Bengal
    #   only 10,11
    #
    # 11: Equatorial Indian Ocean
    #   exclude 4-6,12
    #
    # 12: South China Sea
    #   exclude 9-11
    # 
    # 13: Northern Gulf of California
    #   limit to Gulf + ETP
    #
    # 14: Eastern Tropical Pacific
    #   exclude 15-17, >283
    #
    # 15: Northern Gulf of Mexico
    #   exclude 13,14,17, N. Pacific, seasonal sea ice, >280
    #
    # 16: Western Tropical Atlantic
    #   exclude 13,14, N. Pacific
    #
    # 17: US East Coast
    #   exclude 15
    # ====================================================
    
    
    #把要 mask 的 distance (d_mask) 放進去原本 mask Dataset內

    #把它變成shape(720,1440)
    d_lat_T=d_lat.to_numpy().T

    #增加一個維度
    d_lat_T_3d = d_lat_T.reshape((1, 720, 1440))

    #加進去
    mask_all['d_mask'] = (('time', 'lat', 'lon'),d_lat_T_3d)
    mask=mask_all.mask
    # Exclude ice-surrounded areas
    mask_all['d_mask'].data[mask.data == 3] = np.nan

    # Handle regional cases
    mask_o = mask.isel(lon = ii,lat = jj).data
    if mask_o == 4:
        mask_all['d_mask'].data[mask.data!=4] = np.nan
    elif mask_o == 5:
        mask_all['d_mask'].data[mask.data!=5] = np.nan
    elif mask_o == 6:
    #先建立經緯度範圍的一個暫時的 DataArray
        temp = mask_all['mask'].where((mask.lat > 43) & (mask.lon > 351) ,other = 50).data
        temp2 = mask_all['mask'].where((mask.lat > 48) ,other=50).data
        mask_all['d_mask'].data[np.logical_or(mask.data <= 5, mask.data == 7, mask.data == 8)] = np.nan
        mask_all['d_mask'].data[np.logical_or(temp != 50,temp2 != 50)] = np.nan
        lat_point = mask.lat.isel(lat = jj)
        lon_point = mask.lon.isel(lon = ii)
        if lon_point > 12 and lon_point < 20 and lat_point > 42.3 and lat_point < 46:
            mask_all['d_mask'].data[mask.data != 6] = np.nan
    elif mask_o == 7:
        mask_all['d_mask'].data[np.logical_or(mask.data != 7, mask.data != 11)] = np.nan
    elif mask_o == 8:
        mask_all['d_mask'].data[np.logical_or(mask.data != 8, mask.data != 9)] = np.nan
    elif mask_o == 9:
        mask_all['d_mask'].data[np.logical_or(mask.data != 7, mask.data != 8)] = np.nan
        mask_all['d_mask'].data[np.logical_or(mask.data != 9, mask.data != 11)] = np.nan
    elif mask_o == 10:
        mask_all['d_mask'].data[np.logical_or(mask.data != 10, mask.data != 11)] = np.nan
    elif mask_o == 11:
        mask_all['d_mask'].data[np.logical_or((mask.data >= 4) & (mask.data <=6), mask.data == 12)] = np.nan
    elif mask_o == 12:
        mask_all['d_mask'].data[np.logical_or(mask.data >= 9, mask.data <= 11)] = np.nan
    elif mask_o == 13:
        mask_all['d_mask'].data[np.logical_or(mask.data != 13, mask.data != 14)] = np.nan
    elif mask_o == 14:
        temp = mask_all['mask'].where((mask.lon > 283) ,other = 50).data
        mask_all['d_mask'].data[np.logical_or((mask.data >= 15) & (mask.data <=17), temp != 50)] = np.nan
    elif mask_o == 15:
        temp = mask_all['mask'].where((mask.lon < 260) | (mask.lon > 280),other = 50).data
        mask_all['d_mask'].data[np.logical_or(mask.data == 2, mask.data == 13, mask.data == 14)] = np.nan
        mask_all['d_mask'].data[np.logical_or(mask.data == 17, temp != 50)] = np.nan
    elif mask_o == 16:
        temp = mask_all['mask'].where((mask.lon > 260) ,other = 50).data
        mask_all['d_mask'].data[np.logical_or(mask.data == 13, mask.data == 14, temp != 50)] = np.nan
    elif mask_o == 17:
        mask_all['d_mask'].data[mask.data == 15] = np.nan
    return mask_all['d_mask']