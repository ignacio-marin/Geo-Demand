import os
import pandas as pd

def get_files_path(path):
    """
    Returns a list of tuples containing the file name and the file path
    """
    path_tuple_list = [(f, os.path.join(path, f)) for f in os.listdir(path) if not f.startswith('.')]
    return path_tuple_list

def _format_df_date(df):
    df.rename(columns={'Date/Time':'Date'}, inplace = True)
    df = df.assign(Date=df.Date.dt.round('H'))
    
    return df

def parse_df(file_path, date_cols=['Date/Time'],headers=['Date/Time', 'Lat', 'Lon']):
    df = pd.read_csv(file_path, parse_dates=date_cols, usecols=headers)
    df['Demand'] = 1
    df = _format_df_date(df)
    print(f'* Data parsed: {file_path}')
    return df