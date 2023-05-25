REM Check if Python is installed

python -c "import sys" 2> NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO Python is not installed, grabbing it now...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe -OutFile python-3.10.6-amd64.exe"
    ECHO Installing Python...
    python-3.10.6-amd64.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    ECHO Python is installed, continuing...
    ECHO Installing dependencies...
    pip install -r requirements.txt
    ECHO Dependencies installed, continuing...
    ECHO Prior to launching the bot, please start aDIS and move to the KatalogModul
    ECHO Press any key to continue...
    
)
pip install -r requirements.txt
ECHO Python und Abhängigkeiten sind installiert, weiter...
ECHO Test, ob Teseract installiert ist...
@REM test if C:\rvkinput and C:\rvkoutput exist
if exist C:\tesseract (
    ECHO Tesseract ist installiert, weiter...
) else (
    ECHO Tesseract ist nicht installiert, bitte installieren
    REM Copy a folder from a shared network drive to the local machine
    xcopy "Y:\Gruppen\Bibliothek-Allgemeines\Ausbildungsordner\Alexander Kirchner\bib_data\tesseract" "C:\tesseract" /E /I /H /Y
    REM Set the environment variable
    set tess_installed=true
    ECHO Press any key to continue...
    PAUSE
)
ECHO Test, ob C:\rvkinput und C:\rvkoutput existieren...
@REM test if C:\rvkinput and C:\rvkoutput exist
if exist C:\rvkinput (
    ECHO C:\rvkinput existiert, weiter...
) else (
    ECHO C:\rvkinput existiert nicht, wird erstellt
    mkdir C:\rvkinput
    ECHO Press any key to continue...
    PAUSE
)	
if exist C:\rvkoutput (
    ECHO C:\rvkoutput existiert, weiter...
) else (
    ECHO C:\rvkoutput existiert nicht, wird erstellt
    mkdir C:\rvkoutput
    ECHO Press any key to continue...
    PAUSE
)
@REM create a shortcut to the folder c:\rvkinput
@REM check if the shortcut already exists
if exist C:\rvkinput.lnk (
    ECHO C:\rvkinput.lnk existiert, weiter...
) else (
    ECHO C:\rvkinput.lnk existiert nicht, wird erstellt
    @REM get the username
    username=$(whoami)
    @REM create the shortcut

    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('C:\Users\%username%\Desktop\rvkinput.lnk'); $Shortcut.TargetPath = 'C:\rvkinput'; $Shortcut.Save()"
    ECHO Press any key to continue...
    PAUSE
)
ECHO Befor der Bot gestartet wird, bitte aDIS starten und in das Katalogmodul wechseln
@REM REM ECHO Press any key to continue...
PAUSE
ECHO Starte den Bot...
@REM python main.py
EXIT