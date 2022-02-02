@echo off

@echo Creating Python env..
C:\RoboDK\Python37\python.exe -m venv .\env

:: Use this for Python 2.7
::C:\RoboDK\Python37\python.exe -m pip install virtualenv
::C:\RoboDK\Python37\python.exe -m virtualenv --python=C:\Python27\python.exe .\env

@echo Activating Python env..
CALL .\env\Scripts\activate.bat

@echo Installing requirements..
python -m pip install -r requirements.txt

@echo Adding to PATH:
set PATH=%VIRTUAL_ENV%;%PATH%
echo %PATH%