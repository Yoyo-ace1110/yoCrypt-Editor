# Copyright 2026 (C) Yoyo-ace1110 Corporation. All rights reserved.
from PySide6.QtGui import QShowEvent
import sys, os, qdarktheme 
import collections.abc
from enum import Enum
from typing import Union, Sequence
from abc import abstractmethod, ABCMeta
from PySide6.QtWidgets import * # pyright: ignore[reportWildcardImportFromLibrary]
from PySide6.QtCore import * # pyright: ignore[reportWildcardImportFromLibrary]
from PySide6.QtGui import * # pyright: ignore[reportWildcardImportFromLibrary]
from yoCryptCpp import * # pyright: ignore[reportWildcardImportFromLibrary]
from yotools200.utils import resource_path, Code_Timer
yoCrypt_init(360000, 16, 32)

encoding = "utf-8"
"""
password_file = resource_path("password.txt")
welcome_file = resource_path("Welcome.txt")
filedirname = os.path.dirname(os.path.abspath(__file__))
"""
password_file = resource_path("../password.txt")
welcome_file = resource_path("../Welcome.txt")
filedirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

default_font_size = 3
window: "MainWindow"
ShortcutType = Union[
    QKeySequence, 
    QKeyCombination, 
    QKeySequence.StandardKey, 
    str, 
    int, 
    Sequence[QKeySequence]
]

# using FR = find_and_replace;

# 函數
def _clear_dialog_input(dialog: QDialog):
    """ 清除QDialog的內容 """
    for widget in dialog.findChildren(QLineEdit):
        widget.clear()

# 密碼驗證
class PasswordPrompt(QDialog):
    """ Verifying Master Password """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主密碼驗證")
        self.setFixedSize(300, 140)
        layout = QVBoxLayout()

        self.label = QLabel("請輸入主密碼")
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.button = QPushButton("確定")

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.button.clicked.connect(self.try_login)

        self.password = bytearray()
        self.success = False
        self.fail_count = 0
        self.locked = False
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.unlock)

    def try_login(self):
        if self.locked:
            QMessageBox.warning(self, "請稍候", "您輸入錯誤太多次 請等待30秒後再試")
            return
        raw_password_str = self.input.text()
        password = bytearray(raw_password_str, encoding)
        self.input.clear()
        del raw_password_str
        try:
            # 讀取hashed_password
            hash_file = open(password_file, "r")
            stored_hash = hash_file.read().strip()
            hash_file.close()
            # 驗證成功
            if verify_password(password, stored_hash):
                self.success = True
                self.password = password
                del password
                self.accept()
            # 驗證失敗
            else:
                secure_clear(password)
                self.fail_count += 1
                if self.fail_count >= 5:
                    self.locked = True
                    self.label.setText("錯誤達5次 請等待30秒後再試")
                    self.button.setEnabled(False)
                    self.timer.start(30 * 1000)  # 30秒
                else: QMessageBox.warning(self, "錯誤", f"密碼錯誤，您還有{5 - self.fail_count}次機會")
        except FileNotFoundError:
            QMessageBox.critical(self, "錯誤", f"找不到 {password_file}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"驗證密碼失敗: {e}")

    def unlock(self):
        self.fail_count = 0
        self.locked = False
        self.label.setText("請輸入主密碼")
        self.button.setEnabled(True)

# 色彩主題
class Theme(Enum):
    """ Color Themes """
    dark = "dark"
    light = "light"
    origin = "origin"

# 分頁
class Tab:
    """ Information of a Tab """
    def __init__(self, main_window: "MainWindow", text_edit: "CodeEditor", 
                 file_path: str|None = None, is_dirty: bool = False, is_crypt: bool = False, 
                 highlighter: QSyntaxHighlighter|None = None):
        self.main = main_window
        self.text_edit = text_edit
        self.file_path = file_path
        self.is_dirty = is_dirty
        self.is_crypt = is_crypt
        self.font_size = default_font_size
        self.highlighter = highlighter
        # 字型大小
        if default_font_size == 0: return
        elif default_font_size > 0: self.zoom_in(default_font_size)
        else: self.zoom_out(-default_font_size)
        self.default_font = self.text_edit.font()               # 預設字體
        self.default_point_size = self.default_font.pointSize() # 紀錄預設大小
        # 綁定事件
        self.text_edit.textChanged.connect(self._handle_text_change)

    @property
    def index(self) -> int:
        return self.main.tabs.indexOf(self.text_edit)

    def _handle_text_change(self):
        """ 處理文字變更事件 """
        if not self.is_dirty: 
            # 未儲存的變更
            self.is_dirty = True
            self.update_title()
        # 是不是目前的視窗 
        if self.index == self.main.tab_index:
            # 檢查 find && replace
            if self.main.is_finding: self.main.find_bar.update_search_results()
            if self.main.is_replacing: self.main.replace_bar.update_search_results()

    def zoom_in(self, size: int = 1):
        """ 放大字體 """
        self.font_size += size
        self.text_edit.zoomIn(size)
    
    def zoom_out(self, size: int = 1):
        """ 縮小字體 """
        self.font_size -= size
        self.text_edit.zoomOut(size)

    def reset_zoom(self):
        """ 還原預設字體大小 """
        self.font_size = default_font_size
        self.text_edit.setFont(self.default_font)

    def update_zoom(self):
        """ 同步字型大小 """
        self.reset_zoom()
        delta = default_font_size-self.font_size
        if delta == 0: return
        elif delta > 0: self.zoom_in(delta)
        else: self.zoom_out(-delta)

    def update_title(self):
        """ 更新title """
        base_title = os.path.basename(self.file_path) if self.file_path else "untitled"
        final_title = base_title + " •" if self.is_dirty else base_title
        self.main.tabs.setTabText(self.index, final_title)

# 尋找/取代
class FR_Bar(QWidget):
    """ Base of Find and Replace """
    def init(self, main_window: "MainWindow"):
        super().__init__(main_window)
        # 布局
        self.main = main_window
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(8, 4, 8, 4)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # 預設區分大小寫
        self.flags: QTextDocument.FindFlag 
        self.flags = QTextDocument.FindFlag(0)
        self.flags |= QTextDocument.FindFlag.FindCaseSensitively
        # 屬性
        self.match_count = 0       # 總匹配數
        self.match_index = 0       # 匹配索引 
        self.search_range: QTextCursor | None = None

    def init_find_bar(self):
        """ 尋找欄 """ 
        self.find_layout = QHBoxLayout()
        self.main_layout.addLayout(self.find_layout)
        # 輸入框/label
        self.find_label = QLabel(">")
        self.find_input = QLineEdit()              # 單行輸入框
        self.find_input.setPlaceholderText("尋找") # 輸入框提示
        self.find_input.setFixedWidth(180)         # 寬度
        # 查詢結果
        self.find_result = QLabel("-/-")
        self.find_result.setFixedWidth(50)
        # 按鈕
        self.next_button = QPushButton("👇") # 找下一個
        self.prev_button = QPushButton("👆") # 找上一個    
        self.case_button = QPushButton("Aa") # 大小寫需相符
        self.area_button = QPushButton("☰") # 範圍內尋找
        self.next_button.setFixedWidth(27)   # 設定按鈕寬度
        self.prev_button.setFixedWidth(27)   # 設定按鈕寬度
        self.case_button.setFixedWidth(32)   # 設定按鈕寬度
        self.area_button.setFixedWidth(27)   # 設定按鈕寬度
        self.next_button.clicked.connect(self.action_find_next) # 連接事件
        self.prev_button.clicked.connect(self.action_find_prev) # 連接事件
        self.case_button.clicked.connect(self.action_toggle_case_sensitive) # 連接事件
        self.area_button.clicked.connect(self.action_set_find_area) # 連接事件
        self.find_input.textChanged.connect(self.update_search_results)
        self.case_button.setStyleSheet("background-color: lightgreen;")
        # 排版
        self.find_layout.setContentsMargins(0, 0, 0, 0)
        self.find_layout.addWidget(self.find_label)
        self.find_layout.addWidget(self.find_input)
        self.find_layout.addWidget(self.find_result)
        self.find_layout.addWidget(self.prev_button)
        self.find_layout.addWidget(self.next_button)
        self.find_layout.addWidget(self.case_button)
        self.find_layout.addWidget(self.area_button)
        self.find_layout.addStretch(1)

    def init_replace_bar(self):
        """ 取代欄 """
        self.replace_layout = QHBoxLayout()
        self.main_layout.addLayout(self.replace_layout)
        # 輸入框
        self.replace_input = QLineEdit()              # 單行輸入框
        self.replace_input.setPlaceholderText("取代") # 輸入框提示
        self.replace_input.setFixedWidth(180)         # 寬度
        # 對齊用
        self.padding_label = QLabel("")
        self.padding_label.setFixedWidth(50)
        # 按鈕
        self.replace_one_button = QPushButton("取代")     # 取代
        self.replace_all_button = QPushButton("全部取代")  # 全部取代
        self.replace_one_button.setFixedWidth(42)         # 設定按鈕寬度
        self.replace_all_button.setFixedWidth(64)         # 設定按鈕寬度
        self.replace_one_button.clicked.connect(self.action_replace_one) # 連接事件
        self.replace_all_button.clicked.connect(self.action_replace_all) # 連接事件
        # 排版
        self.replace_layout.setContentsMargins(0, 0, 0, 0)
        self.replace_layout.addWidget(QLabel(">"))
        self.replace_layout.addWidget(self.replace_input)
        self.replace_layout.addWidget(self.padding_label)
        self.replace_layout.addWidget(self.replace_one_button)
        self.replace_layout.addWidget(self.replace_all_button)
        self.replace_layout.addStretch(1)

    def _disable_buttons(self, a0: bool = True):
        self.next_button.setDisabled(a0)
        self.prev_button.setDisabled(a0)
        try:
            self.replace_one_button.setDisabled(a0)
            self.replace_all_button.setDisabled(a0)
        except: pass

    def _update_match_count(self, text: str):
        """ 遍歷文件計算總匹配數 """
        self.match_count = 0
        doc = self.main.text_edit.document()
        
        # 範圍搜尋
        if self.search_range is not None:
            start_pos = self.search_range.selectionStart()
            end_pos = self.search_range.selectionEnd()
        # 全域搜尋
        else:
            cursor = self.main.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            start_pos = cursor.position()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            end_pos = cursor.position()
            del cursor
        
        # 不更改原始游標
        temp_cursor = QTextCursor(doc)
        temp_cursor.setPosition(start_pos)
        
        # 遍歷計數
        while True:
            found_cursor = doc.find(text, temp_cursor, self.flags)
            # 超出範圍就中斷
            if found_cursor.isNull() or found_cursor.selectionEnd() > end_pos: break
            # 計數+1並移動到下一個位置
            self.match_count += 1
            temp_cursor.setPosition(found_cursor.selectionEnd())

    def _current_match_index(self, text: str):
        """ 計算當前被選取匹配項是總數中的第幾個 """
        current_index = 0
        doc = self.main.text_edit.document()
        this_match_start = self.main.text_edit.textCursor().selectionStart()
        
        # 範圍搜尋
        if self.search_range is not None:
            start_pos = self.search_range.selectionStart()
            end_pos = self.search_range.selectionEnd()
        else:
            cursor = self.main.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            start_pos = cursor.position()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            end_pos = cursor.position()
            del cursor
            
        # 不更改原始游標
        temp_cursor = QTextCursor(doc)
        temp_cursor.setPosition(start_pos)
        
        # 遍歷計數
        while True:
            found_cursor = doc.find(text, temp_cursor, self.flags)
            # 超出範圍就中斷
            if found_cursor.isNull() or found_cursor.selectionEnd() > end_pos: break
            # 計數+1並移動到下一個位置
            current_index += 1
            temp_cursor.setPosition(found_cursor.selectionEnd())
            # 計數完成
            if this_match_start == found_cursor.selectionStart(): break
        return current_index

    def update_search_results(self):
        """ 變更時計算總數 """
        search_text = self.find_input.text()
        self.main.last_find_text = search_text
        # 沒有尋找關鍵字
        if not search_text:
            self.match_count = 0
            self.find_result.setText("-/-")
            self._disable_buttons(True)
            return
        # 計算總數
        self._update_match_count(search_text)
        if self.match_count == 0:
            text = "查無結果"
            self._disable_buttons(True)
        else:
            # 重新計算self.match_index
            self.match_index = self._current_match_index(search_text)
            text = f"{self.match_index}/{self.match_count}"
            self._disable_buttons(False)
        self.find_result.setText(text)

    def _action_find_base(self, flags: QTextDocument.FindFlag, surround_start: int):
        """ 尋找功能基底 """
        search_text = self.find_input.text()
        if (not search_text):
            self.find_result.setText("-/-")
            return
        self._update_match_count(search_text)
        if not self.match_count:
            self.find_result.setText("查無結果")
        
        # 向flags方向尋找
        is_forward_search = not bool(flags & QTextDocument.FindFlag.FindBackward)
        # 自動更新畫面的游標，並把文字反白
        found = self.main.text_edit.find(search_text, flags)

        # 範圍搜尋 (範圍內環繞)
        if self.search_range:
            start_pos = self.search_range.selectionStart()
            end_pos = self.search_range.selectionEnd()
            # 檢查是否需要環繞
            if found:
                match_cursor = self.main.text_edit.textCursor()
                # Case: 向前找超過範圍終點
                if is_forward_search and match_cursor.selectionEnd() > end_pos:
                    found = False
                # Case: 向後找超過範圍起點
                elif not is_forward_search and match_cursor.selectionStart() < start_pos:
                    found = False
            # 改變環繞起始位置
            surround_start = start_pos if is_forward_search else end_pos
        # 範圍內沒找到 -> 環繞
        if not found:
            # 重設游標位址
            cursor = self.main.text_edit.textCursor()
            cursor.setPosition(surround_start)
            self.main.text_edit.setTextCursor(cursor)
            # 再找一次
            found = self.main.text_edit.find(search_text, flags)
            
        # 聚焦mainwindow
        if found: self.main.focus_text_edit()
        # 重新計算self.match_index
        self.match_index = self._current_match_index(search_text)
        text = f"{self.match_index}/{self.match_count}" if self.match_count else "查無結果"
        self.find_result.setText(text)

    def action_toggle_case_sensitive(self):
        """ 區分大小寫 """
        # 視覺回饋(綠 -> 區分大小寫)
        if self.flags == QTextDocument.FindFlag(0):
            self.flags |= QTextDocument.FindFlag.FindCaseSensitively
            self.case_button.setStyleSheet("background-color: lightgreen;")
        else: 
            self.flags = QTextDocument.FindFlag(0)
            self.case_button.setStyleSheet("")
        self.update_search_results()

    def action_set_find_area(self): 
        """ 設定尋找範圍 """
        current_cursor = self.main.text_edit.textCursor()
        # 沒有選取文字
        if (not current_cursor.hasSelection()) or (self.search_range is not None):
            self.search_range = None
            self.area_button.setStyleSheet("")
        # 有選取文字
        else: 
            self.search_range = QTextCursor(current_cursor)
            self.area_button.setStyleSheet("background-color: lightgreen;")
        # 更新結果
        self.update_search_results()
        self.action_find_next()

    def action_find_next(self):
        """ 找下一個 """
        cursor = self.main.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self._action_find_base(self.flags, cursor.position())

    def action_find_prev(self):
        """ 找上一個 """
        flags = self.flags | QTextDocument.FindFlag.FindBackward # 向後尋找 
        cursor = self.main.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._action_find_base(flags, cursor.position())

    def action_replace_one(self):
        """ 取代 """
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        # 尋找欄為空則返回
        if not search_text: return
        # 確保有選擇的文字
        cursor = self.main.text_edit.textCursor()
        if not cursor.hasSelection(): 
            self.action_find_next()
            return
        # 替換文字
        origin_pos = cursor.position()
        cursor.insertText(replace_text)
        # 設定光標位置
        cursor.setPosition(origin_pos+len(replace_text))
        self.main.text_edit.setTextCursor(cursor)
        self.action_find_next()
        # dirty
        self.main.tab.is_dirty = True
        self.main.tab.update_title()

    def action_replace_all(self):
        """ 全部取代 """
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not search_text: return
        original_cursor = self.main.text_edit.textCursor()
        temp_cursor = QTextCursor(self.main.text_edit.document())
        
        # 範圍取代
        if self.search_range:
            range_cursor = QTextCursor(self.search_range)
            temp_cursor.setPosition(range_cursor.selectionStart())
            end_pos = range_cursor.selectionEnd() # 範圍終點
        # 整體取代
        else:
            temp_cursor.movePosition(QTextCursor.MoveOperation.Start)
            end_pos = -1
        # 迴圈遍歷
        replace_count = 0
        last_position = -1
        self.main.text_edit.setTextCursor(temp_cursor)
        while self.main.text_edit.find(search_text, self.flags):
            match_cursor = self.main.text_edit.textCursor()
            # 超出範圍->停止替換
            if self.search_range and match_cursor.selectionEnd() > end_pos: break 
            # 替換選取的文字
            match_cursor.insertText(replace_text)
            self.main.text_edit.setTextCursor(match_cursor)
            replace_count += 1
            last_position = match_cursor.position()

        # 恢復並更新
        self.main.text_edit.setTextCursor(original_cursor)
        if replace_count > 0:
            # 光標位置設定與反白
            final_cursor = self.main.text_edit.textCursor()
            final_cursor.setPosition(last_position)
            final_cursor.movePosition(
                QTextCursor.MoveOperation.Left, 
                QTextCursor.MoveMode.KeepAnchor, 
                len(replace_text)
            )
            final_cursor.setPosition(last_position)
            self.main.text_edit.setTextCursor(final_cursor)
            # dirty
            self.main.tab.is_dirty = True
            self.main.tab.update_title()

class FindBar(FR_Bar):
    """ Find function """
    def __init__(self, main_window: "MainWindow"):
        super().init(main_window)
        super().init_find_bar()
        self.main_layout.addStretch(1)

    def showEvent(self, event: QShowEvent) -> None:
        """ 顯示事件 """
        self.main.is_finding = True
        return super().showEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        """ 隱藏事件 """
        self.main.is_finding = False
        return super().hideEvent(event)

class ReplaceBar(FR_Bar):
    """ Replace function """
    def __init__(self, main_window: "MainWindow"):
        super().init(main_window)
        super().init_find_bar()
        super().init_replace_bar()
        self.main_layout.addStretch(1)

    def showEvent(self, event: QShowEvent) -> None:
        """ 顯示事件 """
        self.main.is_replacing = True
        return super().showEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        """ 隱藏事件 """
        self.main.is_replacing = False
        return super().hideEvent(event)

# 高亮器
class HighlighterMeta(type(QSyntaxHighlighter), ABCMeta): # pyright: ignore[reportGeneralTypeIssues]
    pass

class Highlighter(QSyntaxHighlighter, metaclass=HighlighterMeta):
    """ Base of all Highlighters """
    def __init__(self, parent_document: QTextDocument):
        super().__init__(parent_document)
        self.rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        # 初始化函數
        self.load_colors()
        self._empty_QTextCharFormat()
        self._setup_formats()
        self._setup_reg_exp()
        self._setup_rules()
    
    def load_colors(self):
        """ 載入顏色 """
        self.Blue = QColor("#0550ae")
        self.Gray = QColor("#6e7781")
        self.Brown = QColor("#D27067")
        self.Green = QColor("#65B872")
        self.yellow = QColor("#e6e63b")
        self.Dark_Blue = QColor("#AB4ECC")
        self.Green_Brown = QColor("#3A934A")
    
    @abstractmethod
    def _empty_QTextCharFormat(self): pass
    
    @abstractmethod
    def _setup_formats(self): pass
    
    @abstractmethod
    def _setup_reg_exp(self): pass
    
    @abstractmethod
    def _setup_rules(self): pass
    
    @abstractmethod
    def highlightBlock(self, text: str| None): pass

class PyHighlighter(Highlighter):
    """ Highlighter for Python """
    No_State = -1 # None
    State_Single_Double = 1    # " "
    State_Single_Single = 2    # ' '
    State_Triple_Double = 3 # """ """
    State_Triple_Single = 4 # ''' '''
    
    def __init__(self, parent_document: QTextDocument):
        self.line: list[None|QTextCharFormat]
        super().__init__(parent_document)
        self.setCurrentBlockState(self.No_State)

    def _format_line(self, Index, Length, Format, force = True):
        """ 顏色緩衝區 """
        for i in range(Index, Index+Length):
            if (self.line[i] is None) or (force):
                self.line[i] = Format

    def _close_quote(self, state: int, text: str, index: int) -> tuple[int, int]:
        "關閉引號"
        pattern = None
        # 三引號優先
        if state == self.State_Triple_Double:
            pattern = self.pattern_triple_double
        # 單引號次之
        elif state == self.State_Single_Double:
            pattern = self.pattern_single_double
        # 三引號優先
        if state == self.State_Triple_Single:
            pattern = self.pattern_triple_single
        # 單引號次之
        elif state == self.State_Single_Single:
            pattern = self.pattern_single_single
        # 處理pattern
        if pattern is None: raise
        
        match = pattern.match(text, index)
        new_index = match.capturedStart() if match.hasMatch() else -1
        
        # 這行也沒結束引號
        if new_index == -1:
            self._format_line(index, len(text)-index, self.format_string)
        # 把引號之前註解掉
        else: 
            state = self.No_State
            length = new_index + match.capturedLength() - index
            self._format_line(index, length, self.format_string)
            new_index += match.capturedLength()
        return (new_index, state)

    def _find_next_quote(self, index: int, text: str) -> tuple[int, int]: 
        """ 找到最近的引號以及其索引值 """
        exist = []
        # 計算索引
        m11 = self.pattern_single_single.match(text, index)
        m12 = self.pattern_single_double.match(text, index)
        m31 = self.pattern_triple_single.match(text, index)
        m32 = self.pattern_triple_double.match(text, index)
        
        i11 = m11.capturedStart() if m11.hasMatch() else -1
        i12 = m12.capturedStart() if m12.hasMatch() else -1
        i31 = m31.capturedStart() if m31.hasMatch() else -1
        i32 = m32.capturedStart() if m32.hasMatch() else -1
        
        # 加入非-1的
        for i in [i11, i12, i31, i32]:
            if i != -1:
                exist.append(i)
        # 找不到的情況
        if exist == []: return (-1, self.No_State)
        min_index = min(exist)
        # 單引號(三重優先)
        if min_index == i31:
            length, state = 3, self.State_Triple_Single
        elif min_index == i11:
            length, state = 1, self.State_Single_Single
        # 雙引號(三重優先)
        elif min_index == i32:
            length, state = 3, self.State_Triple_Double
        elif min_index == i12:
            length, state = 1, self.State_Single_Double
        # 不應發生: 找的到卻又不匹配
        else: raise RuntimeError(f"min_index doesn't match: {min_index} -> [{i11}, {i12}, {i31}, {i32}]")
        # 將起始引號上色並回傳
        self._format_line(min_index, length, self.format_string)
        return (min_index+length, state)

    def _empty_QTextCharFormat(self):
        """ 空的樣式 """
        self.format_keyword = QTextCharFormat()
        self.format_string = QTextCharFormat()
        self.format_comment = QTextCharFormat()
        self.format_number = QTextCharFormat()

    def _setup_formats(self):
        """ 設定樣式 """
        self.format_keyword.setForeground(self.Dark_Blue)
        self.format_string.setForeground(self.Brown)
        self.format_comment.setForeground(self.Green_Brown)
        self.format_number.setForeground(self.Green)

    def _setup_reg_exp(self):
        """ 設定正規表達式 """
        keywords = ["class", "def", "return", "pass", "lambda", "import", "from", 
                    "if", "elif", "else", "for", "while", "continue", "break", 
                    "True", "False", "None", "and", "or", "not","in", "is", 
                    "try", "except", "finally", "raise", "with", "as", 
                    "global", "yield", "del", "assert", "nonlocal"]
        # import keywords | keyword.kwlist
        keywords_str = r'\b(' + '|'.join(keywords) + r')\b'
        self.pattern_keywords = QRegularExpression(keywords_str)
        self.pattern_comment = QRegularExpression(r"#[^\n]*")
        self.pattern_number = QRegularExpression(r"\b[0-9]+\b")
        # 單個引號
        self.pattern_single_double = QRegularExpression(r"'")
        self.pattern_single_single = QRegularExpression(r'"')
        # 三重引號
        self.pattern_triple_double = QRegularExpression(r'"""')
        self.pattern_triple_single = QRegularExpression(r"'''")

    def _setup_rules(self):
        """ 設定規則 """
        self.rules.append((self.pattern_number, self.format_number))
        self.rules.append((self.pattern_keywords, self.format_keyword))

    def _update_highlightBlock(self):
        """ 把緩衝區的狀態同步到高亮狀態 """
        index = 0
        # 遍歷 self.line 緩衝區
        while index < len(self.line):
            # 略過 None
            if self.line[index] is None: 
                index += 1
                continue
            start = index
            current_format = self.line[index]
            # 向右吃相同區塊
            while True:
                index += 1
                if index >= len(self.line): break
                if self.line[index] != current_format: break
            # 區塊著色
            self.setFormat(start, index-start, current_format)

    def highlightBlock(self, text: str| None):
        """ 對每一行文字進行高亮處理 """
        if text is None: return
        state = self.previousBlockState()
        # 初始化顏色表
        qt_len = len(text.encode('utf-16-le')) // 2
        self.line = [None for _ in range(qt_len)]
        # 開始井號和引號的處理
        index = 0
        while index <= len(text):
            # 引號沒關優先關閉
            if state != self.No_State:
                index, state = self._close_quote(state, text, index)
                if index == -1: return
                continue
            # 引號有關閉找下一個
            quote_index, new_state = self._find_next_quote(index, text)
            
            m_comment = self.pattern_comment.match(text, index)
            comment_index = m_comment.capturedStart() if m_comment.hasMatch() else -1
            
            # 兩者皆無
            if quote_index == -1 and comment_index == -1:
                state = self.No_State
                break
            # 註解優先
            if quote_index == -1 or (comment_index < quote_index and comment_index != -1):
                self._format_line(comment_index, len(text)-comment_index, self.format_comment)
                state = self.No_State
                break
            # 字串優先
            else: # 情況: quote_index < comment_index 或 comment_index == -1
                state = new_state  
                index = quote_index
                continue
        # 上色一般項目
        for pattern, format in self.rules:
            # 初始化index
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                # 上色並往下找
                match = matches.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self._format_line(start, length, format, False)
        # 再度設定BlockState
        self.setCurrentBlockState(state)
        # 套用緩衝區設定
        self._update_highlightBlock()

class MdHighlighter(Highlighter):
    """ Highlighter for Markdown """
    No_State = -1         # None
    Code_Block_State = 1  # ```
    Inline_Code_State = 2 # `...`
    
    def __init__(self, parent_document: QTextDocument):
        self.full_line_rules: list[tuple[QRegularExpression, QTextCharFormat]]
        self.partial_rules: list[tuple[QRegularExpression, dict[int, QTextCharFormat]]]
        self.inline_rules: list[tuple[QRegularExpression, QTextCharFormat]]
        super().__init__(parent_document)
        self.setCurrentBlockState(self.No_State)

    def _empty_QTextCharFormat(self):
        """ 空的樣式 """
        self.format_bold = QTextCharFormat()
        self.format_italic = QTextCharFormat()
        self.format_bold_italic = QTextCharFormat()
        self.format_superscript = QTextCharFormat()
        self.format_subscript = QTextCharFormat()
        self.format_highlight = QTextCharFormat()
        self.format_header = QTextCharFormat()
        self.format_quote = QTextCharFormat()
        self.format_code_block = QTextCharFormat()
        self.format_separator = QTextCharFormat()
        self.format_string = QTextCharFormat()
        self.format_link = QTextCharFormat()
        self.format_strike_out = QTextCharFormat()
        self.format_inline_code = QTextCharFormat()

    def _setup_formats(self):
        """ 設定樣式 """
        Bold = QFont.Weight.Bold
        SubScript = QTextCharFormat.VerticalAlignment.AlignSubScript
        SuperScript = QTextCharFormat.VerticalAlignment.AlignSuperScript
        # 粗體
        self.format_bold.setFontWeight(Bold)
        # 斜體
        self.format_italic.setFontItalic(True)
        # 粗斜體
        self.format_bold_italic.setFontWeight(Bold)
        self.format_bold_italic.setFontItalic(True)
        # 上標
        self.format_superscript.setVerticalAlignment(SuperScript)
        # 下標
        self.format_subscript.setVerticalAlignment(SubScript)
        # 螢光筆
        self.format_highlight.setFontWeight(Bold)
        self.format_highlight.setForeground(self.yellow)
        # 標題/清單 (藍色+粗體)
        self.format_header.setFontWeight(Bold)
        self.format_header.setForeground(self.Blue)
        # 引用 (灰色)
        self.format_quote.setForeground(self.Gray)
        # 列表 (藍色+粗體)
        self.format_unordered = QTextCharFormat(self.format_header)
        self.format_ordered = QTextCharFormat(self.format_header)
        # 勾選清單
        self.format_unfinished = QTextCharFormat(self.format_header)
        self.format_finished = QTextCharFormat(self.format_header)
        # 程式碼
        self.format_code_block.setBackground(self.Gray)
        # 水平分隔線 (灰色+粗體)
        self.format_separator.setFontWeight(Bold)
        self.format_separator.setForeground(self.Gray)
        # 圖片 ![format_string](format_link)
        self.format_string.setForeground(self.Brown)
        # 連結
        self.format_link.setFontUnderline(True)
        # 刪除線
        self.format_strike_out.setFontStrikeOut(True)
        # 行內程式
        # self.format_inline_code

    def _setup_reg_exp(self):
        """ 設定正規表達式 """
        self.pattern_escape = QRegularExpression(r"\\([\\`*_{}\[\]()#+-.!|])")
        # 標頭
        self.pattern_header = QRegularExpression(r"^(#{1,6}\s+.*)")
        # 引用
        self.pattern_quote = QRegularExpression(r"^>\s+.*")
        # 列表
        self.pattern_unordered = QRegularExpression(r"^[\s]*[-\*\+]\s") # 無序
        self.pattern_ordered = QRegularExpression(r"^[\s]*\d+\.\s") # 有序
        # 勾選清單
        self.pattern_unfinished = QRegularExpression(r"^[\s]*[-*+]\s\[\s\]\s.*") # 未完成
        self.pattern_finished = QRegularExpression(r"^[\s]*[-*+]\s\[[xX]\]\s.*") # 已完成
        # 程式碼
        self.pattern_code_block = QRegularExpression(r"^(\s*)```")
        # 水平分隔線
        self.pattern_separator = QRegularExpression(r"^([-*_]){3,}$")
        # 圖片
        self.pattern_image = QRegularExpression(r"!\[([^\]]*)\]\(([^)]+)\)")
        
        # 粗體
        self.pattern_bold1 = QRegularExpression(r"(^|[^*])\*\*([^*]+)\*\*([^*]|$)")
        self.pattern_bold2 = QRegularExpression(r"(^|[^_])\_\_([^_]+)\_\_([^_]|$)")
        # 斜體
        self.pattern_italic1 = QRegularExpression(r"(^|[^*])\*([^*]+)\*([^*]|$)")
        self.pattern_italic2 = QRegularExpression(r"(^|[^_])\_([^_]+)\_([^_]|$)")
        # 粗斜體
        self.pattern_bold_italic1 = QRegularExpression(r"\*\*\*([^*]+)\*\*\*")
        self.pattern_bold_italic2 = QRegularExpression(r"\_\_\_([^_]+)\_\_\_")
        # 上標/下標
        self.pattern_subscript = QRegularExpression(r"~([^~]+)~")
        self.pattern_superscript = QRegularExpression(r"\^([^^]+)\^")
        # 刪除線
        self.pattern_strike_out = QRegularExpression(r"~~([^~]+)~~")
        # 螢光筆 (強調顯示)
        self.pattern_highlight = QRegularExpression(r"==([^=]+)==")
        # 行內程式
        self.pattern_inline_code = QRegularExpression(r"`([^`]+)`")
        # 超連結
        self.pattern_link = QRegularExpression(r"\[([^\]]+)\]\(([^)]+)\)")

    def _setup_rules(self):
        """ 設定規則 """
        # 整行高亮規則
        self.full_line_rules = [
            (self.pattern_quote, self.format_quote),
            (self.pattern_separator, self.format_separator)
        ]
        # 局部高亮規則
        self.partial_rules = [
            (self.pattern_header, {1: self.format_header}), 
            # 只對符號部分標色
            (self.pattern_unfinished, {1: self.format_unfinished}),
            (self.pattern_finished, {1: self.format_finished}),
            (self.pattern_unordered, {1: self.format_unordered}),
            (self.pattern_ordered, {1: self.format_ordered}),
            # 圖片與連結: 拆分內容與網址
            (self.pattern_image, {1: self.format_string, 2: self.format_link}),
            (self.pattern_link, {1: self.format_header, 2: self.format_link}),
        ]
        # 內聯疊加規則
        self.inline_rules = [
            (self.pattern_inline_code, self.format_inline_code),
            (self.pattern_highlight, self.format_highlight),
            (self.pattern_bold1, self.format_bold),
            (self.pattern_bold2, self.format_bold),
            (self.pattern_italic1, self.format_italic),
            (self.pattern_italic2, self.format_italic),
            (self.pattern_bold_italic1, self.format_bold_italic),
            (self.pattern_bold_italic2, self.format_bold_italic),
            (self.pattern_strike_out, self.format_strike_out),
            (self.pattern_subscript, self.format_subscript),
            (self.pattern_superscript, self.format_superscript),
        ]
    
    def is_escaped(self, index: int, text: str|None):
        """ 判斷是否應該跳脫 """
        if text is None: return False
        if index == -1: return False
        # 計算跳脫數
        count = 0
        new_index = index-1
        while new_index >= 0 and text[new_index] == "\\":
            count += 1
            new_index -= 1
        # 判斷
        return (count%2 == 1)
    
    def highlightBlock(self, text: str | None):
        """ 對每一行文字進行高亮處理 """
        if text is None: return
        # 程式碼區塊
        state = self.previousBlockState()
        # 使用 match() 檢查 Code_Block
        match_code = self.pattern_code_block.match(text)
        if match_code.hasMatch():
            # 偵測到Code_Block
            new_state = self.Code_Block_State if (state == self.No_State) else self.No_State
            self.setCurrentBlockState(new_state)
            self.setFormat(0, len(text), self.format_code_block)
            return
        if state == self.Code_Block_State:
            self.setCurrentBlockState(state)
            self.setFormat(0, len(text), self.format_code_block)
            return
        # Full Line Rules
        for pattern, _format in self.full_line_rules:
            match = pattern.match(text)
            if not match.hasMatch(): continue
            # 上色
            self.setFormat(0, len(text), _format) 
        # Partail Rules
        for pattern, group_dict in self.partial_rules:
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                # 往下找下一個匹配
                match = matches.next()
                index = match.capturedStart()
                # 跳脫字元
                if self.is_escaped(index, text) and match.hasMatch(): continue
                # 正常處理
                for group_idx, _format in group_dict.items():
                    start = match.capturedStart(group_idx)
                    length = match.capturedLength(group_idx)
                    if start != -1 and length > 0: self.setFormat(start, length, _format)
        # Inline Rules
        for pattern, _format in self.inline_rules:
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                # 往下找下一個匹配
                match = matches.next()
                index = match.capturedStart()
                # 跳脫
                if self.is_escaped(index, text) and match.hasMatch(): continue
                # 正常處理
                match_len = match.capturedLength()
                if match_len > 0:
                    # 建立新格式副本並合併 (Merge) 內聯樣式
                    new_format = QTextCharFormat(self.format(index))
                    new_format.merge(_format)
                    self.setFormat(index, match_len, new_format)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent: QWidget|None = None):
        """ 初始化CodeEditor """
        super().__init__(parent=parent)
        self.tab: str
        self.set_tab()
        self.brackets = {
            # 半形
            "(": ")", "[": "]", "{": "}", 
            "⟨": "⟩", "⟪": "⟫", 
            # 全形
            "（": "）", "［": "］", "｛": "｝", 
            "〈": "〉", "《": "》", "〔": "〕", 
            "【": "】", "〖": "〗", 
            "「": "」", "『": "』", 
        }
        self.cursor_move_left = QTextCursor.MoveOperation.Left
        self.cursor_move_right = QTextCursor.MoveOperation.Right
        self.cursor_movemode_move = QTextCursor.MoveMode.MoveAnchor
        self.cursor_movemode_keep = QTextCursor.MoveMode.KeepAnchor

    def _handle_left_bracket(self, cursor: QTextCursor, left_char: str):
        """ 處理左括號 """
        self.insertPlainText(self.brackets[left_char])
        cursor.movePosition(self.cursor_move_left, self.cursor_movemode_move, 1)

    def _handle_right_bracket(self, cursor: QTextCursor):
        """ 處理右括號 回傳是否插入該字元 """
        cursor.clearSelection()
        # 左右檢查
        cursor.movePosition(self.cursor_move_left, self.cursor_movemode_keep, 1)
        left_char = cursor.selectedText()
        cursor.movePosition(self.cursor_move_right, self.cursor_movemode_keep, 2)
        right_char = cursor.selectedText()
        cursor.clearSelection()
        # 避免多餘的右括號
        insert_char = True
        if (left_char in self.brackets.keys()):
            if (right_char == self.brackets[left_char]):
                cursor.movePosition(self.cursor_move_right, self.cursor_movemode_move, 1)
                insert_char = False
        self.setTextCursor(cursor)
        return insert_char
    
    def set_tab(self, replace: str = "  ") -> None:
        """ 設定輸入tab時插入的字元 """
        self.tab = replace

    def keyPressEvent(self, e: QKeyEvent|None) -> None:
        """ 特殊按鍵 """
        if e is None: return
        cursor = self.textCursor()
        set_cursor = False
        # 處理tab
        if e.key() == Qt.Key.Key_Tab:
            self.insertPlainText(self.tab)
        # 處理backspace
        elif e.key() == Qt.Key.Key_Backspace:
            # 避免游標在最前面
            if cursor.position() == 0:
                return super().keyPressEvent(e)
            # 檢查前一個
            cursor.movePosition(self.cursor_move_left, self.cursor_movemode_keep, 1)
            left_char = cursor.selectedText()
            # 不是括號
            if not (left_char in self.brackets):
                return super().keyPressEvent(e)
            # 是括號
            cursor.movePosition(self.cursor_move_right, self.cursor_movemode_move, 1)
            cursor.movePosition(self.cursor_move_right, self.cursor_movemode_keep, 1)
            right_char = cursor.selectedText()
            # 去除右括號
            if (self.brackets[left_char] == right_char):
                cursor.removeSelectedText()
            super().keyPressEvent(e)
            set_cursor = True
        # 處理左括號
        elif e.text() in self.brackets.keys():
            super().keyPressEvent(e)
            self._handle_left_bracket(cursor, e.text())
            set_cursor = True
        # 處理右括號
        elif e.text() in self.brackets.values():
            if self._handle_right_bracket(cursor):
                super().keyPressEvent(e)
                set_cursor = True
        else: super().keyPressEvent(e)
        # 套用 cursor
        if set_cursor: self.setTextCursor(cursor)

    def inputMethodEvent(self, a0: QInputMethodEvent | None) -> None:
        """ 一般輸入 """
        if a0 is None: return
        text = a0.commitString()
        cursor = self.textCursor()
        set_cursor = False
        # 處理左括號
        if text in self.brackets.keys():
            # 自動補全
            super().inputMethodEvent(a0)
            self._handle_left_bracket(cursor, text)
            set_cursor = True
        # 處理右括號
        elif text in self.brackets.values():
            if self._handle_right_bracket(cursor):
                super().inputMethodEvent(a0)
                set_cursor = True
        else: super().inputMethodEvent(a0)
        # 套用 cursor
        if set_cursor: self.setTextCursor(cursor)

# 主視窗
class MainWindow(QMainWindow):
    """ Main window of this application """
    def __init__(self, file_to_open: str|None = None):
        """ 初始化mainwindow """
        super().__init__()
        # 建立視窗
        self.setWindowTitle("yoCrypt Editor")
        self.resize(800, 600)
        self.password: bytearray = bytearray() # 密碼
        self.tab_index: int = 0
        self.theme: Theme = Theme.dark     # 預設色彩主題(深色)
        self.last_find_text = ""           # 上次的搜尋關鍵字
        self.last_replace_text = ""        # 上次的取代關鍵字
        self.is_finding: bool = False
        self.is_replacing: bool = False
        # 初始化介面
        self.init_ui()
        self._set_theme()
        self.tab.reset_zoom()
        self.focus_text_edit()
        self.action_disable_line_wrap() # 這不是bug
        self.action_enable_line_wrap()  # 這不是bug
        # 支援直接開啟檔案
        if not self._handle_external_file(file_to_open if file_to_open else welcome_file):
            self._handle_external_file(welcome_file)

    def init_Tab_list(self):
        """ 初始化 self.tab_list(含text_edit) """
        text_edit = CodeEditor(self) # 文字框建立
        temp_Tab = Tab(
            self, 
            text_edit=text_edit, 
            file_path=None, 
            is_dirty=False, 
            is_crypt=False
        )
        self.tab_list: list[Tab] = [temp_Tab]

    def init_menubar(self):
        """ 初始化 self.menubar """
        self.menubar = self.menuBar()
        if self.menubar is None: raise TypeError("menubar is None")
        # 在 menubar 中加入欄位
        self.file_menu = self.menubar.addMenu("File")
        self.edit_menu = self.menubar.addMenu("Edit")
        self.view_menu = self.menubar.addMenu("View")
        if self.file_menu is None: raise TypeError("file_menu is None")
        if self.edit_menu is None: raise TypeError("edit_menu is None")
        if self.view_menu is None: raise TypeError("view_menu is None")

    def init_QTabWidget(self):
        """ 初始化 self.tabs """
        self.tabs = QTabWidget()                                # 分頁欄建立
        self.tabs.setTabsClosable(True)                         # 可以關閉
        self.tabs.addTab(self.text_edit, "")                    # 加入第一個分頁

        self.tabs.currentChanged.connect(self._handle_tab_change)   # 切換分頁事件
        self.tabs.tabCloseRequested.connect(self._handle_tab_close) # 關閉分頁事件
        self.tabs.setMovable(True)                                  # 可以拖曳
        self.tabs.tabBar().tabMoved.connect(self._handel_tabMoved)
        
    def init_FR_dock(self):
        """ 初始化 find && replace 相關設定 """
        self.FR_dock = QDockWidget("尋找/取代", self)  # 浮動視窗
        self.FR_dock.setObjectName("FindReplaceDock") # 設定名稱
        
        self.find_bar = FindBar(self)       # 尋找工具
        self.replace_bar = ReplaceBar(self) # 取代工具
        self.FR_switcher = QWidget()  # (尋找/取代)widget

        self.switcher_layout = QHBoxLayout(self.FR_switcher) # 水平布局
        self.switcher_layout.setContentsMargins(0, 0, 0, 0)  # 消除留白
        self.switcher_layout.addStretch(1)                   # 向右推
        self.switcher_layout.addWidget(self.find_bar)        # 加入find
        self.switcher_layout.addWidget(self.replace_bar)     # 加入replace

        self.find_bar.hide()    # 預設隱藏
        self.replace_bar.hide() # 預設隱藏

        self.FR_dock.setWidget(self.FR_switcher)      # 設定widget
        self.FR_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |    # type: ignore 允許關閉 
            QDockWidget.DockWidgetFeature.DockWidgetMovable |     # type: ignore 允許移動
            QDockWidget.DockWidgetFeature.DockWidgetFloatable     # type: ignore 允許拖曳成獨立視窗
        )
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.FR_dock) # 停在上方
        # 預設大小
        self.FR_switcher.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.FR_dock.setFloating(True) # 預設浮動
        self.FR_dock.hide()            # 隱藏

    def _add_action_to_menu(
        self, 
        action_name: str, 
        label: str, 
        slot: object, 
        shortcut: ShortcutType|None, 
        menu: QMenu
    ) -> QAction: 
        """ 將指定QAction加入指定的Qmenu(可設立捷徑) """
        action = QAction(label, self)
        # new_action = QAction("New", self)
        setattr(self, action_name, action)
        # new_action.triggered.connect(self.action_new)
        action.triggered.connect(slot)
        # new_action.setShortcut("Ctrl+T")
        if shortcut is not None: 
            if isinstance(shortcut, collections.abc.Sequence) and not isinstance(shortcut, (str, QKeySequence)):
                action.setShortcuts(shortcut)
            else: action.setShortcut(shortcut)
        # self.file_menu.addAction(new_action)
        menu.addAction(action)
        return action

    def init_ui(self):
        """ 初始化ui """
        self.zoom_in_action: QAction
        self.init_Tab_list()
        self.init_menubar()
        self.init_QTabWidget()
        self.init_FR_dock()
        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # --- Signal & Slot ---
        # file_menu
        self._add_action_to_menu(
            "change_password_action", 
            "Change Master Password", 
            self.change_master_password, 
            None, 
            self.file_menu
        )
        self.file_menu.addSeparator()
        self._add_action_to_menu(
            "new_action", 
            "New", 
            self.action_new, 
            "Ctrl+T", 
            self.file_menu
        )
        self._add_action_to_menu(
            "open_action", 
            "Open", 
            self.action_open, 
            "Ctrl+O", 
            self.file_menu
        )
        self._add_action_to_menu(
            "open_crypted_action", 
            "Open Crypted", 
            self.action_open_crypted, 
            "Ctrl+Shift+O", 
            self.file_menu
        )
        self.file_menu.addSeparator()
        self._add_action_to_menu(
            "save_action", 
            "Save", 
            self.action_save, 
            None, 
            self.file_menu
        )
        self._add_action_to_menu(
            "save_crypted_action", 
            "Save Crypted", 
            self.action_save_crypted, 
            None, 
            self.file_menu
        )
        self._add_action_to_menu(
            "save_as_action", 
            "Save as", 
            self.action_save_as, 
            None, 
            self.file_menu
        )
        self._add_action_to_menu(
            "save_as_crypted_action", 
            "Save as Crypted", 
            self.action_save_as_crypted, 
            None, 
            self.file_menu
        )
        self._add_action_to_menu(
            "auto_save_action", 
            "Auto Save", 
            self.action_auto_save, 
            "Ctrl+S", 
            self.file_menu
        )
        self.file_menu.addSeparator()
        self._add_action_to_menu(
            "close_tab_action", 
            "Close Current Tab", 
            self.action_close_tab, 
            "Ctrl+W", 
            self.file_menu
        )
        
        # edit_menu
        self._add_action_to_menu(
            "find_action", 
            "Find", 
            self.action_find, 
            "Ctrl+F", 
            self.edit_menu
        )
        self._add_action_to_menu(
            "replace_action", 
            "Replace", 
            self.action_replace, 
            "Ctrl+H", 
            self.edit_menu
        )
        self.edit_menu.addSeparator()
        self._add_action_to_menu(
            "auto_highlight_action", 
            "Auto Highlight", 
            self.action_auto_highlight, 
            None, 
            self.edit_menu
        )
        self._add_action_to_menu(
            "disable_highlight_action", 
            "Disable Highlight", 
            self.action_disable_highlight, 
            None, 
            self.edit_menu
        )
        self._add_action_to_menu(
            "highlight_as_python_action", 
            "Highlight as Python", 
            self.action_highlight_as_python, 
            None, 
            self.edit_menu
        )
        self._add_action_to_menu(
            "highlight_as_markdown_action", 
            "Highlight as Markdown", 
            self.action_highlight_as_markdown, 
            None, 
            self.edit_menu
        )

        # view_menu
        self._add_action_to_menu(
            "set_theme_dark_action", 
            "Toggle To Dark Theme", 
            self.action_set_theme_dark, 
            None, 
            self.view_menu
        )
        self._add_action_to_menu(
            "set_theme_light_action", 
            "Toggle To Light Theme", 
            self.action_set_theme_light, 
            None, 
            self.view_menu
        )
        self._add_action_to_menu(
            "set_theme_origin_action", 
            "Toggle To Original Theme", 
            self.action_set_theme_origin, 
            None, 
            self.view_menu
        )
        self.view_menu.addSeparator()
        self._add_action_to_menu(
            "zoom_in_action", 
            "Zoom In", 
            self.action_zoom_in, 
            None, 
            self.view_menu
        )
        self._add_action_to_menu(
            "zoom_out_action", 
            "Zoom Out", 
            self.action_zoom_out, 
            "Ctrl+-", 
            self.view_menu
        )
        self._add_action_to_menu(
            "reset_zoom_action", 
            "Reset Zoom", 
            self.action_reset_zoom, 
            None, 
            self.view_menu
        )
        self.view_menu.addSeparator()
        self._add_action_to_menu(
            "enable_line_wrap_action", 
            "Enable Word Wrap", 
            self.action_enable_line_wrap, 
            None, 
            self.view_menu
        )
        self._add_action_to_menu(
            "disable_line_wrap_action", 
            "Disable Word Wrap", 
            self.action_disable_line_wrap, 
            None, 
            self.view_menu
        )

        # 特殊快捷鍵
        self.zoom_in_action.setShortcuts([
            QKeySequence(int(Qt.Modifier.CTRL.value)|int(Qt.Key.Key_Plus.value)), 
            QKeySequence("Ctrl+=")
        ])
        self.next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        self.next_tab_shortcut.activated.connect(self.switch_next_tab)

    @property
    def tab(self) -> Tab:
        return self.tab_list[self.tab_index]
    @tab.setter
    def tab(self, val: Tab):
        self.tab_list[self.tab_index] = val

    @property
    def text_edit(self) -> CodeEditor:
        return self.tab.text_edit
    @text_edit.setter
    def text_edit(self, val: CodeEditor):
        self.tab.text_edit = val
    
    @property
    def file_path(self) -> str | None:
        return self.tab.file_path
    @file_path.setter
    def file_path(self, val: str | None):
        self.tab.file_path = val

    @property
    def highlighter(self) -> QSyntaxHighlighter | None:
        return self.tab.highlighter
    @highlighter.setter
    def highlighter(self, val: QSyntaxHighlighter | None):
        self.tab.highlighter = val

    def focus_text_edit(self):
        """ active """
        self.text_edit.activateWindow()
        self.text_edit.setFocus()

    def _ensure_password(self) -> bool:
        """ 檢查密碼是否存在 若不存在則彈出輸入框 """
        if not os.path.exists(password_file):
            QMessageBox.warning(self, "錯誤", "password.txt不存在")
            return False
        # 密碼已存在
        while (not self.password):
            login = PasswordPrompt()
            if (login.exec() != QDialog.DialogCode.Accepted) or (not login.success): return False
            self.password = login.password
        return True
    
    def _handle_tab_change(self, index: int):
        """ 處理分頁切換事件 """
        self.tab_index = index
        # 避免FR出錯
        if self.is_finding: self.find_bar.update_search_results()
        if self.is_replacing: self.replace_bar.update_search_results()

    def _handle_tab_close(self, index: int):
        """ 處理分頁關閉事件 """
        old_index = self.tab_index
        # 更新分頁索引值
        self.tab_index = index
        self.tabs.setCurrentIndex(index)
        # 確保不會誤刪檔案
        if not self._dirty_warning_success():
            # 取消關閉
            self.tab_index = old_index
            self.tabs.setCurrentIndex(old_index)
            return
        self.tabs.removeTab(index)
        self.tab_list.pop(index)
        # 更新 tab_index
        self.tab_index = self.tabs.currentIndex()
        # 至少留一個分頁
        if self.tabs.count() == 0: self.action_new()
        # 避免FR出錯
        if self.is_finding: self.find_bar.update_search_results()
        if self.is_replacing: self.replace_bar.update_search_results()
        self.focus_text_edit()

    def _handel_tabMoved(self, from_: int, to: int):
        """ 拖曳分頁 """
        moved_tab = self.tab_list.pop(from_)
        # 同步更新列表位置
        self.tab_list.insert(to, moved_tab)
        self.tab_index = self.tabs.currentIndex()
        moved_tab.update_title()

    def _dirty_warning_success(self) -> bool:
        """ 當檔案未儲存且會遺失時 詢問使用者是否要儲存(True代表不用cancel) """
        empty_file = (self.file_path is None) and (not self.text_edit.toPlainText())
        if (not self.tab.is_dirty) or empty_file: return True
        file_path = "untitled" if (self.file_path is None) else self.file_path
        # 詢問使用者
        reply = QMessageBox.question(self, "儲存變更",
            "檔案 ["+file_path+"] 尚未儲存，是否要儲存變更？",
            # 提供 Yes, No, Cancel 三個選項
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel # 預設選中 Cancel 避免誤觸
        )
        if reply == QMessageBox.StandardButton.No: return True
        elif reply == QMessageBox.StandardButton.Yes: return self._auto_save()
        elif reply == QMessageBox.StandardButton.Cancel: return False
        else: raise ValueError(f"unexpected QMessageBox reply: {reply}")

    def _clear_master_password(self):
        """ 主密碼清理 """
        secure_clear(self.password)
        self.password = bytearray()

    def _auto_highlight(self, file_path: str):
        """ 自動套用高亮器 """
        extension = str(os.path.splitext(file_path)[1])
        doc = self.text_edit.document()
        if doc is None: raise RuntimeError("self.text_edit.document() is None")
        # Python
        if extension in [".py", ".ipynb"]: self.highlighter = PyHighlighter(doc)
        # Markdown
        elif extension in [".md"]: self.highlighter = MdHighlighter(doc)
        # 以上皆非
        else: self.highlighter = None

    def _read_file_from(self, file_path: str, hint: str, decrypt: bool = False) -> bool:
        """ 讀取指定位置的檔案 回傳是否成功 """
        file_name = os.path.basename(file_path)
        # 內部函數
        def msg(): self.statusBar().showMessage(f"已{hint}: {file_name}", 5000) # pyright: ignore[reportOptionalMemberAccess]
        # 嘗試多種編碼讀取
        encrypted_data = None
        encodings_to_try = ["utf-8", "gbk", "cp950", "latin-1"]
        for encoding in encodings_to_try:
            try:
                file = open(file_path, "r", encoding=encoding)
                encrypted_data = file.read()
                file.close()
                break
            except UnicodeDecodeError: continue
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"讀取檔案 {file_name} 失敗: {e}")
                return False # 讀取失敗
        if encrypted_data is None:
            QMessageBox.critical(self, "編碼錯誤", f"無法識別檔案 {file_name} 的編碼格式，開啟失敗。")
            return False
        # 解密/顯示/提示
        try: 
            # Tab
            plain_text = yoAES.decrypt(encrypted_data, self.password) if decrypt else encrypted_data
            self.text_edit.setPlainText(plain_text)
            # 高亮
            self._auto_highlight(file_path)
            # 提示
            self.statusBar().clearMessage() # pyright: ignore[reportOptionalMemberAccess]
            QTimer.singleShot(50, msg)
            self.file_path = file_path
            self.tab.is_crypt = decrypt
            # 強制更新is_dirty
            QApplication.processEvents()
            self.tab.is_dirty = False
            self.tab.update_title()
            self.tab.update_zoom()
            self.focus_text_edit()
            return True
        except Exception as e: 
            QMessageBox.critical(self, "解密錯誤", f"解密檔案 {file_name} 失敗: {e}")
            self.text_edit.clear()
            return False

    def _handle_external_file(self, file_path: str) -> bool:
        """ 處理從外部傳入的檔案路徑 """
        if not self._read_file_from(file_path, "開啟檔案", False):
            self.tab.update_title()
            return False
        return True

    def action_new(self):
        """ 新增一個分頁(檔案) """
        new_index = self.tabs.count()
        # 新分頁
        text_edit = CodeEditor(self)
        new_tab = Tab(self, text_edit=text_edit, file_path=None, is_dirty=True, is_crypt=False)
        self.tab_list.append(new_tab)
        # 切分頁
        self.tabs.addTab(text_edit, "")
        self.tabs.setCurrentIndex(new_index)
        self.tab_index = new_index
        self.tab.update_title()
        self.tab.reset_zoom()

    def _open_file(self, hint: str, decrypt: bool) -> bool:
        """ 選擇並開啟檔案 """
        options = QFileDialog.Option(0)
        # 取得路徑
        file_path, _ = QFileDialog.getOpenFileName(self, hint, "", "All Files (*)", options=options)
        if not file_path: return False # 取消
        # 開啟檔案
        self.action_new()
        success = self._read_file_from(file_path, hint, decrypt)
        if not success: self._handle_tab_close(self.tab_index)
        return success

    def action_open(self): 
        """ 開啟普通檔案 """
        self._open_file("開啟普通檔案", decrypt=False)

    def action_open_crypted(self):
        """ 開啟加密檔案 """
        if not self._ensure_password(): return
        self._open_file("開啟加密檔案",  decrypt=True)

    def _save_file(self, file_path: str, hint: str, encrypt: bool) -> bool:
        """ 儲存至file_path """
        file_name = os.path.basename(file_path)
        # 內部函數
        def msg(): 
            """ 更新statusBar """
            self.statusBar().showMessage(f"已{hint}: {file_name}", 4000) # pyright: ignore[reportOptionalMemberAccess]
        # 讀取輸入框
        try:
            plain_text = self.text_edit.toPlainText()
            write_data = yoAES.encrypt(plain_text, self.password) if encrypt else plain_text
            # 寫檔
            file = open(file_path, "w", encoding="utf-8")
            file.write(write_data)
            file.close()
            # 提示
            self.statusBar().clearMessage() # pyright: ignore[reportOptionalMemberAccess]
            QTimer.singleShot(50, msg)
            self.tab.is_dirty = False
            self.tab.update_title()
            self.tab.is_crypt = encrypt
            return True
        # 儲存失敗
        except Exception as e: QMessageBox.critical(self, "錯誤", f"儲存{os.path.basename(file_path)}失敗: {e}")
        return False

    def action_save(self):
        """ 儲存普通檔案 """
        if self.file_path is None: return self.action_save_as()
        self._save_file(self.file_path, hint="儲存普通檔案", encrypt=False)

    def action_save_as(self):
        """ 另存普通檔案 """
        options = QFileDialog.Option(0)
        # 取得位址
        file_path, _ = QFileDialog.getSaveFileName(self, "另存普通檔案", "", "All Files (*)", options=options)
        if not file_path: return  # 使用者按取消
        self.file_path = file_path
        # 儲存
        self._save_file(self.file_path, hint="另存普通檔案", encrypt=False)

    def action_save_crypted(self):
        """ 儲存加密檔案 """
        if not self._ensure_password(): return
        # 尚未設定檔案位址
        if self.file_path is None: return self.action_save_as_crypted()
        # 已設定位址
        self._save_file(self.file_path, hint="儲存加密檔案", encrypt=True)

    def action_save_as_crypted(self):
        """ 另存加密檔案 """
        if not self._ensure_password(): return
        hint = "另存加密檔案"
        # 取得位址
        options = QFileDialog.Option(0)
        file_path, _ = QFileDialog.getSaveFileName(self, hint, "", "All Files (*)", options=options)
        if not file_path: return  # 使用者按取消
        self.file_path = file_path
        # 加密儲存
        self._save_file(file_path, hint=hint, encrypt=True)

    def _auto_save(self) -> bool:
        """ 自動判斷並儲存-有回傳值 """
        if self.tab.is_crypt: 
            if not self._ensure_password(): return False
            # 同action_save_as_crypted
            if (self.file_path is None):
                hint = "另存加密檔案"
                options = QFileDialog.Option(0)
                file_path, _ = QFileDialog.getSaveFileName(self, "另存加密檔案", "", "All Files (*)", options=options)
                if not file_path: return False # 使用者按取消
            # 同action_save_crypted
            else:
                hint="儲存加密檔案"
                file_path = self.file_path
            if self._save_file(file_path, hint=hint, encrypt=True):
                self.file_path = file_path
                return True
            return False
        # 同action_save
        if (self.file_path is not None):
            return self._save_file(self.file_path, hint="儲存普通檔案", encrypt=False)
        # 同action_save_as
        options = QFileDialog.Option(0)
        file_path, _ = QFileDialog.getSaveFileName(self, "另存普通檔案", "", "All Files (*)", options=options)
        if not file_path: return False # 使用者按取消
        self.file_path = file_path
        return self._save_file(self.file_path, hint="另存普通檔案", encrypt=False)
    
    def action_auto_save(self):
        """ 自動判斷並儲存-沒回傳值 """
        self._auto_save()

    def change_master_password(self):
        """ 更改主密碼 """
        if not self._ensure_password(): return
        if not self._dirty_warning_success(): return
        new_password_bytearray = None
        # 內部函數
        def _ask_for_continue_change_password(hint: str) -> bool:
            """ 詢問使用者是否繼續更改主密碼 """
            reply = QMessageBox.question(
                self,
                "檔案加密失敗",
                hint, 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No: # 停止整個更改流程
                QMessageBox.information(self, "取消", "主密碼更改已取消")
                return True
            return False

        # 舊密碼輸入與驗證
        dialog = QInputDialog(self)
        dialog.setWindowTitle("更改主密碼")
        dialog.setLabelText("請輸入舊密碼:")
        dialog.setTextEchoMode(QLineEdit.EchoMode.Password)
        if not dialog.exec(): return # cancel
        
        old_password_str = dialog.textValue() # 暫存為 str
        _clear_dialog_input(dialog) # 立即清除 UI 輸入
        
        if not old_password_str:
            QMessageBox.warning(self, "錯誤", "密碼不能為空")
            return
            
        # 將 str 轉換為 bytearray 供驗證使用
        old_password_for_verification = bytearray(old_password_str, encoding)
        del old_password_str # 立即清除原始的 str 副本
        
        # 驗證
        with open(os.path.join(filedirname, "password.txt"), "r", encoding="utf-8") as f:
            stored_hash = f.read().strip()
        if not verify_password(old_password_for_verification, stored_hash):
            # 驗證失敗 清除 bytearray 引用
            secure_clear(old_password_for_verification)
            del old_password_for_verification 
            QMessageBox.warning(self, "錯誤", "舊密碼錯誤！")
            return
        # 驗證成功 清除 bytearray 引用
        secure_clear(old_password_for_verification)
        del old_password_for_verification 
        
        # 新密碼輸入與確認
        new_password_str = ""
        confirm_password_str = ""
        while True:
            # 輸入新密碼
            dialog = QInputDialog(self)
            dialog.setWindowTitle("更改主密碼")
            dialog.setLabelText("請輸入新密碼: ")
            dialog.setTextEchoMode(QLineEdit.EchoMode.Password)
            if not dialog.exec(): return # cancel
            new_password_str = dialog.textValue()
            _clear_dialog_input(dialog) # 清除 UI 輸入
            new_password_bytearray = bytearray(new_password_str, encoding)
            
            # 確認新密碼
            dialog = QInputDialog(self)
            dialog.setWindowTitle("更改主密碼")
            dialog.setLabelText("請確認新密碼:")
            dialog.setTextEchoMode(QLineEdit.EchoMode.Password)
            if not dialog.exec(): return # cancel
            confirm_password_str = dialog.textValue()
            _clear_dialog_input(dialog) # 清除 UI 輸入
            confirm_password_bytearray = bytearray(confirm_password_str, encoding)

            del new_password_str, confirm_password_str
            
            # 驗證與錯誤處理
            if not new_password_bytearray or not confirm_password_bytearray: 
                QMessageBox.warning(self, "錯誤", "密碼不能為空")
                continue
            if new_password_bytearray != confirm_password_bytearray:
                QMessageBox.warning(self, "錯誤", "兩次輸入的密碼不一致")
                continue
            break
        
        # 密碼清除
        secure_clear(confirm_password_bytearray)
        del confirm_password_bytearray
        
        decrypted_contents: dict[str, str] = {}
        error_occurred = False

        # 嘗試解密 Files 內所有 txt 檔案
        for fname in os.listdir(os.path.join(filedirname, "Files")):
            # 略過非 txt 跟 password
            if fname == "password.txt" or not fname.endswith(".txt"):  continue
            fpath = os.path.join(filedirname, "Files", fname)
            # 解密
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    encrypted_data = f.read()
                decrypted_text = yoAES.decrypt(encrypted_data, self.password)
                decrypted_contents[fpath] = decrypted_text
            except Exception as e:
                # 問使用者是否繼續
                hint = f"檔案 {fpath} 解密失敗: {e}\n是否繼續更新剩下的檔案? \n注意: 更新後 {fpath} 將無法讀取"
                if _ask_for_continue_change_password(hint): 
                    error_occurred = True
                    break

        # 嘗試加密儲存
        if not decrypted_contents: return
        for fpath, decrypted_text in decrypted_contents.items():
            try: 
                new_encrypted = yoAES.encrypt(decrypted_text, new_password_bytearray)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_encrypted)
            except Exception as e:
                hint = f"檔案 {fpath} 重新加密失敗: {e}\n是否繼續更新剩下的檔案? \n注意: 更新後 {fpath} 將無法讀取"
                if _ask_for_continue_change_password(hint): 
                    error_occurred = True
                    break
        
        # 復原程序 
        if error_occurred:
            QMessageBox.warning(self, "復原", "正在嘗試使用舊密碼還原檔案...")
            for fpath, decrypted_text in decrypted_contents.items():
                # 用舊密碼加密回去
                try:
                    rollback_encrypted = yoAES.encrypt(decrypted_text, self.password)
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(rollback_encrypted)
                # 連還原都失敗
                except Exception as rollback_e:
                    QMessageBox.critical(self, "嚴重錯誤", f"無法還原檔案 {fpath}，請手動檢查備份！")
        
        # 清除明文
        decrypted_text = ""
        decrypted_contents.clear()
        del decrypted_contents, decrypted_text
        if error_occurred: 
            # 錯誤發生時 也確保所有密碼被清除
            secure_clear(new_password_bytearray)
            del new_password_bytearray
            return

        # 更新密碼與清理
        self._clear_master_password() 
        self.password = new_password_bytearray
        with open(os.path.join(filedirname, "password.txt"), "w", encoding="utf-8") as f:
            f.write(hash_password(new_password_bytearray))
        del new_password_bytearray
        
        QMessageBox.information(self, "完成", "主密碼已更新 所有txt已重新加密")

    def action_zoom_in(self):
        """ 字體放大 """
        self.tab.zoom_in(1)

    def action_zoom_out(self):
        """ 字體縮小 """
        self.text_edit.zoomOut(1)
    
    def action_reset_zoom(self):
        """ 還原預設字體大小 """
        self.tab.reset_zoom()

    def _set_FR_pos(self):
        """ 動態計算 尋找/取代框 的位置 """
        self.FR_dock.show()
        self.FR_dock.adjustSize()
        main_window_rect = self.geometry()
        main_width = main_window_rect.width()
        main_x, main_y = main_window_rect.x(), main_window_rect.y()

        dock_width = self.FR_dock.width()
        x, y = (main_x+main_width)-(dock_width+10), main_y+54
        self.FR_dock.move(x, y)

    def action_find(self):
        """ 尋找 """
        self.FR_dock.hide()
        self.find_bar.show()
        self.replace_bar.hide()
        cursor = self.text_edit.textCursor()
        # 優先尋找反白的部分
        if cursor.hasSelection():
            text = cursor.selection().toPlainText()
            self.find_bar.find_input.setText(text)
            self.find_bar.find_input.selectAll()
            self.find_bar.action_find_next()
        # 顯示上次搜尋的關鍵字
        elif self.last_find_text:
            self.find_bar.find_input.setText(self.last_find_text)
            self.find_bar.find_input.selectAll()
            self.find_bar.action_find_next()
        # 激活視窗
        self.find_bar.update_search_results()
        self._set_FR_pos()
        self.FR_dock.show()
        self.FR_dock.activateWindow()
        self.find_bar.find_input.setFocus()

    def action_replace(self):
        """ 尋找+取代 """
        self.FR_dock.hide()
        self.replace_bar.show()
        self.find_bar.hide()
        cursor = self.text_edit.textCursor()
        # 優先尋找反白的部分
        if cursor.hasSelection():
            text = cursor.selection().toPlainText()
            self.replace_bar.find_input.setText(text)
            self.replace_bar.action_find_next()
        # 顯示上次搜尋的關鍵字
        elif self.last_find_text:
            self.replace_bar.find_input.setText(self.last_find_text)
            self.replace_bar.action_find_next()
        # 顯示上次取代的關鍵字
        if self.last_replace_text:
            self.replace_bar.replace_input.setText(self.last_replace_text)
            self.replace_bar.replace_input.selectAll()
        # 激活視窗
        self.replace_bar.update_search_results()
        self._set_FR_pos()
        self.FR_dock.show()
        self.FR_dock.activateWindow()
        self.replace_bar.replace_input.setFocus()

    def _set_theme(self):
        """ 切換色彩主題 """
        if self.theme == Theme.origin:
            # 作業系統原生主題
            app = QApplication.instance()
            if not isinstance(app, QApplication): raise RuntimeError("QApplication.instance is None")
            app.setStyleSheet("""
                QWidget { color: black; background-color: #ECECEC; }
                QPushButton { color: black; background-color: #F0F0F0; border: 1px solid #C0C0C0; }
                QPushButton:hover { background-color: #E6E6E6; }
                QPushButton:pressed { background-color: #C0C0C0; border-style: inset; }
                QLineEdit, QLabel { color: black; background-color: #ECECEC; }
                CodeEditor { color: black; background-color: white; }
                QDockWidget { color: black; background-color: #ECECEC; }
            """)
            QApplication.setStyle(QStyleFactory.create("Fusion")) # +這行更像light
            # qdarktheme的主題
        else: qdarktheme.setup_theme(self.theme.value)
        self.tab.update_zoom()

    def action_set_theme_dark(self):
        """ 切換到深色主題 """
        self.theme = Theme.dark
        self._set_theme()

    def action_set_theme_light(self):
        """ 切換到深色主題 """
        self.theme = Theme.light
        self._set_theme()

    def action_set_theme_origin(self):
        """ 切換到深色主題 """
        self.theme = Theme.origin
        self._set_theme()

    def action_close_tab(self):
        """ 關閉當前分頁 """
        self._handle_tab_close(self.tab_index)

    def action_auto_highlight(self):
        """ 自動判斷文件格式並高亮 """
        self.text_edit.blockSignals(True)
        self.text_edit.document().blockSignals(True)
        if self.file_path is None: 
            return self._auto_highlight("untitled.txt")
        self._auto_highlight(self.file_path)
        QApplication.processEvents()
        self.text_edit.blockSignals(False)
        self.text_edit.document().blockSignals(False)

    def action_disable_highlight(self):
        """ 禁用highlighter """
        if self.highlighter is None: return
        self.text_edit.blockSignals(True)
        self.text_edit.document().blockSignals(True)
        self.highlighter.setDocument(None)
        self.highlighter = None
        QApplication.processEvents()
        self.text_edit.blockSignals(False)
        self.text_edit.document().blockSignals(False)

    def action_highlight_as_python(self):
        """ 當作python source file編輯 """
        self.text_edit.blockSignals(True)
        self.text_edit.document().blockSignals(True)
        if self.highlighter is not None:
            self.highlighter.setDocument(None)
        self.highlighter = PyHighlighter(self.text_edit.document())
        QApplication.processEvents()
        self.text_edit.blockSignals(False)
        self.text_edit.document().blockSignals(False)

    def action_highlight_as_markdown(self):
        """ 當作python source file編輯 """
        self.text_edit.blockSignals(True)
        self.text_edit.document().blockSignals(True)
        if self.highlighter is not None:
            self.highlighter.setDocument(None)
        self.highlighter = MdHighlighter(self.text_edit.document())
        QApplication.processEvents()
        self.text_edit.blockSignals(False)
        self.text_edit.document().blockSignals(False)

    def switch_next_tab(self):
        """ 切換至下一個分頁 """
        current_index = self.tabs.currentIndex()
        total_tabs = self.tabs.count()
        # 切換(環繞)
        next_index = (current_index + 1) % total_tabs
        self.tabs.setCurrentIndex(next_index)
        self._handle_tab_change(next_index)

    def action_enable_line_wrap(self):
        """ 啟用自動換行 """
        option = self.text_edit.document().defaultTextOption()
        # 自動換行模式: 不切斷單字
        option.setWrapMode(QTextOption.WrapMode.WordWrap)
        self.text_edit.document().setDefaultTextOption(option)
        self.text_edit.setLineWrapMode(self.text_edit.LineWrapMode.WidgetWidth)

    def action_disable_line_wrap(self):
        """ 停用自動換行 """
        option = self.text_edit.document().defaultTextOption()
        # 自動換行模式: 停用
        option.setWrapMode(QTextOption.WrapMode.NoWrap)
        self.text_edit.document().setDefaultTextOption(option)
        self.text_edit.setLineWrapMode(self.text_edit.LineWrapMode.NoWrap)

    def closeEvent(self, a0):
        """ 關閉時的動作 """
        if a0 is None: raise ValueError("in closeEvent: a0 is None")
        for i in range(len(self.tab_list)):
            self.tab_index = i
            self.tabs.setCurrentIndex(i)
            if not self._dirty_warning_success():
                a0.ignore()
                return
        self._clear_master_password()
        a0.accept()

# pyinstaller --onefile --exclude-module PyQt5 --exclude-module PyQt6 --windowed --icon=main_icon.ico main.py
# pyinstaller --onedir --exclude-module PyQt5 --exclude-module PyQt6 --windowed --icon=main_icon.ico main.py
if __name__ == "__main__":
    with Code_Timer("init"):
        file_to_open = None
        app = QApplication(sys.argv)
        # 被開啟檔案的路徑
        if len(sys.argv) > 1: file_to_open = sys.argv[1]
        # 傳遞file_to_open
        window = MainWindow(file_to_open=file_to_open)
    window.show()
    sys.exit(app.exec())

# --- TODO: ---
# line_wrap_mode/clear_clipboard_on_exit/show_line_numbers
# setting: 
# color/color_theme/verify_password_first
# default_font_size/default_highlighter
# welcome_file/yoCrypt_init_param/FR
# Font Family/line_wrap_mode/sucure_timeout
# show_line_numbers/files_path
# 區分同名檔案(標籤顯示完整路徑)

# --- FIXME: --- 
