import sys
from bot import Bot, ControlBot#,TestBot
import json
import time
from discord_notification import *
import os
from logger import Log
from preprocess import Create_Json, PDF_Create
input_folder = "C:/rvkinput"
output_folder = "C:/rvkoutput"

log=Log("data/logs/main.log")
class Main:
    def __init__(self, debug:bool=False) -> None:
        if not debug:
            self.testbot = Bot()
        self.manualdata={}
        self.donedata={}
        self.progess=0
        self.to_do=0
        pass
    
    def resume_file_present(self, input_folder, cur_file_name):
        prefix = "resume_"
        if type(cur_file_name)==list:
            for file in cur_file_name:
                if os.path.exists(f"{input_folder}/{prefix}{file}"):
                    return True
        else:
            if os.path.exists(f"{input_folder}/{prefix}{cur_file_name}"):
                return True
            return False
    
    def create_resume_file(self, data, subject_name):
        prefix = "resume_"
        if not os.path.exists(f"{input_folder}/{prefix}{subject_name}.json"):
            with open(f"{input_folder}/{prefix}{subject_name}.json","w",encoding="utf-8") as f:
                json.dump(data,f,indent=4)
        log.info(f"Created resume file for {subject_name}")
    
    def main_startup(self, resume:bool=False)->tuple[str,int,bool]:

        files_in_input = os.listdir(input_folder)
        resume_data={}
        res_file_present = False
        if resume==True:
            if self.resume_file_present(input_folder, files_in_input):
                print("Resume file found\n reading content")
                #pick the file with the "resume_" prefix
                open_file = [file for file in files_in_input if file.startswith("resume_")]
                with open(f"{input_folder}/{open_file[0]}","r",encoding="utf-8") as f:
                    resume_data = json.load(f)
                skip_entries = len(resume_data)
                
                # with open(f"{input_folder}/resume_{files_in_input[0]}","w",encoding="utf-8") as f:
                #     json.dump({},f,indent=4)
                res_file_present = True
            else:
                print("No resume file found")
                self.create_resume_file({},files_in_input[0])

        else:
            return files_in_input[0], 0, False
        if res_file_present:
            
            return open_file[0].replace("resume_",""), skip_entries, res_file_present
            
    
    def read_write_json(self, folder, input_file, payload:dict):
        with open(f'{folder}/{input_file}',"r",encoding="utf-8") as f:
            file_data=json.load(f)
        curr_entry=len(file_data)+1
        file_data[curr_entry]=payload
        with open(f'{folder}/{input_file}',"w",encoding="utf-8") as f:
            json.dump(file_data,f,indent=4)
        log.info(f"Written to {folder}/{input_file}")
        
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
        file, skip_titles ,resume_file_present= self.main_startup(resume=resume)
        error_file = file.replace(".json","_error.json")
        done_file = file.replace(".json","_done.json")
        #check if error file exists
        if not os.path.exists(f'{output_folder}/{error_file}'):
            with open(f'{output_folder}/{error_file}',"w",encoding="utf-8") as f:
                json.dump({},f,indent=4)
        if not os.path.exists(f'{output_folder}/{done_file}'):
            with open(f'{output_folder}/{done_file}',"w",encoding="utf-8") as f:
                json.dump({},f,indent=4)
        log.info(f"created files {error_file} and {done_file}")
        
        i=1
        with open(f'{input_folder}/{file}',"r",encoding="utf-8") as f:
            data=json.load(f)
            print(len(data))
        if resume==True:
            if resume_file_present==True:
                data=self.resume_run(data=data, skip_files=skip_titles)
        self.to_do=len(data)
        for entry in data:
            ppn=data[entry]["PPN"]
            sig=data[entry]["SIG"]
            notice=data[entry]["NOT"]
            edition=data[entry]["EDI"]
            if sig == " ":
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition,"ERR":"No signature"})
                print(f"Skipped entry {entry} due to error: No signature")
                self.read_write_json(folder=input_folder, input_file=f"resume_{file}", payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition})
                log.info(f'Skipped entry {entry} due to error: No signature')
                continue
            if not notice == "":
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition,"ERR":"Notice not empty"})
                continue
            if self.testbot.run(ppn=ppn, signatur=sig)==False:
                send_notification(message=f"Skipped entry {entry} due to error",computer="test",type="error")
                self.read_write_json(folder=output_folder, input_file=error_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition,"ERR:":"Error in testbot"})
            else:
                send_notification(message=f"Completed entry {i}/{len(data)}",computer="test",type="info")
                self.read_write_json(folder=output_folder, input_file=done_file, payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition})
                #write completed entry to resume file
                self.read_write_json(folder=input_folder, input_file=f"resume_{file}", payload={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition})
            time.sleep(1)
            print(f"Completed entry {i}/{len(data)}")
            self.progess=i
            i+=1
        
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

    def resume_run(self,data,skip_files:int):
        full_data=data
        #iterate over full data and remove entries that are already done
        entries_to_complete={}
        for id, content in enumerate(full_data):
            if id>=skip_files:
                entries_to_complete[content]=full_data[content]
        
        # with open(f'{input_folder}/resume_.json',"w",encoding="utf-8") as f:
        #     json.dump(entries_to_complete,f,indent=4)
        print(len(entries_to_complete))
        log.info(f"Resuming run with {len(entries_to_complete)} entries")
        #get data of run that was interrupted
        
            
        return entries_to_complete
        # data
    
    def exit_handler(self):
        message="@everyone\n\n Der Bot wurde beendet, entweder durch einen Fehler, oder der Durchlauf wurde beendet. Bitte prüfen und ggf. neu starten. "
        send_restart(message=message) 
                    
         
            
if __name__ == "__main__":
    # autojson,manualjson = Preprocess(file="data/source/chemie_final.json", output_file="data/results/chemie_run.json", file_encoding="utf-8").main()
    # print(autojson,manualjson)
    # main=Main().run(autojson=autojson,manualjson=manualjson)   
    main=Main(debug=False)#.main(resume=True)
    try:    
        main.main(resume=True)
    except:
        main.exit_handler()
    finally:
        print("Done")
        print(main.progess,main.to_do)
        if main.progess==main.to_do:
            from post import post
            post(dupes=True)
        sys.exit()
    # main=Main().main()
    
    #testing=Main(debug=True).main()
    
    
    # contrl=Main().control()
