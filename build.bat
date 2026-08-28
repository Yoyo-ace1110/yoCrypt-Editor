@echo off
chcp 65001 >nul

pyinstaller --clean --onedir --exclude-module PyQt5 --exclude-module PyQt6 --windowed --icon=main_icon.ico --name=yoCryptEditor --distpath=./ main.py

if exist yoCryptEditor (
    ren yoCryptEditor main_x64
)

copy password.txt main_x64\
copy Welcome.txt main_x64\

echo Successfully Build For Windows
