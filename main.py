import numpy as np
import os
import pandas as pd

from plot_func import plot_scatter_coordinates
from settings import ACCOUNTS

def format_df_date(df):
    df.rename(columns={'Date/Time':'Date'}, inplace = True)
    df = df.assign(Date=df.Date.dt.round('H'))
    return df

def parse_df(file_path, date_cols=['Date/Time'],headers=['Date/Time', 'Lat', 'Lon']):
    df = pd.read_csv(file_path, parse_dates=date_cols, usecols=headers)
    df['Demand'] = 1
    df = format_df_date(df)
    return df

def filter_df_perimeter(df, lat_lim, lon_lim):
    """
    Narrows the map scope to the study area
    """
    min_lat, max_lat = lat_lim
    min_lon, max_lon = lon_lim
    filter_df = df[(df.Lat.between(min_lat,max_lat)) & (df.Lon.between(min_lon,max_lon))]
    filter_df.reset_index(inplace=True)
    return filter_df

def define_quadrant(df, split, lat_lim, lon_lim):
    """
    Divides the map in split x split grid. The quadrant coordinate will be the center of it
    """
    lat_lim = (df.Lat.min(), df.Lat.max())
    lon_lim = (df.Lon.min(), df.Lon.max())
    step_lat = (lat_lim[1] - lat_lim[0]) / split
    step_lon = (lon_lim[1] - lon_lim[0]) / split

    df['Q1'] = np.ceil((df.Lat - lat_lim[0]) / step_lat)
    df['Q2'] = np.ceil((df.Lon - lon_lim[0]) / step_lon)
     # when equal to lower boundry, Q == 0
    df.Q1.replace(0, 1, inplace=True)
    df['LatQ'] = lat_lim[0] + df.Q1 * step_lat - step_lat/2
    df.Q2.replace(0, 1, inplace=True)
    df['LonQ'] = lon_lim[0] + df.Q2 * step_lon - step_lon/2

def calculate_relative_distance(df, center, radius):
    """
    Returns the real distance of all points to the center, and classifies 
    according to it the influence area group it falls in (relative distance).
    eg: if a point has a distance to the center equal to 2.4, and the radious
    is equal to 1, the relative distance will be be 3 (between 2-3 times r)
    """
    xi, yi = center
    df['Distance'] = np.sqrt((df['LatQ'] - xi)**2 + (df['LonQ'] - yi)**2)
    df['RelativeDistance'] = np.floor(df['Distance'] / radius) + 1

def extend_df(df, col_multiply='Gap')
    df = pd.DataFrame(np.repeat(sdf.values,df['Gap'],axis=0), cols=sort_q.columns)

def fill_date_gaps(df):
    max_date = df.Date.max()
    sort_df = df.sort_values('Date')
    sort_df.reset_index(inplace=True)

    sort_df['ShiftDate'] = sort_q.Date.shift(-1)
    sort_df['ShiftDate'].fillna(max_date, inplace=True,drop=True)
    sort_df['Gap'] = (sort_df.ShiftDate - sort_df.Date).dt.total_seconds() / 3600
    extend_df = extend_df(sort_df,'Gap')

if __name__ == '__main__':
    ## Parse data
    client = 'uber'
    params = ACCOUNTS[client]
    data_path = os.path.join(params['path'], 'raw')
    df = parse_df(os.path.join(data_path, os.listdir(data_path)[1]))

    ### Parameters
    df = filter_df_perimeter(df, params['lat_lim'], params['lon_lim'])
    define_quadrant(df, params['split'], params['lat_lim'], params['lon_lim']) 

    aggregate = {'Demand' : sum, 'LatQ':min, 'LonQ':min, 'Date':min,'Q1':min,'Q2':min}
    group_cols = [df.Date.dt.day, df.Date.dt.hour,df.LatQ, df.LonQ]
    agg_df = df.groupby(group_cols).agg(aggregate) 
    agg_df.reset_index(drop=True, inplace=True)

    calculate_relative_distance(agg_df, params['center'], params['radius'])
    plot_scatter_coordinates(
                        agg_df,
                        'LatQ', 
                        'LonQ', 
                        'RelativeDistance',
                         center=params['center'], 
                         radius=params['radius'])
    # plot_scatter_coordinates(
    #                     agg_df,
    #                     'Q1', 
    #                     'Q2', 
    #                     'RelativeDistance') 


