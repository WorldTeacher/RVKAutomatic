import json
import re,os
import subprocess
import chardet

class Create_Json():
    def __init__(self,txt_folder) -> None:
        path=txt_folder.replace("/","\\")
        textfiles = os.listdir(txt_folder)
        self.txtfile=f'{path}\{textfiles[0]}'
        print(self.txtfile)
        self.json_file=self.txtfile.replace(".txt",".json")
        self.encoding = chardet.detect(open(self.txtfile, 'rb').read())['encoding']
        if not self.txtfile.endswith(".txt"):
            print("Invalid file, must be .txt, exiting")
            exit()
        if not self.txt_control():
            print("Invalid file")
            exit()
        
        if self.encoding != "utf-8":
            self.convert_to_utf8()
    
    
    def txt_control(self):
        print(self.encoding)
        with open(self.txtfile,"r",encoding=self.encoding) as f:
            data=f.read()
        #check if SET: Pica2rvk-Export is in the file, as this should be unique to these files
        if not "SET: Pica2rvk-Export" in data:
            return False
        else:
            return True        

    def convert_to_utf8(self):
        with open(self.txtfile,"r",encoding=self.encoding) as f:
            data=f.read()
        with open(self.txtfile,"w",encoding="utf-8") as f:
            f.write(data)

    def create_json(self):
        cmd_pt1=r'processing\jdk17.0.3_6\bin\java.exe -jar processing\OberfellExport2Json.jar'
        cmd=f'{cmd_pt1} "{self.txtfile}" "{self.json_file}"'
        with open("converter.bat","w") as f:
            f.write(cmd)
        subprocess.run("converter.bat",shell=True)
        return self 
    def delete_txt_file(self):
        os.remove(self.txtfile)
        return self       
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


def remove_duplicates(file):
    with open(file, 'r') as f:
        data = json.load(f)

    cleaned_data = {}
    ppn_set = set()

    for key, value in data.items():
        ppn = value['PPN']
        if ppn not in ppn_set:
            cleaned_data[key] = value
            ppn_set.add(ppn)

    with open(f'{file}', 'w') as f:
        json.dump(cleaned_data, f, indent=4)

    
class PDF_Create:
    def __init__(self) -> None:
        self.path=r"C:\rvkoutput"
        if not os.path.exists(f'{self.path}/backup'):
            os.mkdir(f'{self.path}/backup')
    
        pass
    
    def create_pdf(self,remove_dupes=False):
        if remove_dupes==True:
            json_files=os.listdir(self.path)
            for file in json_files:
                if file.endswith(".json"):
                    remove_duplicates(f'{self.path}/{file}')
        cmd=r'processing\jdk17.0.3_6\bin\java.exe --module-path "processing/javafx-sdk-18.0.1/lib" --add-modules javafx.controls,javafx.fxml -jar processing/rvkJsonToPdf.jar'
        cmd_pt2=f'{self.path}'
        cmd=f'{cmd} {cmd_pt2}'
        with open("barcode.bat","w") as f:
            f.write(cmd)	
        subprocess.run("barcode.bat",shell=True)
        return self
    
    def move_json_file(self):
        files=os.listdir(self.path)
        for file in files:
            if file.endswith(".json"):
                os.rename(f'{self.path}/{file}',f'{self.path}/backup/{file}')	
    
    
if __name__ == "__main__":
    #preprocess = Preprocess(file="", output_file="data/source/chemie_merged.json", file_encoding="utf-8").main()
    
    # create=Create_Json(r"C:\rvkinput").create_json().delete_txt_file()
    pdf=PDF_Create().create_pdf(remove_dupes=True).move_json_file()