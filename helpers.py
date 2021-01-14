import numpy as np
import pandas as pd

### Equal area rings approach
def ring_equal_area_radius(r, area):
    external_radio = np.sqrt((area + np.pi*r**2)/np.pi)
    return external_radio

def equal_area_rings_radius(r, n_rings):
    rr = [r]
    area = np.pi*r**2
    for i in range(n_rings-1):
        r = ring_equal_area_radius(r, area)
        rr.append(r)
    return np.array(rr)

### This is the one
def radius_list(r0:float, decay_ratio: float):
    """
    Returns an array of n_rings radius. Each new radius is the sum of the previous
    one plus the original radius (r0) decreasing size n times decay. The idea is that
    the further we go, the smaller the next radius gets
    eg: r0 = 4 decay_ratio = 0   n_rings = 3 -> [4,8,12]
        r0 = 2 decay_ratio = 0.1 n_rings = 3 -> [2, 3.8, 5.4]
    """
    l = [r0]
    n_rings = int(1/decay_ratio)
    for i in range(n_rings - 1):
        l.append(l[i] + r0 * (1 - (i+1)*decay_ratio))
    return np.array(l)

### Variance functions
def calc_relative_variance(df, group_cols, qty_col):
    """
    group_cols: [df.Date.dt.dayofweek, df.Date.dt.hour, df.RelativeDistance]
    f: np.var, semivariance
    """
    df['RelativeVar'] = df.groupby(group_cols)[qty_col].transform(np.var)

def semivariance(x):
    if len(x):
        return 0
    else:
        z = np.reshape(x, (len(x), 1))
        v = 0.5 * (z - z.transpose()) ** 2
        return sum(np.concatenate(v)) / len(x)

### Normalize array and fill the gaps

def fill_series_gaps(x:pd.Series):
    """
    Gets a pandas Series with missing indexes, fills the spaces
    and interpolates the values between them.
    Because the values are probabilities, it recalculates the final
    value over the total
    +++++++++++++++++++++
    | Index |    Value  |    fill+interpolation: 
    +++++++++++++++++++++               [0.4, 0.4, 0.3, 0.2]
    +   0   |     0.4   |    final:
    +   1   |     0.4   |             [0.307, 0.307, 0.23, 0.153]
    +   4   |     0.2   |
    """
    n = x.index.max()
    y = pd.Series(index=np.arange(x.index.max()+1),dtype=np.float64)
    fill = x.combine(y, min).interpolate()
    return fill / fill.sum()

def regroup_dist_buckets(x:pd.Series, n):
    """
    n: bucket size
    """
    m = np.floor(len(x)/n)
    index = pd.interval_range(start=0, periods=m+1, freq=n, closed='left')
    z = pd.Series(index=pd.RangeIndex(0,m * n, n),dtype=np.float64)

    for k,i in enumerate(z.index):
        z[i] = x[k*n:k*n+n].sum()
    return z

def regroup_dist_interval_buckets(x:pd.Series, n):
    """
    n: bucket size
    """
    m = np.floor(len(x)/n)
    index = pd.interval_range(start=0, periods=m+1, freq=n, closed='left')
    z = pd.Series(index=index,dtype=np.float64)
    for k, idx_tup in enumerate(z.index.to_tuples()):
        low, high = idx_tup
        z.loc[low] = x[low:high].sum()
    return z

