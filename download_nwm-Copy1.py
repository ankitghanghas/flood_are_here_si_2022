import urllib.request
import os
import time
import pandas as pd


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

## change_this

def main():
    os.chdir('/home/jovyan/data/aghanghas/inundation_map/nwm-v2-1')

    start_time=time.time()
    start_date='2018-09-18'
    end_date='2018-09-26'

    time_list=pd.date_range(start=start_date,end=end_date,freq='H')     #makes a time list with one hour frequency between start and end date.


    bucket_name="https://noaa-nwm-retrospective-2-1-pds.s3.amazonaws.com/model_output/"

    for idx, t in enumerate(time_list):
        time1=t.strftime('%Y%m%d%H')
        f_name=time1+"00.CHRTOUT_DOMAIN1.comp"
        key_name=str(t.year)+"/" + f_name
        url_path=bucket_name+key_name
        
        #coudn't just read file directly into python so i am just downloading it, will remove at the end
        try: 
            urllib.request.urlretrieve(url_path,f_name)
        except urllib.request.HTTPError:  
            continue

if __name__ == '__main__':
    main()

