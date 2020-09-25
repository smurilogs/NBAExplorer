            
from abc import ABC, abstractmethod
import json
import os

class FileHandler(ABC):

    # load a .json file and turn it into object
    @staticmethod
    def load_json_file(aPath):
        with open(os.path.join(aPath), 'r') as file:
            obj = json.load(file)
        return obj

    # save an object to a .json file
    @staticmethod
    def save_json_file(aObj, aPath):
        with open(os.path.join(aPath), 'w') as file:
            json.dump(aObj, file, indent = 4)

    # create an empty directory
    @staticmethod
    def create_directory(aPath):
        try:
            if not os.path.exists(os.path.join(aPath)):
                os.makedirs(os.path.join(aPath))
        except OSError:
            print ('Error: Creating directory. ' +  aPath)
