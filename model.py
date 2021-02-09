import calendar
from itertools import cycle
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import time

from dataloader import DataLoader
from helpers import fill_series_gaps, radius_list
from helpers import regroup_dist_interval_buckets, get_quantile_dict
from settings import ACCOUNTS


### TODO: add lat-lim boundries to geo demand and assert if center is out of bounds

class Center:

    def __init__(self, center:tuple, df:pd.DataFrame, dict_dist:dict):
        self.center = center
        self.scope_df = df
        self.distributions = dict_dist
        self.day_of_week_distributions = {
            k: self.convolve_distributions(self.distributions[k]) for k in self.distributions.keys()
        }
        self.week_distribution = {
            'Week' : self.convolve_distributions(self.day_of_week_distributions)
        }

    def convolve_distributions(self, dist_dict:dict):
        for k,d in enumerate(dist_dict.values()):
            if k == 0:
                dist = d
            else:
                dist = np.convolve(dist, d)
        return dist

    def plot_weekday(self,weekday:int):
        quant_dict = get_quantile_dict(self.distributions[str(weekday)])
        quant_keys = list(quant_dict)
        # TODO: function that automatically provides a list of color paterns according to the lenght of the quant dict
        cycol1 = cycle(['lightcoral','gold','turquoise','lightgreen','lightgreen','turquoise','gold','lightcoral'])
        cycol2 = cycle(['lightcoral','gold','turquoise','lightgreen','turquoise','gold','lightcoral'])
        for n,k in enumerate(quant_keys):
            x = [i for i in range(len(quant_dict[k]))]
            if n == 0:
                c1 = next(cycol1)
                plt.scatter(x,quant_dict[k], color=c1, s=10, label=k)
            else:
                c1 = next(cycol1)
                c2 = next(cycol2)
                x = [i for i in range(len(quant_dict[k]))]
                plt.scatter(x,quant_dict[k], color=c1, s=10, label=k)
                plt.fill_between(x, quant_dict[quant_keys[n-1]], 
                                    quant_dict[quant_keys[n]], 
                                    color=c2, alpha=0.1)

        plt.legend(title='Quantiles', loc='best')
        plt.title(f'{list(calendar.day_name)[weekday]} Demand. {self.center}')
        plt.xlabel('Hour')
        plt.ylabel('Demand')
        plt.grid(axis='both',linestyle='-', linewidth=1, alpha=0.2)
        plt.show()

    def plot_distribution(self, weekday:int,hour:int, bins=20):
        if weekday and hour:
            D = self.distributions[str(weekday)][str(hour)]
            title = list(calendar.day_name)[weekday] + ' ' + str(hour) + 'h'
        elif weekday:
            D = self.day_of_week_distributions[str(weekday)]
            title = list(calendar.day_name)[weekday] 
        else:
            D = self.week_distribution['Week']
            title = 'Weekly'
        
        n_bins = int(np.floor(len(D)/bins))
        resize_dist = regroup_dist_interval_buckets(D,n_bins)
        resize_dist.plot(kind='bar', alpha=0.4)
        resize_dist.plot(linestyle='--',color='r', alpha=0.5)
        plt.xticks(rotation=45)
        plt.title(f'{title} Distribution. {self.center}')
        plt.xlabel('Demand')
        plt.ylabel('Prob')
        plt.show() 
        

class GeoModel:

    def __init__(self, df:pd.DataFrame, r:float, r_decay:float, alpha:float):
        self.df = df
        self.radius = r
        self.decay = r_decay
        self.r_lst = radius_list(self.radius, self.decay)
        self.alpha = alpha

### Define df influence area depending on center
    def filter_df(self, center:tuple, lon_col:str, lat_col:str,):
        fltr_df = self.df.copy()
        latitude = fltr_df.loc[:,lat_col]
        longitude = fltr_df.loc[:,lon_col]
        fltr_df.loc[:,'Distance'] = self.euclidian_distance(center, latitude, longitude)
        fltr_df = fltr_df[fltr_df.Distance <= max(self.r_lst)].reset_index(drop=True)
        return fltr_df

    def get_filter_df_attributes(self, df:pd.DataFrame):
        time_group = [df.Date.dt.dayofweek, df.Date.dt.hour]
        dist_group = [df.Date.dt.dayofweek, df.Date.dt.hour, df.Date]
        df.loc[:,'TimeW'] = self.time_weights(df, time_group)
        df.loc[:,'DistanceW'] = self.distance_weights(df, dist_group)
        df.loc[:,'Prob'] = df.DistanceW * df.TimeW
        return df

### Distance
    @staticmethod   
    def euclidian_distance(center:tuple, latitude:pd.Series, longitude:pd.Series):
        xi, yi = center
        return np.sqrt((longitude - xi)**2 + (latitude - yi)**2)

    @staticmethod
    def relative_distance(distance:pd.Series, radius_arr:list):
        """
        Given an array of radius, it classifies each point relative to it.
        Each points euclidean distance will be compared with the radius list and
        returned the index (relative distance) it falls in. 
        """
        return distance.apply(lambda x: 1 + np.searchsorted(radius_arr, x))

    @staticmethod
    def time_gap(dates:pd.Series, uom='weekly'):
        """
        Returns the relative time gap from the latest date. 
        The uom (unit of mesure) arguments defines the output units, by default weeks.
        If not specified, uom would be hourly
        """
        uom = (3600*24*7) if uom == 'weekly' else 3600 ## can be improved
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

    def time_weights(self,df:pd.DataFrame,grouping:list):
        """
        Grouping shpuld be: ['WeekDay','Hour'] 
        """
        df.loc[:,'TimeGap'] = self.time_gap(df.Date)
        group = df.groupby(grouping)
        return group['TimeGap'].transform(self.inverse_weight, self.alpha, inv_split='unique')
        
    def distance_weights(self,df:pd.DataFrame, grouping:list):
        """
        Grouping should be: ['Date'] (includes hour)
        Recommended alfa: 1.5-2
        """
        df.loc[:,'RelativeDistance'] = self.relative_distance(df['Distance'], self.r_lst)
        group = df.groupby(grouping)
        return group['RelativeDistance'].transform(self.inverse_weight, self.alpha)

### Calculate model
    def get_distribution(self, df:pd.DataFrame, weekday:int, hour:int):
        filter1 = (df.Date.dt.dayofweek == weekday)
        filter2 = (df.Date.dt.hour == hour)
        sub_df = df[filter1 & filter2]
        return fill_series_gaps(sub_df.groupby('Demand')['Prob'].sum())

    def model(self, center:tuple):
        scope_df = self.filter_df(center, lat_col='LatQ', lon_col='LonQ') 
        scope_df = self.get_filter_df_attributes(scope_df)
        distributions = {}
        for wkd in scope_df.Date.dt.dayofweek.sort_values().unique():
            for h in scope_df.Date.dt.hour.sort_values().unique():
                if str(wkd) in distributions.keys():
                    distributions[str(wkd)][str(h)] = self.get_distribution(scope_df, wkd, h)
                else:
                    distributions[str(wkd)] = {}
                    distributions[str(wkd)][str(h)] = self.get_distribution(scope_df, wkd, h)
                    
        return Center(center, scope_df, distributions)

if __name__ == '__main__':
    dl = DataLoader('uber')
    df = dl.read_all('clean',date_format='%Y-%m-%d %H:%M:%S')
    r = ACCOUNTS['uber']['radius']
    r_decay = ACCOUNTS['uber']['r_decay']
    alpha = ACCOUNTS['uber']['alpha']
    c1 = ACCOUNTS['uber']['center']
    print('* Data parsed')
    gm = GeoModel(df, r ,r_decay, alpha)
    p1 = gm.model(c1)