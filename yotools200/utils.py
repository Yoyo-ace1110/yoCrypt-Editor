import time
import sys
import os

def empty_func() -> None: pass

def true_func(point) -> bool: return True

def memory_address(any): return hex(id(any))

def is_chinese(ch: str): 
    """ 判斷是否為中文 """
    if len(ch) != 1: raise ValueError("is_chinese() 只接受單一字元")
    return '\u4e00' <= ch <= '\u9fff'

def is_punctuation(ch: str):
    """ 判斷是否為標點 """
    import regex
    if len(ch) != 1: raise ValueError("is_punctuation() 只接受單一字元")
    return regex.match(r'\p{P}|\p{S}', ch) is not None

def resource_path(relative_path: str) -> str:
    """支援 PyInstaller 打包後讀取資源(動態讀寫)"""
    if getattr(sys, 'frozen', False): base_path = os.path.dirname(sys.executable)
    else: base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)

class Code_Timer:
    def __init__(self, label: str):
        self.label = label

    def __enter__(self):
        self.start =  time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start) * 1000
        print(f"{self.label:<10}: {duration_ms:.4f} ms")
