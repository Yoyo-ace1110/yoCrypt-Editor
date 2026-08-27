echo "© Copyright Notice"
echo "2025-2026 Yoyo-ace1110. All Rights Reserved."

# --- 取得輸入檔案與設定檔 ---
INPUT_FILE="$1"
CONFIG_FILE="$2"

# 檢查輸入檔
if [ -z "$INPUT_FILE" ]; then
    echo "[Usage] ./compile.sh <filename.cpp> [config.cfg]"
    exit 1
fi

# 預設使用 default.cfg
if [ -z "$CONFIG_FILE" ]; then
    CONFIG_FILE="default.cfg"
fi

# 檢查設定檔是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[Error] Config file \"$CONFIG_FILE\" not found!"
    exit 1
fi

# Linux 的 Python 擴充模組副檔名為 .so
BASENAME=$(basename "$INPUT_FILE" .cpp)
OUTPUT_FILE="${BASENAME}_module.so"

echo "[Step] Compiling $INPUT_FILE using $CONFIG_FILE ..."
echo "command: [g++ \"$INPUT_FILE\" @\"$CONFIG_FILE\" $(python-config --includes) -o \"$OUTPUT_FILE\"]"

# --- 執行編譯 ---
g++ "$INPUT_FILE" "@$CONFIG_FILE" -o "$OUTPUT_FILE"

# --- 檢查結果 ---
if [ $? -eq 0 ]; then
    echo "[Success] Generated: $OUTPUT_FILE"
else
    echo "[Error] Compilation failed!"
    exit 1
fi

# chmod +x cpp/compile.sh 
