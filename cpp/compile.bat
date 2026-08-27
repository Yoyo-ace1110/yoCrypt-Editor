@echo off
chcp 65001 > nul
setlocal

echo © Copyright Notice
echo 2025-2026 Yoyo-ace1110. All Rights Reserved.

:: --- 取得輸入檔案與設定檔 ---
set INPUT_FILE=%~1
set CONFIG_FILE=%~2

:: 檢查輸入檔
if "%INPUT_FILE%"=="" (
    echo [Usage] compile.bat ^<filename.cpp^> ^<config.cfg^>
    goto :eof
)

:: 預設使用 defualt.cfg
if "%CONFIG_FILE%"=="" (
    set CONFIG_FILE=defualt.cfg
)

:: 檢查設定檔是否存在
if not exist "%CONFIG_FILE%" (
    echo [Error] Config file "%CONFIG_FILE%" not found!
    goto :eof
)

set OUTPUT_FILE=%~n1_module.pyd

echo [Step] Compiling %INPUT_FILE% using %CONFIG_FILE% ...
echo command: [g++.exe "%INPUT_FILE%" @%CONFIG_FILE% -o "%OUTPUT_FILE%"]

:: --- 執行編譯 ---
g++.exe "%INPUT_FILE%" @%CONFIG_FILE% -o "%OUTPUT_FILE%"

:: --- 檢查結果 ---
if %errorlevel% equ 0 (
    echo [Success] Generated: %OUTPUT_FILE%
) else (
    echo [Error] Compilation failed!
)

endlocal
:eof
