import bot
import json
import time
from discord_notification import *
from preprocess import Preprocess




class Main:
    def __init__(self) -> None:
        self.testbot = bot.TestBot()
        pass
    
    def run(self,autojson,manualjson):
        with open(autojson,"r",encoding="utf-8") as f:
            data=json.load(f)
            
        for entry in data:
            ppn=data[entry]["PPN"]
            sig=data[entry]["SIG"]
            notice=data[entry]["NOT"]
            edition=data[entry]["EDI"]
            if sig == " ":
                continue
            if self.testbot.run(ppn=ppn, signatur=sig)==False:
                #add entry to manual json
                with open(manualjson,"r",encoding="utf-8") as f:
                    manual_data=json.load(f)
                curr_entry=len(manual_data)+1
                manual_data[curr_entry]={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition}
                with open(manualjson,"w",encoding="utf-8") as f:
                    json.dump(manual_data,f,indent=4)
                continue
            else:
                #remove entry from auto json
                del data[entry]
                with open(autojson,"w",encoding="utf-8") as f:
                    json.dump(data,f,indent=4)
                continue
       
       
    def test(self,file):
        manualdata={}
        donedata={}
        i=1
        with open(file,"r",encoding="utf-8") as f:
            data=json.load(f)
        for entry in data:
            ppn=data[entry]["PPN"]
            sig=data[entry]["SIG"]
            notice=data[entry]["NOT"]
            edition=data[entry]["EDI"]
            if sig == " ":
                continue
            if self.testbot.run(ppn=ppn, signatur=sig)==False:
                send_notification(message=f"Skipped entry {entry} due to error",computer="test",type="error")
                with open("data/source/this_testrun_manual.json","r",encoding="utf-8") as f:
                    error_data=json.load(f)
                curr_entry=len(error_data)+1
                manualdata[curr_entry]={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition}
                with open("data/source/this_testrun_manual.json","w",encoding="utf-8") as f:
                    json.dump(manualdata,f,indent=4)
            send_notification(message=f"Completed entry {i}/{len(data)}",computer="test",type="info")
            with open("completed.json","r",encoding="utf-8") as f:
                completed_data=json.load(f)
            curr_entry=len(completed_data)+1
            donedata[curr_entry]={"PPN":ppn,"SIG":sig,"NOT":notice,"EDI":edition}
            with open("completed.json","w",encoding="utf-8") as f:
                json.dump(donedata,f,indent=4)
            i+=1
        
    def control(self):
        controlbot = bot.ControlBot()
        truly_done={}
        with open("data/source/chemie_merged.json","r",encoding="utf-8") as f:
            test_data=json.load(f)
        for entry in test_data:
            ppn=test_data[entry]["PPN"]
            signatur=test_data[entry]["SIG"]
            notification=test_data[entry]["NOT"]
            edition=test_data[entry]["EDI"]
            if controlbot.run(ppn=ppn,signatur=signatur)==True:
                with open("data/results/chemie.json","r",encoding="utf-8") as f:
                    data=json.load(f)
                curr_entry=len(data)+1
                truly_done[curr_entry]={"PPN":ppn,"SIG":signatur,"NOT":notification,"EDI":edition}
                
        # # testbot = bot.TestBot()
        # with open(manualjson,"w",encoding="utf-8") as f:
        #     data=json.load(f)
        # for i in data:
        #     ppn = data[i]["PPN"]
        #     signature = data[i]["SIG"]
        #     edition = data[i]["EDI"]
        #     notice = data[i]["NOT"]
            
        #     with open(manualjson,"r",encoding="utf-8") as f:
        #         auto_data=json.load(f)
            
        #     if testbot.run(ppn=ppn, signatur=signature)==None:
        #         print("failed")
        #     with open(manualjson,"w",encoding="utf-8") as f:
        #         this_data={
        #             "PPN":ppn,
        #             "SIG":signature,
        #             "EDI":edition,
        #             "NOT":notice
        #         }
            
        #         json.update(f,this_data)
        #     send_notification(f"Failed at {i}/{len(data)}","Computer Alexander","error")
        #     #     break
        #     # else:
        #     #     print("success")
        #     # time.sleep(30)
        #     # # send_notification(f"{i}/{len(data)}","Computer Alexander","info")
            
            
            
            
            
if __name__ == "__main__":
    # autojson,manualjson = Preprocess(file="data/source/newexport.json", output_file="data/source/trial.json", file_encoding="utf-8").main()
    # print(autojson,manualjson)
    # main=Main().run(autojson=autojson,manualjson=manualjson)       
    main=Main().test(file="data/test.json")
# testbot = bot.TestBot()

# jsonfile = "data/source/newexport.json"

# with open(jsonfile, "r", encoding="utf-8") as f:
#     jsonfile = json.load(f)
#     print(len(jsonfile))
# for i in jsonfile:
#     ppn = jsonfile[i]["PPN"]
#     signature = jsonfile[i]["SIG"]
#     if testbot.run(ppn=ppn, signatur=signature)==False:
#         print("failed")
#         with open()
#         continue
#     else:
#         print("success")
#     time.sleep(3)
#     send_notification(f"{i}/{len(jsonfile)}","Computer Alexander","info")
