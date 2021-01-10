from datetime import datetime
import os
import pandas as pd

from settings import DATA_DIR

class FileHandler:

    data_path = DATA_DIR

    def __init__(self, client):
        self.client = client
        self.client_path = self.get_client_dir()
        self.dirs_path = self.get_dirs_paths()
        
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
        dir_path = self.dirs_path[dir_name]
        return [(f, os.path.join(dir_path, f)) for f in os.listdir(dir_path) if not f.startswith('.')]

if __name__ == '__main__':
    fh = FileHandler('uber')