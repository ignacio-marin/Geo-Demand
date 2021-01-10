import numpy as np
import os
import pandas as pd
import time

from dataloader import FileHandler
from tools import radius_list
from settings import ACCOUNTS


### Distance
def euclidian_distance(center:tuple):
    xi, yi = center
    return np.sqrt((df.loc[:,'LatQ'] - xi)**2 + (df.loc[:,'LonQ'] - yi)**2)

def relative_distance(radius_arr:list, d_column: str):
    """
    Given an array of radius, it classifies each point relative to it.
    Each points euclidean distance will be compared with the radius list and
    returned the index (relative distance) it falls in. 
    """
    return df.loc[:,d_column].apply(lambda x: 1 + np.searchsorted(radius_arr, x))

def time_gap(date_serie:pd.Series, agg='weekly'):
    """
    Returns the relative time gap from the latest date. The agg arguments defines
    the gap measure. By defaul, is per hour
    """
    uom = (3600*24*7) if agg == 'weekly' else 3600 ## can be improved
    max_Date = date_serie.max()
    time_delta = max_Date - date_serie
    return 1 + np.floor(time_delta.dt.total_seconds() / uom)

### Weights
def _inverse_weight(v_series:pd.Series, alfa:float, inv_split = ''):
    """
    Unique inv_split gives the same weight to each unique value. 
    By default, it divides the inverse value among all data points
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    | V | Inverse |        Unique     |     Sum (Default)  |
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    + 1 |    1    |  1/1.75   = 0.571 |   1/3.25   = 0.307 |
    + 1 |    1    |  1/1.75   = 0.571 |   1/3.25   = 0.307 |
    + 2 |   0.5   | 0.5/1.75  = 0.285 |  0.5/3.25  = 0.153 |
    + 2 |   0.5   | 0.5/1.75  = 0.285 |  0.5/3.25  = 0.153 |
    + 4 |   0.25  | 0.25/1.75 = 0.142 |  0.25/3.25 = 0.076 |
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    inv_distance = (1 / v_series ** alfa)
    if inv_split == 'unique':
        return inv_distance / inv_distance.unique().sum()
    else:
        return inv_distance / inv_distance.sum()

def time_weights(df:pd.DataFrame,d_column:str,grouping:list, alfa:float):
    """
    Grouping shpuld be: ['WeekDay','Hour'] 
    """
    df.loc[:,d_column] = time_gap(df.Date)
    group = df.groupby(grouping)
    return group[d_column].transformd(_inverse_weight, alfa, inv_split='unique')
    
def distance_weights(df:pd.DataFrame, d_column:str,grouping:list, alfa:float):
    """
    Grouping should be: ['Date'] (includes hour)
    Recommended alfa: 1.5-2
    """
    df.loc[:,d_column]  = relative_distance(r_lst, 'Distance')
    group = df.groupby(grouping)
    return group[d_column].transform(_inverse_weight, alfa)

if __name__ == '__main__':
    fh = FileHandler('uber')
    df_lst = [pd.read_csv(path[1]) for path in fh.get_dir_files('clean')]
    df = pd.concat(df_lst).reset_index(drop=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    r_lst = radius_list(0.004, 0.1)

    center = ACCOUNTS['uber']['center']
    df.loc[:,'Distance'] = euclidian_distance(center)
    df = df[df.Distance <= r_lst[-1]].reset_index(drop=True)
    # df.loc[:,'RelativeDistance']  = relative_distance(r_lst, 'Distance')
    df['TimeW'] = time_weights(df,'TimeW', [df.Date.dt.dayofweek, df.Date.dt.hour], 1.5)
    df['DistanceW'] = distance_weights(df,'RelativeDistance', [df.Date.dt.dayofweek, 
                                                               df.Date.dt.hour, df.Date], 1.5)

