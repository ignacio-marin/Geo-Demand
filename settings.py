from os.path import abspath, dirname, join

ROOT_DIR = dirname(abspath(__file__))
DATA_DIR = join(ROOT_DIR,'data')

ACCOUNTS = {
    'uber': {
        'path': join(DATA_DIR, 'uber'),
        'lat_lim': (40.5,40.9), 
        'lon_lim': (-74.3,-73.6),
        'split': 50,
        'center': (40.75, -74),
        'radius': 0.04
    },
}
