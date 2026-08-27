@echo off
chcp 65001 > nul
setlocal

echo © Copyright Notice
echo 2025-2026 Yoyo-ace1110. All Rights Reserved.

:: --- 取得輸入模組名稱 ---
set MODULE_NAME=%~1
set STUB_DIR=temp_stubs

if "%MODULE_NAME%"=="" (
    echo [Usage] generate_pyi.bat ^<module_name^>
    goto :eof
)

:: 檢查 .pyd 是否存在
if not exist "%MODULE_NAME%.pyd" (
    echo [Error] %MODULE_NAME%.pyd not found in current directory!
    goto :eof
)

echo [Step1] Building environment and generating stubs for %MODULE_NAME% ...

:: --- 呼叫環境建構啟動器 ---
python stub_launcher.py %MODULE_NAME% -o %STUB_DIR% --ignore-invalid-expressions ".*" --print-invalid-expressions-as-is
:: python stub_launcher.py %MODULE_NAME% -o %STUB_DIR% --ignore-invalid-expressions ".*" --print-invalid-expressions-as-is

:: 在 Success 後面加入這段
if %errorlevel% equ 0 (
    echo [Step2] Success! Starting deep search for .pyi files...
    
    :: 顯示目前目錄下所有產出的檔案（診斷用）
    dir /s /b %STUB_DIR%
    
    :: 遍歷 temp_stubs 下所有 __init__.pyi 或 [模組名].pyi
    set "FOUND="
    for /f "delims=" %%f in ('dir /s /b %STUB_DIR%\__init__.pyi %STUB_DIR%\%MODULE_NAME%.pyi 2^>nul') do (
        echo [Found] Moving "%%f" to ".\%MODULE_NAME%.pyi"
        move /y "%%f" ".\%MODULE_NAME%.pyi" > nul
        set FOUND=1
    )

    if defined FOUND (
        echo [Final] %MODULE_NAME%.pyi is ready.
        rd /s /q "%STUB_DIR%"
    ) else (
        echo [Error] Stubgen finished but produced NO .pyi files.
        echo [Check] Please check if yoVec_pybind.cpp still has manual type_caster.
    )
)

endlocal
:eof

:: pyi調整(開啟正規表達式): 
:: 基本格式:
:: 把 """\s*\n\s*(.*?)\n\s*"""  取代為 """ $1 """\n
:: 把 :\s*\n\s*\.\.\.           取代為 : ...
:: 看到C++名稱就取代掉，再檢查是否重複
:: 跑clean_pyi.py
