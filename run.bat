@REM REM Check if Python is installed

python -c "import sys" 2> NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO Python is not installed, grabbing it now...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe -OutFile python-3.10.6-amd64.exe"
    ECHO Installing Python...
    python-3.10.6-amd64.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    ECHO Python is installed, continuing...
    ECHO Installing dependencies...
    pip install -r reqs.txt    
)
@REM pip install -r requirements.txt
ECHO Python und Abhängigkeiten sind installiert, weiter...
ECHO Test, ob Teseract installiert ist...
@REM test if C:\rvkinput and C:\rvkoutput exist
if exist C:\tesseract (
    ECHO Tesseract ist installiert, weiter...
) else (
    ECHO Tesseract ist nicht installiert, wird installiert
    REM Copy a folder from a shared network drive to the local machine
    xcopy "Y:\Gruppen\Bibliothek-Allgemeines\Ausbildungsordner\Alexander Kirchner\bib_data\tesseract" "C:\tesseract" /E /I /H /Y
    REM Set the environment variable
)
ECHO Test, ob C:\rvkinput und C:\rvkoutput existieren...
@REM test if C:\rvkinput and C:\rvkoutput exist
if exist C:\rvkinput (
    ECHO C:\rvkinput existiert, weiter...
) else (
    ECHO C:\rvkinput existiert nicht, wird erstellt
    mkdir C:\rvkinput
)	
if exist C:\rvkbackup (
    ECHO C:\rvkbackup existiert, weiter...
) else (
    ECHO C:\rvkbackup existiert nicht, wird erstellt
    mkdir C:\rvkbackup
)	

if exist C:\rvkoutput (
    ECHO C:\rvkoutput existiert, weiter...
) else (
    ECHO C:\rvkoutput existiert nicht, wird erstellt
    mkdir C:\rvkoutput
)
@REM create a shortcut to the folder c:\rvkinput
@REM check if the shortcut already exists
@echo off
if exist C:\rvkinput.lnk (
    ECHO C:\rvkinput.lnk existiert, weiter...
) else (
    ECHO C:\rvkinput.lnk existiert nicht, wird erstellt
    @REM get the username
    username=$(whoami)
    @REM create the shortcut
    @echo off
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('C:\Users\%username%\Desktop\rvkinput.lnk'); $Shortcut.TargetPath = 'C:\rvkinput'; $Shortcut.Save()"
)
Echo wird ein neues Fach geladen, oder ein altes bearbeitet? 
set /p fach=(n(eu) / a(lt))
@REM echo %fach%
if %fach%==n (
    ECHO Neues Fach wird geladen... bitte die aus Oberfell gespeicherte TXT Datei in den rvkinput Ordner kopieren und alle alten Dateien löschen
    PAUSE
    @REM copy the created txt file to the rvkinput folder
    @REM check folder content
    if exist C:\rvkinput\*.txt (
        ECHO TXT Datei gefunden, weiter...
    ) else (
        ECHO TXT Datei nicht gefunden, bitte in den rvkinput Ordner kopieren
        ECHO Press any key to continue...
        PAUSE
    )
    python pre.py
    ECHO Press any key to continue...
    PAUSE
) else (
    ECHO Altes Fach wird bearbeitet...
)
ECHO Befor der Bot gestartet wird, bitte aDIS starten und in das Katalogmodul wechseln
@REM REM ECHO Press any key to continue...
PAUSE
ECHO Starte den Bot...
python main.py
ECHO Bot beendet, bitte rvkoutput Ordner prüfen

EXIT