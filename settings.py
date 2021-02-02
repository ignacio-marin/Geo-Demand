import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR,'data')

ACCOUNTS = {
    'uber': {
        'path': os.path.join(DATA_DIR, 'uber'),
        'lat_lim': (40.65,40.85), 
        'lon_lim': (-74.1,-73.9),
        'step': 0.005,
        'center': (40.75, -73.9975),
        'radius': 0.004,
        'r_decay':0.1,
        'alpha':1.5
    },
}
