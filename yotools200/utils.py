import os
import sys
import time
from typing import Any

# --- resource_path ---

def resource_path(relative_path: str) -> str:
    """
    獲取資源文件的絕對路徑。
    用於 PyInstaller 打包時，將資源文件從臨時目錄 (sys._MEIPASS) 讀取出來。
    當作為腳本運行時，它返回相對於腳本的路徑。
    """
    try:
        # PyInstaller 創建的臨時資料夾路徑
        # 這是當程式被打包成單一執行檔時資源檔案所在的路徑
        base_path = sys._MEIPASS
    except Exception:
        # 當程式以 .py 腳本運行時
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Code_Timer ---

class Code_Timer:
    """
    程式碼計時器 (Context Manager)。
    使用 with 語句測量程式碼區塊的執行時間。
    """
    def __init__(self, name: str = "Code Block"):
        self.name = name
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __enter__(self) -> 'Code_Timer':
        """ 進入 with 區塊時記錄開始時間 """
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """ 離開 with 區塊時記錄結束時間並打印結果 """
        self.end_time = time.perf_counter()
        elapsed_time = self.end_time - self.start_time
        print(f"[{self.name}] 執行時間: {elapsed_time:.4f} 秒")
        # 如果需要，您可以將時間儲存起來
        self.elapsed = elapsed_time
        