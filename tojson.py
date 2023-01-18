import json
import time

import csv
import regex as re

onedata="""SET: Pica2rvk-Export TTL: 960          PPN: 1078722234  
4000 dtv-Atlas zur Chemie; Tafeln und Texte
4170 dtv$l...
1100 19XX
3000 Breuer, Hans
5090 VC 5020 [Chemie und Pharmazie / Allgemeine Chemie; Mathematik, Statistik und Datenverarbeitung in Chemie und Pharmazie / Allgemeine Chemie / Kompendien, Repetitorien, Leitfäden, Kurzdarstellungen, Vorlesungsskripten]
5500 |s| |a|Chemistry |a|Outlines
5550 Chemie ; ID: gnd/4009816-3
E001 10-12-92 : l01
7101 Che A 6: 10
RVK40011 VC 1000
RVK40013 202
RVK40014 B846
RVK40015 GA<<mybrNEWLINE>>dies ist die falsche GA
DSTATUS42001 false
DSTATUS42002 false
DSTATUS42003 true
"""



# print(datastr)

def create_dict(data):
    data = data.split('\n')
    data = [x for x in data if x != '']
    data = [x.split(' ',maxsplit=1) for x in data]
    data = {x[0]:x[1] for x in data}
    return data
def create_usable_data(data):

    try:
        ppnreg=re.compile(r'PPN: (\d+)')
        ppn=ppnreg.search(data).group(1)
    except AttributeError:
        ppn = None
    try:
        issuereg=re.compile(r'4020 (\d+)')
        issue=issuereg.search(data).group(1)
    except AttributeError:
        issue = None
    try:
        rvk_cutter_reg=re.compile(r'RVK40014 (.*)')
        rvk_notation_reg=re.compile(r'RVK40011 (.*)')
        rvk_notation=rvk_notation_reg.search(data).group(1)
        signature = f'{rvk_notation} {rvk_cutter_reg.search(data).group(1)}'
    except AttributeError:
        signature = None
    try:
        notes_reg=re.compile(r'RVK40015 (.*)')
        notes = notes_reg.search(data).group(1)
    except AttributeError:
        notes = None
    dataframe = {
        "ppn": ppn,
        "issue": issue,
        "signature": signature,
        "notes": notes
    }

    return dataframe

def create_json(file, output_file,file_encoding="utf-8"):
    datafile = open(file, "r",encoding=file_encoding)
    data = datafile.read()
    datastr = data.split('\n\n')
    datafile.close()
    line_index=1
    notes_index=1
    json_entries={}
    notes_json_entries={}
    for line in datastr:
        df=create_usable_data(line)
        print(df)
        if df["notes"] != None:
            if "<<mybrNEWLINE>>" in df["notes"]:
                df["notes"]=df["notes"].replace("<<mybrNEWLINE>>"," ")
            notes_json_entries[notes_index]=df
            notes_index+=1
        else:# add data to json, use line_index as key
            json_entries[line_index]=df
            line_index+=1


    with open(output_file, 'a') as outfile:
        json.dump(json_entries, outfile, indent=4,sort_keys=False,ensure_ascii=False)
    notes_file=output_file.replace(".json","_notes.json")
    with open(notes_file, 'a') as outfile:
        json.dump(notes_json_entries, outfile, indent=4,sort_keys=False,ensure_ascii=False)


# def remove_entries_with_notes(file, output_file):
#     #iterate through json file, remove entries with notes add them to a new file
#     new_json={}
#     with open(file, 'r') as json_file:
#         data = json.load(json_file)
#         for key in data:
#             if data[key]["notes"] == None:
#                 continue
#             else:
#                 new_json[key]=data[key]
#                 data.
#     with open(output_file, 'a') as outfile:
#         json.dump(new_json, outfile, indent=4,sort_keys=False,ensure_ascii=False)
create_json(file="data/source/chemie_raw.txt",output_file="data/chemies.json") 

# remove_entries_with_notes(file="data/chemie copy.json",output_file="data/chemie_notes.json")

