import pandas as pd


def _format_df_date(df):
    df.rename(columns={'Date/Time':'Date'}, inplace = True)
    df = df.assign(Date=df.Date.dt.round('H'))
    return df

def parse_df(file_path, date_cols=['Date/Time'],headers=['Date/Time', 'Lat', 'Lon']):
    df = pd.read_csv(file_path, parse_dates=date_cols, usecols=headers)
    df['Demand'] = 1
    df = _format_df_date(df)
    return df