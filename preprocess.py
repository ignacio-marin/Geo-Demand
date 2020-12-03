import datetime
import numpy as np
import os
import pandas as pd

from plot_func import plot_scatter_coordinates
from dataloader import parse_df

from settings import ACCOUNTS

def filter_df_perimeter(df, lat_lim, lon_lim):
    """
    Narrows the map scope to the study area given the boundries
    """
    min_lat, max_lat = lat_lim
    min_lon, max_lon = lon_lim
    filter_df = df[(df.Lat.between(min_lat,max_lat)) & (df.Lon.between(min_lon,max_lon))]
    filter_df.reset_index(inplace=True)
    return filter_df

def define_quadrant(df, split, lat_lim, lon_lim):
    """
    Divides the map in a split by split grid. 
    The quadrant representative coordinate will be the center of it
    """
    lat_lim = (df.Lat.min(), df.Lat.max())
    lon_lim = (df.Lon.min(), df.Lon.max())
    step_lat = (lat_lim[1] - lat_lim[0]) / split
    step_lon = (lon_lim[1] - lon_lim[0]) / split

    df['Q1'] = np.ceil((df.Lat - lat_lim[0]) / step_lat).astype(int)
    df['Q2'] = np.ceil((df.Lon - lon_lim[0]) / step_lon).astype(int)
    df.Q1.replace(0, 1, inplace=True) # when equal to lower boundry, Q == 0
    df['LatQ'] = lat_lim[0] + df.Q1 * step_lat - step_lat/2
    df.Q2.replace(0, 1, inplace=True)
    df['LonQ'] = lon_lim[0] + df.Q2 * step_lon - step_lon/2

def aggregate_by_quadrant(df):
    aggregate = {'Demand' : sum, 'LatQ':min, 'LonQ':min, 'Date':min,'Q1':min,'Q2':min}
    group_cols = [df.Date.dt.day, df.Date.dt.hour,df.LatQ, df.LonQ]
    agg_df = df.groupby(group_cols).agg(aggregate) 
    agg_df.reset_index(drop=True, inplace=True)
    return agg_df

def groupby_quadrant(df):
    group_cols = [df.Q1, df.Q2]
    return df.groupby(group_cols)

def _fake_date_df(min_date, max_date):
    delta_h = int((max_date - min_date).total_seconds() / 3600)
    dates = [min_date + datetime.timedelta(hours=i) for i in range(int(delta_h))]
    return pd.DataFrame(dates, columns=['Date'])

def fill_date_gaps(df, min_date, max_date):
    date_df = _fake_date_df(min_date, max_date)
    merged_df = pd.merge(left = date_df,
                        right = df,
                        on = 'Date',
                        how = 'left')
    merged_df.reset_index(inplace=True, drop=True)
    ## TODO: function this fillna
    merged_df['Demand'].fillna(0, inplace=True)
    merged_df['LatQ'].fillna(df.LatQ.max(), inplace=True)
    merged_df['LonQ'].fillna(df.LonQ.max(), inplace=True)
    merged_df['Q1'].fillna(df.Q1.max(), inplace=True)
    merged_df['Q2'].fillna(df.Q2.max(), inplace=True)

    return merged_df

## TODO: fill quadrant gaps

def fill_all_quadrants(gp, min_date, max_date):
    """
    Given a pandas df groupby object, it fullfills all the missing date/hours for each
    group and concatenates the final results
    """
    df_list = [fill_date_gaps(df, min_date, max_date) for _, df in gp]  
    new_df = pd.concat(df_list)
    new_df.reset_index(inplace=True, drop=True)
    return new_df

if __name__ == '__main__':
    ### Parse
    client = 'uber'
    params = ACCOUNTS[client]
    data_path = os.path.join(params['path'], 'raw')
    df = parse_df(os.path.join(data_path, os.listdir(data_path)[1]))
    min_date = df.Date.min()
    max_date = df.Date.max()

    ### Define scope grid
    df = filter_df_perimeter(df, params['lat_lim'], params['lon_lim'])
    define_quadrant(df, params['split'], params['lat_lim'], params['lon_lim']) 
    df = aggregate_by_quadrant(df)

    ### Add missing lines
    gp = groupby_quadrant(df)
    test_gp = gp.get_group((17,40))
    clean_df = fill_all_quadrants(gp, min_date, max_date)


    