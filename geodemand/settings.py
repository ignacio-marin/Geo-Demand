import os


if os.name == 'posix':
    ROOT_DIR = DATA_DIR = '/mnt'
else:

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(ROOT_DIR,'data')

ACCOUNTS = {
    'uber': {
        'path': os.path.join(DATA_DIR, 'uber'),
        'lon_lim': (-74.1,-73.9),
        'lat_lim': (40.65,40.85), 
        'step': 0.005,
        'center': (-73.99, 40.75),
        'radius': 0.004,
        'r_decay':0.1,
        'alpha':1.5
    },
}
