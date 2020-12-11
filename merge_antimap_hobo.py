import pandas as pd
import numpy as np
import os

# Sets QGIS project directory as working directory
os.chdir(os.path.dirname(QgsProject.instance().fileName()))

FOLDER_NAME = "20190725"
HOBO_CSV = os.path.join(os.getcwd(), FOLDER_NAME, "H97_20190725.csv")
ANTIMAP_CSV = os.path.join(os.getcwd(), FOLDER_NAME, "250719_2242_45.csv")

# Reads hobo csv file
hobo = pd.read_csv(HOBO_CSV, skiprows=2, usecols=(1, 2, 3),
                   names=['Time', 'T', 'RH'],
                   parse_dates={'time': [0]},
                   date_parser=lambda x: pd.to_datetime(x).strftime('%m/%d/%y %H:%M:%S'),
                   index_col='time')
hobo = hobo[np.isfinite(hobo["T"])]  # dumps rows with NaNs
    
'''Creates timeseries dataframe from 'AntiMap Log' .csv file'''
# converts filename to Timestamp
start_time = pd.to_datetime(os.path.basename(ANTIMAP_CSV)[:-4], format='%d%m%y_%H%M_%S')
utc_time = start_time - pd.Timedelta(hours=3)
gps = pd.read_csv(ANTIMAP_CSV, names=['lat', 'lon', 'time'], usecols=[0, 1,5],
                  index_col='time')

log_time = pd.to_timedelta(gps.index, unit='ms')  # ms to timedelta
gps.index = utc_time + log_time  # adds timedeltas to Timestamp//
gps = gps.resample('1s').mean()
gps = gps[~gps.index.duplicated(keep='first')]  # dumps duplicates

first = gps.iloc[0].name
last = gps.iloc[-1].name
dr = pd.date_range(first, last, freq='1s', name='Time')

hobo = hobo.reindex(dr)
gps = gps.reindex(dr)

large_df = pd.concat([gps, hobo], axis=1)

large_df.to_csv(FOLDER_NAME+"_merged.csv")