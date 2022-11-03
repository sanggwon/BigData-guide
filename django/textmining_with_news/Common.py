import pandas as pd
import json
import os

class Common:
    def stopwords():
        currentpath = os.getcwd()
        with open(currentpath + '\\stopwords.txt', 'rt', encoding='UTF8') as f:
            stopwords = f.read().splitlines()
        return stopwords