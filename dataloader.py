from datetime import datetime
import os
import pandas as pd

def get_files_path(path):
    """
    Returns a list of tuples containing the file name and the file path
    """
    path_tuple_list = [(f, os.path.join(path, f)) for f in os.listdir(path) if not f.startswith('.')]
    return path_tuple_list

def _format_date(df):
    df = df.rename(columns={'Date/Time':'Date'})
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %H:%M:%S')
    df = df.assign(Date=df.Date.dt.round('H'))
    return df

def parse_df(file_path,headers=['Date/Time', 'Lat', 'Lon']):
    then = datetime.now()
    print('* Start parse df')
    df = pd.read_csv(file_path, usecols=headers)
    print(f' - File read ({datetime.now() - then})')
    df['Demand'] = 1
    print(f' - Demand = 1 added ({datetime.now() - then})')
    df = _format_date(df)
    print(f' - Dates reformated ({datetime.now() - then})')
    print(f' - Data parsed: {file_path}')
    return df