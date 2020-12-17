import pandas as pd
import numpy as np
import os
import glob

FOLDER_NAME = "20201216"
UTC_OFFSET = 2

def read_H97(H97_fname):
    hobo = pd.read_csv(H97_fname, skiprows=2, usecols=(1, 2, 3),
                       names=['Time', 'T', 'rh'],
                       parse_dates={'time': [0]},
                       date_parser=lambda x: 
                           pd.to_datetime(x).strftime('%m/%d/%y %H:%M:%S'),
                       index_col='time')
    hobo = hobo[np.isfinite(hobo["T"])]  # dumps rows with NaNs
    return hobo

def read_gps(fname):
    '''Creates timeseries dataframe from 'AntiMap Log' .csv file'''
    # converts filename to Timestamp
    start_time = pd.to_datetime(os.path.basename(fname)[:-4], 
                                format='%d%m%y_%H%M_%S')
    utc_time = start_time - pd.Timedelta(hours=UTC_OFFSET)
    gps = pd.read_csv(fname, names=['lat', 'lon', 'time'], usecols=[0, 1, 5],
                      index_col='time')
    
    log_time = pd.to_timedelta(gps.index, unit='ms')  # ms to timedelta
    gps.index = utc_time + log_time  # adds timedeltas to Timestamp//
    gps = gps.resample('1s').mean()
    gps = gps[~gps.index.duplicated(keep='first')]  # dumps duplicates
    return gps    



def read_all(folder):
    
    h97 = glob.glob(folder+'/*.csv')[0]
    hobo = read_H97(h97)
    #lapup = read_lapup('Meteo_1min_JUL2018_raw.zip')
    gpslist = glob.glob(folder+'/GPS/*.csv')
    gpslist.sort()
    gps_dflist = [read_gps(i) for i in gpslist]
    gps = pd.concat(gps_dflist, axis=0)
    gps = gps[~gps.index.duplicated(keep='first')]
    first = gps.iloc[0].name
    last = gps.iloc[-1].name
    dr = pd.date_range(first, last, freq='1s', name='Time')
    hobo = hobo.reindex(dr)
    gps = gps.reindex(dr)
    large_df = pd.concat([gps, hobo], axis=1)
    return large_df



# Sets QGIS project directory as working directory
# os.chdir(os.path.dirname(QgsProject.instance().fileName()))

dir_path = os.path.join(os.getcwd(), FOLDER_NAME)


large_df = read_all(dir_path)
large_df.to_csv(FOLDER_NAME+"_merged.csv")