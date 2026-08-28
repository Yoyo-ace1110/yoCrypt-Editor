@echo off
chcp 65001 >nul

pyinstaller --clean --onedir --noconfirm --exclude-module PyQt5 --exclude-module PyQt6 --windowed --icon=main_icon.ico --name=main_x64 --distpath=./ main.py

ren main_x64\main_x64.exe yoCryptEditor.exe
copy password.txt main_x64\
copy Welcome.txt main_x64\

echo Successfully Build For Windows
