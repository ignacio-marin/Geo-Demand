from geodemand.dataloader import DataLoader
from geodemand.settings import ACCOUNTS
from geodemand.model import GeoModel


if __name__ == '__main__':
    dl = DataLoader('uber')
    df = dl.read_all('clean',date_format='%Y-%m-%d %H:%M:%S')
    r = ACCOUNTS['uber']['radius']
    r_decay = ACCOUNTS['uber']['r_decay']
    alpha = ACCOUNTS['uber']['alpha']
    c1 = ACCOUNTS['uber']['center']
    print('* Data parsed')
    gm = GeoModel(df, r ,r_decay, alpha)
    p1 = gm.model((-73.99, 40.75))