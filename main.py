from bot import Bot, ControlBot#,TestBot
import json
import time
from discord_notification import *
from preprocess import Preprocess
import os,sys
from datetime import date



class Main:
    def __init__(self, debug:bool=False) -> None:
        if not debug:
            self.testbot = Bot()
        self.manualdata={}
        self.donedata={}
        pass
    
    
    def main_startup(self):
        input_folder = "C:/rvkinput"
        output_folder = "C:/rvkoutput"
        files_in_input = os.listdir(input_folder)
        try:
            today_runs = len(os.listdir(f'{output_folder}/{date.today()}'))
        except FileNotFoundError:
            os.makedirs(f'{output_folder}/{date.today()}',exist_ok=False)
            today_runs = len(os.listdir(f'{output_folder}/{date.today()}'))
            
        print(files_in_input)
        if len(files_in_input)>1:
            print("Only one file, sorry")
            exit()
        print(f"starting work on {files_in_input[0]}")
        curr_date=date.today()
        print(curr_date)
        if not os.path.exists(f'{output_folder}/{curr_date}/run_{today_runs+1}'):
            os.makedirs(f'{output_folder}/{curr_date}/run_{today_runs+1}',exist_ok=False)
        output_folder=f'{output_folder}/{curr_date}/run_{today_runs+1}'
        return input_folder, output_folder, files_in_input[0]   
    
    def read_write_json(self, folder, input_file, payload:dict):
        with open(f'{folder}/{input_file}',"r",encoding="utf-8") as f:
            file_data=json.load(f)
        curr_entry=len(file_data)+1
        file_data[curr_entry]=payload
        with open(f'{folder}/{input_file}',"w",encoding="utf-8") as f:
            json.dump(file_data,f,indent=4)
    
    def testrun(self, resume:bool=False):
        input_folder, output_folder, file = self.main_startup()
        error_file = file.replace(".json","_error.json")
        done_file = file.replace(".json","_done.json")
        if not os.path.exists(f'{output_folder}/{error_file}'):
            with open(f'{output_folder}/{error_file}',"w",encoding="utf-8") as f:
                json.dump({},f,indent=4)
        if not os.path.exists(f'{output_folder}/{done_file}'):
            with open(f'{output_folder}/{done_file}',"w",encoding="utf-8") as f:
                json.dump({},f,indent=4)
        
        
        i=1
        with open(f'{input_folder}/{file}',"r",encoding="utf-8") as f:
            data=json.load(f)
        if resume==True:
            data=self.resume_run(data, output_folder)
        for entry in data:
            ppn=data[entry]["PPN"]
            sig=data[entry]["SIG"]
            notice=data[entry]["NOT"]
            edition=data[entry]["EDI"]
            if sig == " ":
                continue
            if not notice == "":
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition,"ERR":"NOTICE_NOT_EMPTY_ERR"})
            self.read_write_json(folder=output_folder, input_file=done_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition})
    
    def main(self,resume:bool=False):
        """
        The main function of the program. It will run the bot on all entries in the input file.
        
        
        
        Args:
            - resume (bool, optional): Changes the run to detect older runs and remove the entries from the list, to remove duplicate work. Defaults to False.
        """
        input_folder, output_folder, file = self.main_startup()
        error_file = file.replace(".json","_error.json")
        done_file = file.replace(".json","_done.json")
        failed_file = file.replace(".json","_failed.json")
        #check if error file exists
        if not os.path.exists(f'{output_folder}/{error_file}'):
            with open(f'{output_folder}/{error_file}',"w",encoding="utf-8") as f:
                json.dump({},f,indent=4)
        if not os.path.exists(f'{output_folder}/{done_file}'):
            with open(f'{output_folder}/{done_file}',"w",encoding="utf-8") as f:
                json.dump({},f,indent=4)
        
        i=1
        with open(f'{input_folder}/{file}',"r",encoding="utf-8") as f:
            data=json.load(f)
        if resume==True:
            data=self.resume_run(data, output_folder)
        for entry in data:
            ppn=data[entry]["PPN"]
            sig=data[entry]["SIG"]
            notice=data[entry]["NOT"]
            edition=data[entry]["EDI"]
            if sig == " ":
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition,"ERR":"No signature"})
                continue
            if not notice == "":
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition,"ERR":"Notice not empty"})
                continue
            if self.testbot.run(ppn=ppn, signatur=sig)==False:
                send_notification(message=f"Skipped entry {entry} due to error",computer="test",type="error")
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition})
            else:
                send_notification(message=f"Completed entry {i}/{len(data)}",computer="test",type="info")
                self.read_write_json(folder=output_folder, input_file=done_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition})
            time.sleep(1)
            i+=1
            print(f"Completed entry {i}/{len(data)}")
        
    def control(self):
        controlbot = ControlBot()
        truly_done={}
        error_done={}
        with open("data/source/chemie_merged.json","r",encoding="utf-8") as f:
            test_data=json.load(f)
        for entry in test_data:
            ppn=test_data[entry]["PPN"]
            signatur=test_data[entry]["SIG"]
            notification=test_data[entry]["NOT"]
            edition=test_data[entry]["EDI"]
            if controlbot.run(ppn=ppn,signatur=signatur)==True:
                #send_embedded_message_control(ppn=ppn, signatur=signatur,message="Both fields were changed")
                with open("data/results/chemie.json","r",encoding="utf-8") as f:
                    data=json.load(f)
                curr_entry=len(data)+1
                truly_done[curr_entry]={"PPN":ppn,"SIG":signatur,"NOT":notification,"EDI":edition}
                with open("data/results/chemie.json","w",encoding="utf-8") as f:
                    json.dump(truly_done,f,indent=4)
            else:
                #send_embedded_message_control(ppn=ppn, signatur=signatur, message="One or more fields were not changed, see errors.json for more details")
                with open("data/results/errors.json","r") as f:
                    error_data = json.load(f)
                curr_error_entry=len(data)+1
                error_done[curr_error_entry]={"PPN":ppn,"SIG":signatur,"NOT":notification,"EDI":edition}
                with open("data/results/errors.json","r") as f:
                    json.dump(error_done,f,indent=4)   


    def resume_run(self,data,output_folder):
        full_data=data
        print(output_folder)
        #get data of run that was interrupted
        interruptedRun= output_folder.split("/")[-1].split("_")[1]
        interruptedRun=int(interruptedRun)-1
        #get files in output folder
        files=os.listdir(f'C:/rvkoutput/{date.today()}/run_{interruptedRun}')
        print(files[0])
        with open(f'C:/rvkoutput/{date.today()}/run_{interruptedRun}/{files[0]}',"r",encoding="utf-8") as f:
            completed_data=json.load(f)
        #count, how many entries were completed
        completed_entries=len(completed_data)
        #take the full_data and remove the completed entries
        entries_to_complete = {k: full_data[k] for k in list(full_data)[completed_entries:]}
        #write the entries_to _complete to a new file in the output folder
        with open(f"{output_folder}/run_{interruptedRun}_resume.json","w",encoding="utf-8") as f:
            json.dump(entries_to_complete,f,indent=4)
            
        return entries_to_complete
        # data
        
                    
         
            
if __name__ == "__main__":
    # autojson,manualjson = Preprocess(file="data/source/chemie_final.json", output_file="data/results/chemie_run.json", file_encoding="utf-8").main()
    # print(autojson,manualjson)
    # main=Main().run(autojson=autojson,manualjson=manualjson)       
    main=Main(debug=False).main(resume=False)
    

    
    # main=Main().main()
    
    #testing=Main(debug=True).main()
    
    
    # contrl=Main().control()
