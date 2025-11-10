@echo off
chcp 65001 > nul

set dir="C:\Users\yosprout\Desktop\Codes\python\pyQT\yoCrypt_Editor"
set python_path="C:\Users\yosprout\AppData\Local\Programs\Python\Python311"
cd /d "%dir%"
REM "%dir%\main.exe %1"
"%python_path%\python.exe" -u "%dir%\main.py" "%1"
