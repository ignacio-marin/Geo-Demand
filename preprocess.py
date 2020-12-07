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
    filter_lat =  ((df.Lat > min_lat) & (df.Lat < max_lat))
    filter_lon =  ((df.Lon > min_lon) & (df.Lon < max_lon))
    filter_df = df[filter_lat & filter_lon]
    filter_df.reset_index(inplace=True)
    print(f'* Perimeter narrowed: Lat ({lat_lim}), Lon ({lon_lim})')
    return filter_df

def define_quadrant(dfm, step, lat_lim, lon_lim):
    """
    Divides the map in a grid of step x step quadrants size
    The quadrant representative coordinate will be the center of itself
    """
    df = dfm.copy()
    df.loc[:,'Q1'] = np.ceil(np.abs(df.loc[:,'Lat'] - lat_lim[0]) / step).astype(int)
    df.loc[:,'Q2'] = np.ceil(np.abs(df.loc[:,'Lon'] - lon_lim[0]) / step).astype(int)
    df.Q1.replace(0, 1, inplace=True) # when coordinate equal to lower boundry, Q == 0
    df.loc[:,'LatQ'] = lat_lim[0] + (df.loc[:, 'Q1'] - 0.5) * step
    df.Q2.replace(0, 1, inplace=True)
    df.loc[:,'LonQ'] = lon_lim[0] + (df.loc[:, 'Q2'] - 0.5) * step
    return df

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

def create_df_skeleton(min_date, max_date, lat_lim, lon_lim, step):
    lat_split = np.ceil((lat_lim[1] - lat_lim[0]) / step).astype(int) ## Needs function
    lon_split = np.ceil((lon_lim[1] - lon_lim[0]) / step).astype(int) ## repeated in definde quadrant
    date_df = create_date_spam_df(min_date, max_date)
    ext_1 = extend_df(date_df,group='Date',multiplier=lat_split)
    ext_1.rename(columns={'Cumsum':'Q1'}, inplace=True)
    ext_2 = extend_df(ext_1, group=['Date','Q1'],multiplier=lon_split)
    ext_2.rename(columns={'Cumsum':'Q2'}, inplace=True)
    ext_2.drop(columns='Gap', inplace=True)
    ext_2['LatQ'] = lat_lim[0] + (ext_2['Q1'] - 0.5) * step ## Needs function
    ext_2['LonQ'] = lon_lim[0] + (ext_2['Q2'] - 0.5) * step ## repeated in definde quadrant
    return ext_2

def fill_date_gaps(df, min_date, max_date, lat_lim, lon_lim, step):
    skeleton_df = create_df_skeleton(min_date, max_date, lat_lim, lon_lim, step)
    merged_df = pd.merge(left = skeleton_df,
                         right = df,
                         on = ['Date', 'Q1', 'Q2', 'LatQ', 'LonQ'],
                         how = 'left')
    merged_df.reset_index(inplace=True, drop=True)
    ## TODO: function this fillna
    merged_df['Demand'].fillna(0, inplace=True)
    ## TODO: 
    merged_df['LatQ'].fillna(df.LatQ.max(), inplace=True)
    merged_df['LonQ'].fillna(df.LonQ.max(), inplace=True)

    return merged_df

def fill_all_quadrants(df_list, gp_keys, min_date, max_date, lat_lim, lon_lim, step):
    """
    Given a pandas groupby object, it fullfills all the missing date/hours for each
    group and concatenates the final results
    """
    df_to_concat = [fill_date_gaps(df, min_date, max_date, lat_lim, lon_lim, step) for df in df_list] 
    new_df = pd.concat(df_to_concat)
    new_df.reset_index(inplace=True, drop=True)
    return new_df

if __name__ == '__main__':
    ### Parameters
    client = 'uber'
    params = ACCOUNTS[client]
    step, lat_lim, lon_lim = params['step'], params['lat_lim'], params['lon_lim']
    data_path = os.path.join(params['path'], 'raw')

    ## Parse
    df = parse_df(os.path.join(data_path, os.listdir(data_path)[1]))
    min_date = df.Date.min()
    max_date = df.Date.max()

    ### Define scope grid
    df = filter_df_perimeter(df, lat_lim, lon_lim)
    define_quadrant(df, step, lat_lim, lon_lim) 
    df = aggregate_by_quadrant(df)
    complete_df = fill_date_gaps(df, min_date, max_date, lat_lim, lon_lim, step)
