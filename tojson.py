import json
import time

import csv
import regex as re

data="""SET: Pica2rvk-Export TTL: 767          PPN: 019577621  
2000 3-7985-0803-8
4000 Einf�hrung in die St�chiometrie; kurzes Lehrbuch der allgemeinen und physikalischen Chemie ; mit 516 Aufgaben und L�sungen
4020 18., vollst. �berarb. Aufl.
1100 1991
3000 Nyl�n, Paul ; ID: gnd/1055138005
5090 VC 5200 [Chemie und Pharmazie / Allgemeine Chemie; Mathematik, Statistik und Datenverarbeitung in Chemie und Pharmazie / Allgemeine Chemie / Aufgabensammlungen; "Problem und Antwort"; Chemisches Rechnen; SI-Einheiten; St�chiometrie (-) s.a. VB 4090 Lern- und Pr�fungsprogramme s.a. VC 6000 ff.]
5550 St�chiometrie ; ID: gnd/4057657-7
E001 26-08-93 : l01
7101 Che A 300: 3
RVK40011 VC 5200
RVK40012 Chemie und Pharmazie / Allgemeine Chemie; Mathematik, Statistik und Datenverarbeitung in Chemie und Pharmazie / Allgemeine Chemie / Aufgabensammlungen; "Problem und Antwort"; Chemisches Rechnen; SI-Einheiten; St�chiometrie (-) s.a. VB 4090 Lern- und Pr�fungsprogramme s.a. VC 6000 ff.
RVK40013 201
RVK40014 N995 (18)
DSTATUS42001 false
DSTATUS42002 false
DSTATUS42003 false
"""

datafile = open("chemieExport.txt", "r",encoding="ISO-8859-1")
data = datafile.read()
datastr = data.split('\n\n')


print(datastr)

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
        notes_reg=re.compile(r'RVK50015 (.*)')
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
line_index=1
json_entries={}
for line in datastr:
    df=create_usable_data(line)
    print(df)
    # add data to json, use line_index as key
    
    json_entries[line_index]=df
    line_index+=1


with open('testdata.json', 'a') as outfile:
    json.dump(json_entries, outfile, indent=4,sort_keys=False,ensure_ascii=False)
    
    

