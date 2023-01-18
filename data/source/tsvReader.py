import pandas as pd
import json
import time

class TsvReader():
    def __init__(self):
        self.manual_data = {}
        self.auto_data = {}
        pass
    def load_data_csv(self,data_path):
        #read csv, save as dataframe
        data= pd.read_csv(data_path, sep='\t',header=1,names=['ppn','Signatur','Notizen', 'Auflagen'])
        for i in range(len(data)):
            dataframe = {
                "ppn":data['ppn'][i],
                'issue': data['Auflagen'][i],
                'notes': data['Notizen'][i],
                'signature': data['Signatur'][i]
            }
            if dataframe['notes'] != "NaN":
                self.manual_data[len(self.manual_data)+1] = dataframe
            else:
                self.auto_data[len(self.auto_data)+1] = dataframe
    
tsv= TsvReader()
tsv.load_data_csv('data/source/export.tsv')
              