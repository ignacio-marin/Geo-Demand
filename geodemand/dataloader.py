from datetime import datetime
import os
import pandas as pd

from geodemand.settings import DATA_DIR

class FileHandler:

    data_path = DATA_DIR

    def __init__(self, client):
        self.client = client
        self.client_path = self.get_client_dir()
        self.directories = self.get_dirs_paths()
        
    def get_client_dir(self):
        return os.path.join(self.data_path, self.client)

    def get_dirs_paths(self):
        dirs = os.listdir(self.client_path)
        dirs_dict = {}
        for f in dirs:
            if not f.startswith('.'):
                dirs_dict[f] = os.path.join(self.client_path, f)

        return dirs_dict

    def get_dir_files(self, dir_name):
        dir_path = self.directories[dir_name]
        return [(f, os.path.join(dir_path, f)) for f in os.listdir(dir_path) if not f.startswith('.')]

class DataLoader:

    def __init__(self, client):
        self.client = client
        self.file_handler = FileHandler(self.client)

    def read_all(self,folder_name, date_format='%Y-%m-%d %H:%M:%S', date_col='Date'):
        df_list = [pd.read_csv(path) for _, path in self.file_handler.get_dir_files(folder_name)]
        df = pd.concat(df_list).reset_index(drop=True)
        if date_format:
            df['Date'] = pd.to_datetime(df[date_col], format=date_format)
            return df
        else:
            return df
