import json
import re


class Preprocess():
    """
    Take the raw data from the file and split it into two json files.
    
    
    
    """
    def __init__(self, file, output_file, file_encoding="utf-8"):
        self.file = file
        self.output_file = output_file
        self.file_encoding = file_encoding
        self.autono=1
        self.manualno=1
        self.autojson={}
        self.manualjson={}
        
    def read_file(self):
        #open json file
        file=open(self.file,"r",encoding=self.file_encoding)
        data = json.load(file)
        file.close()
        return data

    def create_json_files(self):
        data=self.read_file()
        for i in data:
            if data[i]["NOT"] != "":
                try:
                    data[i]['NOT']=data[i]["NOT"].replace("<<mybrNEWLINE>>"," ")
                except AttributeError:
                    pass
                self.manualjson[self.manualno]=data[i]
                self.manualno+=1
            else:
                self.autojson[self.autono]=data[i]
                self.autono+=1
    def main(self)->tuple:
        """
        Splits the data into two json files.
        
        Returns the names of the two files.
        
        """
        self.create_json_files()
        with open(self.output_file,"w",encoding=self.file_encoding) as f:
            json.dump(self.autojson,f,indent=4)
        with open(self.output_file.replace(".json","_manual.json"),"w",encoding=self.file_encoding) as f:
            json.dump(self.manualjson,f,indent=4)  
        
        return self.output_file, self.output_file.replace(".json","_manual.json")            
if __name__ == "__main__":
    preprocess = Preprocess(file="C:/Users/aky547/Desktop/Oberfell_to_tsv/output_files/chemie_out.json", output_file="data/source/chemie_merged.json", file_encoding="utf-8").main()