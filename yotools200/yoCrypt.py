from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import base64
import os
import hmac

_count: int
_salt_size: int
_hash_len: int
_already_init = False

def yoCrypt_init(count: int = 200*1000, salt_size: int = 16, hash_len: int = 32, encoding: str = "utf-8"):
    global _count, _already_init, _salt_size, _hash_len, _encoding
    if _already_init: return print(f"yoCrypt has already init: count = {_count}")
    _count = count
    _salt_size = salt_size
    _hash_len = hash_len
    _encoding = encoding
    _already_init = True

def _ensure_init(): 
    if not _already_init: raise RuntimeError("yoCrypt has not init yet")
    return True

def _ensure_bytes(password: str|bytes|bytearray):
    """ 確保是正確型別 """
    _ensure_init()
    if isinstance(password, bytearray):
        return bytes(password)
    if isinstance(password, str):
        return password.encode(_encoding)
    return password

def _try_clear(password: str|bytes|bytearray):
    if isinstance(password, bytearray):
        for i in range(len(password)):
            password[i] = 0

def hash_password(password: str|bytes|bytearray) -> str:
    """ 將傳入的密碼雜湊 """
    password = _ensure_bytes(password)
    salt = os.urandom(_salt_size)
    key = PBKDF2(password, salt, dkLen=_hash_len , count=_count, hmac_hash_module=SHA256)
    _try_clear(password)
    del password
    return f"pbkdf2_sha256${_count}${base64.b64encode(salt).decode()}${base64.b64encode(key).decode()}"

def verify_password(password: str|bytes|bytearray, stored: str) -> bool:
    password = _ensure_bytes(password)
    try:
        algo, iter_str, salt_b64, key_b64 = stored.split("$")
        if algo != "pbkdf2_sha256": raise ValueError("Unsupported algorithm")
        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64)
        key = base64.b64decode(key_b64)
        new_key = PBKDF2(password, salt, dkLen=len(key), count=iterations, hmac_hash_module=SHA256)
        _try_clear(password)
        del password
        return hmac.compare_digest(new_key, key)
    except Exception as e: raise e

# 加密函數
class yoAES:
    @staticmethod
    def encrypt(plain_text: str, password: str|bytes|bytearray):
        password = _ensure_bytes(password)
        salt = get_random_bytes(_salt_size)
        key = PBKDF2(password, salt, dkLen=_hash_len, count=_count)
        _try_clear(password)
        del password
        cipher = AES.new(key, AES.MODE_GCM)
        cipher_text, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))
        encrypted_data = base64.b64encode(salt + cipher.nonce + tag + cipher_text).decode('utf-8')
        return encrypted_data
    @staticmethod
    def decrypt(encrypted_text: str, password: str|bytes|bytearray):
        password = _ensure_bytes(password)
        data = base64.b64decode(encrypted_text)
        salt, nonce, tag, cipher_text = data[:16], data[16:32], data[32:48], data[48:]
        key = PBKDF2(password, salt, dkLen=32, count=_count)
        _try_clear(password)
        del password
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plain_text = cipher.decrypt_and_verify(cipher_text, tag).decode('utf-8')
        return plain_text
