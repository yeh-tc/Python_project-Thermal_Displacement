import numpy as np
import xarray as xr
import time

f_grid = xr.open_dataset('./OISST/lsmask.oisst.v2.nc')
lon = f_grid['lon'].values
lat = f_grid['lat'].values

Re = 6371  # Earth's radius in km
res = lon[1] - lon[0]  # Get grid parameters for calculation

lats = np.arange(lat.min(), lat.max() + res, res)
dlon = np.concatenate([lon[-1] - lon[:-1] + res, lon])
lat_mat, dlon_mat = np.meshgrid(lats, dlon)
d = np.empty((len(lats), len(dlon), len(lats)))
start_time = time.time()
for ilat, current_lat in enumerate(lats):
        # Calculate distance to all other points
    d[ilat, :, :] = Re * np.arccos(
        np.sin(np.deg2rad(current_lat)) * np.sin(np.deg2rad(lat_mat)) +
        np.cos(np.deg2rad(current_lat)) * np.cos(np.deg2rad(lat_mat)) * np.cos(np.deg2rad(dlon_mat))
    )

    # Periodically report status
    if ilat % (len(lats) // 20) == 0:
        elapsed_time = (time.time() - start_time) / 60
        print(f"{100 * ilat / len(lats):.0f}% done, {elapsed_time:.0f} min elapsed")

    # Convert the array to xarray DataArray for saving
d_da = xr.DataArray(
    d.astype(np.float32),
    coords={"lats": lats, "dlon": dlon, "lat": lats},
    dims=["lats", "dlon", "lat"]
)
d_da.to_netcdf(fout)

d = np.zeros((len(lats), len(dlon), len(lats)))
d_da.to_netcdf('oisst_distance.nc')
