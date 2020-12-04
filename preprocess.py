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

## TODO: instead of defining quadrant by nº of splits, consider giving the distance directly (step)
## wbhich should be much easier  ()
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
    gp = df.groupby(group_cols)
    return gp, gp.groups.keys()

def cumsum_by_group(df, group='Date',cumsum_col='Gap'):
    df['Cumsum'] = df.groupby(group)[cumsum_col].transform(pd.Series.cumsum) / df[cumsum_col]

def extend_df(df, group='Date', multiplier=50):
    """
    Given a Series containing int, the line extends the df it´sclea corresponding value.
    """
    df['Gap'] = multiplier
    df = pd.DataFrame(np.repeat(df.values,df['Gap'],axis=0), columns=df.columns)
    cumsum_by_group(df, group, 'Gap')
    return df

def create_date_spam_df(min_date, max_date):
    """
    Given 2 dates limits, the function returns as many lines as timedeltas between both values.
    Each line contains each date step
    """
    delta_h = int((max_date - min_date).total_seconds() / 3600)
    dates = [min_date + datetime.timedelta(hours=i) for i in range(int(delta_h))]
    return pd.DataFrame(dates, columns=['Date'])

def create_df_skeleton(min_date, max_date, split):
    date_df = create_date_spam_df(min_date, max_date)
    ext_1 = extend_df(date_df,group='Date',multiplier=split)
    ext_1.rename(columns={'Cumsum':'Q1'}, inplace=True)
    ext_2 = extend_df(ext_1, group=['Date','Q1'],multiplier=split)
    ext_2.rename(columns={'Cumsum':'Q2'}, inplace=True)
    ext_2.drop(columns='Gap', inplace=True)
    ## TODO: we need to create a back function that given coordinate boundries, and the split
    ## can associate the center coordinate lat and lon (inversa as define quadrant)
    ## TODO: alternatively, we can create the skeleton coordinates giving boundry limits
    return ext_2

def fill_date_gaps(df, min_date, max_date, split):
    skeleton_df = create_df_skeleton(min_date, max_date, split)
    merged_df = pd.merge(left = skeleton_df,
                         right = df,
                         on = ['Date', 'Q1', 'Q2'],
                         how = 'left')
    merged_df.reset_index(inplace=True, drop=True)
    ## TODO: function this fillna
    merged_df['Demand'].fillna(0, inplace=True)
    ## TODO: 
    merged_df['LatQ'].fillna(df.LatQ.max(), inplace=True)
    merged_df['LonQ'].fillna(df.LonQ.max(), inplace=True)

    return merged_df

def fill_all_quadrants(df_list, gp_keys, min_date, max_date, split):
    """
    Given a pandas groupby object, it fullfills all the missing date/hours for each
    group and concatenates the final results
    """
    df_to_concat = [fill_date_gaps(df, min_date, max_date, split) for df in df_list] 
    new_df = pd.concat(df_to_concat)
    new_df.reset_index(inplace=splitTrue, drop=True)
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
    complete_df = fill_date_gaps(df, min_date, max_date, params['split'])
