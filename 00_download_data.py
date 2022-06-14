import requests
import wget
import re,os

# Daily data from NOAA
url ='https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/'

# Set this to the directory with the codes
workingDir = os.getcwd()

# Set this to directory where .nc file will save
OISST_Dir = os.path.join(workingDir, 'OISST\\')

# Checking if the directory exist or not
# If it is non-existent then create one
if os.path.exists(OISST_Dir):
    pass
    print('資料夾存在')
else:
    os.makedirs(OISST_Dir, exist_ok=True)

# Check if url link is a file
# isFile function
def isFile(url):
    if url.endswith('/'):
        return False
    else:
        return True
    
# get_url function
def get_url(base_url):
    text = ''
    try:
        # html into text
        text=requests.get(base_url).text 
    except Exception as e:
        print("error - > ",base_url,e)
        pass
    reg = '<a href="(.*?)">.*</a>'
    urls = [base_url + url for url in re.findall(reg, text) if url != '../']
    return urls

# Download file function
# First check if the input url is a file (without ending with '/')
# If it is a file
# extract the file name from url
# check if the file exit is your folder
# if no
# use wget package for downloading
def get_file(url):
    if isFile(url):
        try:
            full_name = url.split('//')[-1]
            filename = full_name.split('/')[-1]
            path_filename = OISST_Dir  + filename
            if os.path.isfile(path_filename):
                print(f'{filename} 存在')
                pass
            else:
                wget.download(url,OISST_Dir)
        except:
            pass
    else:
        urls = get_url(url)
        for u in urls:
            get_file(u)
            
get_file(url)