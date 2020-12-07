import numpy as np
import os
import pandas as pd

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




# TODO: define preprocessing script with all data manipulation. 
# Grid definition needs to be included, but distances will not...
# Add calculate_weights function based on the 2 distance ones



