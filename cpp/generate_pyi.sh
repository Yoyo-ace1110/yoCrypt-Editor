echo "© Copyright Notice"
echo "2025-2026 Yoyo-ace1110. All Rights Reserved."

# --- 取得輸入模組名稱 ---
MODULE_NAME="$1"
STUB_DIR="temp_stubs"

if [ -z "$MODULE_NAME" ]; then
    echo "[Usage] ./generate_pyi.sh <module_name>"
    exit 1
fi

# 檢查 .so 是否存在 (Linux 的 Python 擴充模組副檔名為 .so)
if [ ! -f "${MODULE_NAME}.so" ]; then
    echo "[Error] ${MODULE_NAME}.so not found in current directory!"
    exit 1
fi

echo "[Step1] Building environment and generating stubs for $MODULE_NAME ..."

# --- 呼叫 stub_launcher.py (確保使用你的虛擬環境 python 或系統 python) ---
# 優先使用 .venv，若沒有則使用系統 python
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
else
    PYTHON_CMD="python"
fi

$PYTHON_CMD stub_launcher.py "$MODULE_NAME" -o "$STUB_DIR" --ignore-invalid-expressions ".*" --print-invalid-expressions-as-is

# --- 檢查執行結果 ---
if [ $? -eq 0 ]; then
    echo "[Step2] Success! Starting deep search for .pyi files..."
    
    # 顯示目前目錄下所有產出的檔案（診斷用）
    find "$STUB_DIR" -type f
    
    # 遍歷 temp_stubs 下所有 __init__.pyi 或 [模組名].pyi
    FOUND=""
    while IFS= read -r f; do
        if [ -n "$f" ]; then
            echo "[Found] Moving \"$f\" to \"./${MODULE_NAME}.pyi\""
            mv -f "$f" "./${MODULE_NAME}.pyi"
            FOUND="1"
        fi
    done < <(find "$STUB_DIR" -type f \( -name "__init__.pyi" -o -name "${MODULE_NAME}.pyi" \))

    if [ -n "$FOUND" ]; then
        echo "[Final] ${MODULE_NAME}.pyi is ready."
        rm -rf "$STUB_DIR"
    else
        echo "[Error] Stubgen finished but produced NO .pyi files."
        echo "[Check] Please check if C++ source still has manual type_caster."
    fi
else
    echo "[Error] Stub generation failed!"
    exit 1
fi

# pyi調整(開啟正規表達式): 
# 基本格式:
# 把 """\s*\n\s*(.*?)\n\s*"""  取代為 """ $1 """\n
# 把 :\s*\n\s*\.\.\.           取代為 : ...
# 看到C++名稱就取代掉，再檢查是否重複
# 跑clean_pyi.py
