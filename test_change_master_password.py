import os
import shutil

# 測試設定
TEST_DIR = "Files"
PASSWORD_FILE = "password.txt"

def reset_test_env():
    """ 每次測試前重置資料夾與檔案 """
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    
    # 建立三個測試檔案
    # 假設舊密碼加密後的內容如下 (這裡用明文模擬，測試時請確保你能解密它們)
    files = {
        "file1.txt": "這是第一個檔案的內容",
        "file2.txt": "這是第二個檔案的內容",
        "file3.txt": "這是第三個檔案的內容"
    }
    
    for name, content in files.items():
        with open(os.path.join(TEST_DIR, name), "w", encoding="utf-8") as f:
            # 注意: 這裡應該填入你用「舊密碼」加密過的字串
            f.write(content) 
    print("--- 測試環境已就緒 ---")

# --- 情境模擬區 ---

def trigger_scenario(scenario_num):
    reset_test_env()
    
    if scenario_num == 1:
        print("情境 1: 全都成功。不用做任何破壞。")
        
    elif scenario_num == 2:
        print("情境 2: 解密階段失敗。")
        # 破壞方式: 把 file2.txt 改成亂碼，讓 yoAES.decrypt 噴 Exception
        with open(os.path.join(TEST_DIR, "file2.txt"), "w") as f:
            f.write("I am totally corrupted data")
            
    elif scenario_num == 3:
        print("情境 3: 加密階段失敗。")
        # 破壞方式: 在解密完成後，手動把 file3.txt 設為唯讀
        # 這樣在「嘗試加密儲存」寫入 file3 時會噴 PermissionError
        fpath = os.path.join(TEST_DIR, "file3.txt")
        os.chmod(fpath, 0o444) # 設為唯讀
        print(f"已將 {fpath} 設為唯讀，模擬寫入失敗")
        
    elif scenario_num == 4:
        print("情境 4: 連復原也失敗。")
        # 破壞方式: 先讓加密失敗，同時把所有檔案權限鎖死
        # 這樣加密寫不進去，連 Rollback 想寫入舊資料也會失敗
        for fname in os.listdir(TEST_DIR):
            os.chmod(os.path.join(TEST_DIR, fname), 0o444)
        print("所有檔案已鎖死，加密與復原都將失敗")

trigger_scenario(3)
