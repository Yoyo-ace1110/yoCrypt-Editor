# Copyright (C) 2026 Yoyo-ace1110
import base64, os
current_path = os.path.dirname(os.path.abspath(__file__))
mingw_bin = os.path.join(current_path, r"dll")
if os.path.exists(mingw_bin):
    os.add_dll_directory(os.path.abspath(mingw_bin))
else:
    print(f"[Env] Warning: MinGW bin not found at {mingw_bin}")
import yoCryptCpp_pybind_module

def yoCrypt_init(count: int = 360000, salt_size: int = 16, hash_len: int = 32):
    """ 初始化C++核心參數 """
    yoCryptCpp_pybind_module.yoCrypt_init(count, salt_size, hash_len)

def secure_clear(data: bytearray):
    """ 手動呼叫 C++ 核心進行記憶體覆寫 """
    yoCryptCpp_pybind_module.secure_clear(data)

def hash_password(password: bytearray) -> str:
    """ 呼叫C++進行PBKDF2運算 並在Python端格式化 (會自動清除傳入的密碼) """
    raw_res_list = yoCryptCpp_pybind_module.hash_password(password)
    # 取得原始 bytes (salt + key)
    raw_res = bytes(raw_res_list)
    
    # 拆分 salt (16 bytes) 與 key (其餘)
    salt = raw_res[:16]
    key = raw_res[16:]
    
    # 取得目前的迭代次數
    salt_b64 = base64.b64encode(salt).decode()
    key_b64 = base64.b64encode(key).decode()
    return f"pbkdf2_sha256$360000${salt_b64}${key_b64}"

def verify_password(password: bytearray, stored: str) -> bool:
    """ C++驗證 (會自動清除傳入的密碼) """
    try:
        parts = stored.split('$')
        if len(parts) != 4: return False
        iterations = int(parts[1])
        # vector<unsigned char>
        salt = list(base64.b64decode(parts[2]))
        expected_key = list(base64.b64decode(parts[3]))
        # 呼叫 C++
        return yoCryptCpp_pybind_module.verify_password(password, salt, expected_key, iterations)
    except Exception as e:
        print(f"Verify Error: {e}")
        return False

class yoAES:
    @staticmethod
    def encrypt(plain_text: str, password: bytearray) -> str:
        """ 將明文轉為bytes後交給C++加密 (會自動清除傳入的密碼) """
        plain_bytes = list(plain_text.encode('utf-8'))
        # C++ 回傳 salt + nonce + tag + ciphertext
        raw_encrypted = yoCryptCpp_pybind_module.AES_encrypt(plain_bytes, password)
        return base64.b64encode(bytes(raw_encrypted)).decode('utf-8')

    @staticmethod
    def decrypt(encrypted_text: str, password: bytearray) -> str:
        """ 解碼Base64後交給C++解密並驗證 """
        raw_data = list(base64.b64decode(encrypted_text))
        # C++ 會驗證 Tag，失敗會拋出 RuntimeError
        decrypted_bytes = yoCryptCpp_pybind_module.AES_decrypt(raw_data, password)
        return bytes(decrypted_bytes).decode('utf-8')
