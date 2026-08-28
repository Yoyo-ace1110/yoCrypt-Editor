#!/bin/bash

pyinstaller --clean --onedir --noconfirm --exclude-module PyQt5 --exclude-module PyQt6 --windowed --icon=main_icon.ico --name=main_x64 --distpath=./ main.py

if [ -d "yoCryptEditor" ]; then
    mv yoCryptEditor main_linux
fi

cp password.txt main_linux/
cp Welcome.txt main_linux/

echo "Successfully Build For Linux"
