import numpy as np
import os
import pandas as pd
import time

from dataloader import FileHandler
from helpers import radius_list
from settings import ACCOUNTS


### TODO: self.filter/transformed dataframe

class Point:
    
    def __init__(self,center):
        self.center =  center
        self.predictions = {}
        

class GeoModel:

    def __init__(self, df:pd.DataFrame, center:tuple, r:float, r_decay:float, alpha:float):
        self.center = center
        self.df = df
        self.decay = r_decay
        self.radius = r
        self.r_lst = radius_list(self.radius, self.decay)
        self.alpha = alpha
        self.fltr_df = self.__transform_df(self.df, 'LatQ', 'LonQ') 
        self.__get_fltr_df_attributes()
        ## Column names should be defined in the client settings (also used in preprocess)

    def __transform_df(self, df, lat_col:str, lon_col:str):
        fltr_df = self.df.copy()
        latitude = fltr_df.loc[:,lat_col]
        longitude = fltr_df.loc[:,lon_col]
        fltr_df.loc[:,'Distance'] = self.euclidian_distance(self.center, latitude, longitude)
        fltr_df = fltr_df[fltr_df.Distance <= max(self.r_lst)].reset_index(drop=True)
        return fltr_df

    def __get_fltr_df_attributes(self):
        time_group = [self.fltr_df.Date.dt.dayofweek, self.fltr_df.Date.dt.hour]
        dist_group = [self.fltr_df.Date.dt.dayofweek, self.fltr_df.Date.dt.hour, self.fltr_df.Date]
        self.fltr_df.loc[:,'TimeW'] = self.time_weights(time_group)
        self.fltr_df.loc[:,'DistanceW'] = self.distance_weights(dist_group)
        self.fltr_df.loc[:,'Prob'] = self.fltr_df.DistanceW * self.fltr_df.TimeW

### Distance
    @staticmethod   
    def euclidian_distance(center:tuple, latitude:pd.Series, longitude:pd.Series):
        xi, yi = center
        return np.sqrt((latitude - xi)**2 + (longitude - yi)**2)

    @staticmethod
    def relative_distance(distance:pd.Series, radius_arr:list):
        """
        Given an array of radius, it classifies each point relative to it.
        Each points euclidean distance will be compared with the radius list and
        returned the index (relative distance) it falls in. 
        """
        return distance.apply(lambda x: 1 + np.searchsorted(radius_arr, x))

    @staticmethod
    def time_gap(dates:pd.Series, agg='weekly'):
        """
        Returns the relative time gap from the latest date. The agg arguments defines
        the gap measure. By defaul, is per hour
        """
        uom = (3600*24*7) if agg == 'weekly' else 3600 ## can be improved
        max_Date = dates.max()
        time_delta = max_Date - dates
        return 1 + np.floor(time_delta.dt.total_seconds() / uom)

### Weights
    @staticmethod
    def inverse_weight(values:pd.Series, alfa:float, inv_split = ''):
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
        inv_distance = (1 / values ** alfa)
        if inv_split == 'unique':
            return inv_distance / inv_distance.unique().sum()
        else:
            return inv_distance / inv_distance.sum()

    def time_weights(self,grouping:list):
        """
        Grouping shpuld be: ['WeekDay','Hour'] 
        """
        self.fltr_df.loc[:,'TimeGap'] = self.time_gap(self.fltr_df.Date)
        group = self.fltr_df.groupby(grouping)
        return group['TimeGap'].transform(self.inverse_weight, self.alpha, inv_split='unique')
        
    def distance_weights(self,grouping:list):
        """
        Grouping should be: ['Date'] (includes hour)
        Recommended alfa: 1.5-2
        """
        self.fltr_df.loc[:,'RelativeDistance'] = self.relative_distance(self.fltr_df['Distance'], self.r_lst)
        group = self.fltr_df.groupby(grouping)
        return group['RelativeDistance'].transform(self.inverse_weight, self.alpha)

### Calculate model
    def get_distribution(self, weekday:int, hour:int):
        filter1 = (self.fltr_df.Date.dt.dayofweek == weekday)
        filter2 = (self.fltr_df.Date.dt.hour == hour)
        sub_df = self.fltr_df[filter1 & filter2]
        return sub_df.groupby('Demand')['Prob'].sum()

if __name__ == '__main__':
    fh = FileHandler('uber')
    df_lst = [pd.read_csv(path[1]) for path in fh.get_dir_files('clean')]
    df = pd.concat(df_lst).reset_index(drop=True)
    ### Date format should be hanldled in the DataLoader class TODO
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    r = 0.004
    r_decay = 0.1
    alpha = 1.5
    center = ACCOUNTS['uber']['center']
    print('* Data parsed')
    gm = GeoModel(df, center,r ,r_decay, alpha)

