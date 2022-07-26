import glob
import pandas as pd
import xarray
import time
from dask.distributed import Client


# input nc file
filePath='./OISST/*.????????.nc'

# time range for climatology
#startTime = '1982-01-01'
#endTime = '2019-12-31'

# filename to datetime
#def filename_to_datetime(filename):
#    filedate = re.match(r'.*(\d{8}).nc',filename)
#    if filedate:
#        return datetime.datetime.strptime(filedate.group(1),'%Y%m%d')
#    else:
#        return datetime.datetime.strptime('1700-01-01',"%Y-%m-%d")
    
# check if the file is within the time range 
#def get_time(start_time, end_time):
#    return [file for file in glob.glob(filePath) 
#            if datetime.datetime.strptime(start_time,"%Y-%m-%d") < filename_to_datetime(file) < datetime.datetime.strptime(end_time,"%Y-%m-%d")]

#fileForMerge = get_time(startTime, endTime)

fileForMerge=[file for file in glob.glob(filePath)]

print('Merging files')
tic = time.time()
#client = Client()
ds2 = xarray.open_mfdataset(fileForMerge, parallel=True,chunks={'time': '500MB'})
toc = time.time()
print('Finish Merging..in {:.4f} mins'.format((toc-tic)/60))
print('################')

print('Calculate sst monthly mean')
mean_month_sst =ds2["sst"].resample(time='1MS').mean()
pr_mean_done = mean_month_sst.compute()
#mean_month_sst =ds2.groupby('time.month').mean(skipna=True,dim="time")
startTime = pd.to_datetime(str(pr_mean_done.time.min().data)).strftime('%Y-%m-%d')
endTime = pd.to_datetime(str(pr_mean_done.time.max().data)).strftime('%Y-%m-%d')
print('Saving sst mean')
pr_mean_done.load().to_netcdf(f"OISST_25km_monthly_{startTime}-{endTime}.nc")
#mean_month_sst.load().to_netcdf(f"OISST_25km_monthly_{startTime}-{endTime}.nc")
print('Making ice mask monthly..')
# making ice mask monthly
# ice data is missing for Dec 1987, Jan 1988, and Nov 2011
# These periods are handled near the end of the script
missing_data = ['1987-12-31','1988-01-31','2011-11-30']
# load ice data and fill missing data to zero
ice = ds2.ice.fillna(0)
# make ice binary
ice_binary = xarray.where(ice <= 0 ,0 ,1)
# make monthly ice mask
# create a new file
ndays_ice = 15
ice_mask = ice_binary.resample(time='1m').sum()
ice_mask = xarray.where(ice_mask > ndays_ice ,1 ,0)
# to be conservative, fill missing months with maximum ice extent from preceding and following months
for i in missing_data:
    idx = list(ice_mask.time.values).index(ice_mask.sel(time=i).time)
    ice_mask[idx] = ice_mask[idx-1:idx+1].max('time')
    
ice_mask.load().to_netcdf(f"oisst_25km_monthly_ice_mask_{startTime}-{endTime}.nc")
