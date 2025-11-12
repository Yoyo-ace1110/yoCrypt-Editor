import sys, os, qdarktheme
from PyQt5.QtWidgets import * # pyright: ignore[reportWildcardImportFromLibrary]
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor, QTextDocument
from yotools200.yoCrypt import yoCrypt_init, hash_password, verify_password, yoAES
from yotools200.utils import resource_path, Code_Timer
yoCrypt_init(360000, 16, 32, 'utf-8')

encoding = 'utf-8'
password_file_name = "password.txt"
password_file = resource_path(password_file_name)
welcome_file = resource_path("Welcome.txt")
filedirname = os.path.dirname(os.path.abspath(__file__))
window: "MainWindow"

def _clear_dialog_input(dialog: QDialog):
    """ 清除QDialog的內容 """
    for widget in dialog.findChildren(QLineEdit):
        widget.clear()

class PasswordPrompt(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主密碼驗證")
        self.setFixedSize(300, 140)
        layout = QVBoxLayout()

        self.label = QLabel("請輸入主密碼")
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
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
        password = self.input.text()
        self.input.clear()
        try:
            # 讀取hashed_password
            hash_file = open(password_file, "r")
            stored_hash = hash_file.read().strip()
            hash_file.close()
            # 驗證成功
            if verify_password(password, stored_hash):
                self.success = True
                self.password = bytearray(password, encoding)
                self.accept()
            # 驗證失敗
            else:
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

class Tab:
    def __init__(self, main_window: "MainWindow", index: int, text_edit: QPlainTextEdit, file_path: str|None = None, is_dirty: bool = False, is_crypt: bool = False):
        self.main = main_window
        self.index = index
        self.text = text_edit
        self.path = file_path
        self.is_dirty = is_dirty
        self.is_crypt = is_crypt
        # 綁定事件
        self.text.textChanged.connect(self._handle_text_change)

    def _handle_text_change(self):
        """ 處理文字變更事件 """
        self.is_dirty = True
        self.update_title()

    def update_title(self):
        """ 更新title """
        if not self.path: return self.main.setTabText(self.index, "untitled●")
        title = os.path.basename(self.current_file)
        title = title+' ●' if self.is_dirty else title
        self.main.setTabText(self.index, title)

class FR_Bar(QWidget):
    def init(self, main_window: "MainWindow"):
        super().__init__(main_window)
        # 布局
        self.main_window = main_window
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(8, 4, 8, 4)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # 屬性
        self.case_sensitive = True # 預設區分大小寫
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
        self.case_button.clicked.connect(self.action_same_case) # 連接事件
        self.area_button.clicked.connect(self.action_find_area) # 連接事件
        self.find_input.textChanged.connect(self.update_search_results)
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

    def _calculate_match_count(self, text, flags):
        """ 遍歷文件計算總匹配數 """
        self.match_count = 0
        # 原始光標
        original_cursor = self.main_window.text_edit.textCursor()

        if self.search_range:
            # 進入範圍搜尋
            range_cursor = QTextCursor(self.search_range)
            start_pos = range_cursor.selectionStart()
            end_pos = range_cursor.selectionEnd() 
            # 設置臨時光標從範圍起點開始
            temp_cursor = QTextCursor(self.main_window.text_edit.document())
            temp_cursor.setPosition(start_pos)
            self.main_window.text_edit.setTextCursor(temp_cursor)
            # 遍歷計數
            while self.main_window.text_edit.find(text, flags): # pyright: ignore[reportCallIssue, reportArgumentType]
                match_cursor = self.main_window.text_edit.textCursor()
                # 匹配項超出範圍 停止計數
                if match_cursor.selectionEnd() > end_pos: break
                self.match_count += 1
        else:
            # 整體搜尋
            temp_cursor = QTextCursor(self.main_window.text_edit.document())
            temp_cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.main_window.text_edit.setTextCursor(temp_cursor)
            # 遍歷計數
            while self.main_window.text_edit.find(text, flags): # pyright: ignore[reportCallIssue, reportArgumentType]
                self.match_count += 1

        # 恢復光標位置
        self.main_window.text_edit.setTextCursor(original_cursor)

    def _find_current_index(self, text):
        """ 計算當前被選取匹配項是總數中的第幾個 """
        flags = QTextDocument.FindFlag()
        if self.case_sensitive: flags |= QTextDocument.FindFlag.FindCaseSensitively # 區分大小寫
        current_selection_start = self.main_window.text_edit.textCursor().selectionStart()
        original_cursor = self.main_window.text_edit.textCursor() 
        temp_cursor = QTextCursor(self.main_window.text_edit.document()) # 臨時光標
        
        current_index = 0
        # 範圍搜尋模式
        if self.search_range:
            # 從範圍上方開始
            range_cursor = QTextCursor(self.search_range)
            start_pos = range_cursor.selectionStart()
            end_pos = range_cursor.selectionEnd()
            temp_cursor.setPosition(start_pos) 
            self.main_window.text_edit.setTextCursor(temp_cursor)
            # 遍歷計數
            while self.main_window.text_edit.find(text, flags): # pyright: ignore[reportCallIssue, reportArgumentType]
                match_cursor = self.main_window.text_edit.textCursor()
                # 超出範圍停止
                if match_cursor.selectionEnd() > end_pos: break
                current_index += 1
                if match_cursor.selectionStart() == current_selection_start: break
        # 整體搜尋模式
        else: 
            temp_cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.main_window.text_edit.setTextCursor(temp_cursor)
            # 遍歷計數
            while self.main_window.text_edit.find(text, flags): # pyright: ignore[reportCallIssue, reportArgumentType]
                current_index += 1
                if self.main_window.text_edit.textCursor().selectionStart() == current_selection_start: break
                
        # 恢復光標位置
        self.main_window.text_edit.setTextCursor(original_cursor)
        return current_index

    def _action_find_base(self, flags: QTextDocument.FindFlag, move_operation: QTextCursor.MoveOperation):  
        """ 尋找功能基底 """
        search_text = self.find_input.text()
        if (not search_text) or (not self.match_count): 
            self.find_result.setText("-/-")
            return
        # 向flags方向尋找
        if self.case_sensitive: flags |= QTextDocument.FindFlag.FindCaseSensitively # type: ignore
        is_forward_search = not bool(flags & QTextDocument.FindFlag.FindBackward)
        found = self.main_window.text_edit.find(search_text, flags)

        # 範圍搜尋 (範圍內環繞)
        if self.search_range:
            range_cursor = QTextCursor(self.search_range)
            start_pos = range_cursor.selectionStart()
            end_pos = range_cursor.selectionEnd()
            # 檢查是否需要環繞
            if found:
                match_cursor = self.main_window.text_edit.textCursor()
                # Case: 向前找超過範圍終點
                if is_forward_search and match_cursor.selectionEnd() > end_pos:
                    found = False
                # Case: 向後找超過範圍起點
                elif not is_forward_search and match_cursor.selectionStart() < start_pos:
                    found = False
            # 範圍內環繞
            if not found:
                cursor = self.main_window.text_edit.textCursor()
                # 向前找/向後找
                if is_forward_search: cursor.setPosition(start_pos)
                else: cursor.setPosition(end_pos)
                self.main_window.text_edit.setTextCursor(cursor)
                # 重新搜尋
                if not self.main_window.text_edit.find(search_text, flags):
                    raise RuntimeError("text !found in action_find_next but found in _update_search_results")
        # 整體環繞
        elif not found:
            # 從move_operation環繞
            cursor = self.main_window.text_edit.textCursor()
            cursor.movePosition(move_operation)
            self.main_window.text_edit.setTextCursor(cursor)
            # 發生 -> bug
            if not self.main_window.text_edit.find(search_text, flags):
                raise RuntimeError("text !found in action_find_next but found in _update_search_results")
            
        # 聚焦mainwindow
        self.main_window.focus_text_edit()
        # 重新計算self.match_index
        self.match_index = self._find_current_index(search_text)
        text = f"{self.match_index}/{self.match_count}" if self.match_count else "查無結果"
        self.find_result.setText(text)

    def update_search_results(self):
        """ 變更時計算總數 """
        search_text = self.find_input.text()
        self.main_window.last_find_text = search_text
        if not search_text:
            self.match_count = 0
            self.find_result.setText("-/-")
            self._disable_buttons(True)
            return
        # 計算總數
        flags = QTextDocument.FindFlags() 
        if self.case_sensitive: flags |= QTextDocument.FindFlag.FindCaseSensitively
        self._calculate_match_count(search_text, flags)
        if self.match_count == 0:
            text = "查無結果"
            self._disable_buttons(True)
        else:
            text = f"-/{self.match_count}"
            self._disable_buttons(False)
        self.find_result.setText(text)

    def action_same_case(self):
        """ 區分大小寫 """
        self.case_sensitive = not self.case_sensitive
        # 視覺回饋(綠->區分)
        if not self.case_sensitive: self.case_button.setStyleSheet("")
        else: self.case_button.setStyleSheet("background-color: lightgreen;")

    def action_find_area(self): 
        """ 設定尋找範圍 """
        current_cursor = self.main_window.text_edit.textCursor()
        if (not current_cursor.hasSelection()) or (self.search_range is not None):
            self.search_range = None
            self.area_button.setStyleSheet("")
        else: # 有選取文字
            self.search_range = QTextCursor(current_cursor)
            self.area_button.setStyleSheet("background-color: lightgreen;")
        # 更新結果
        self.update_search_results()
        self.action_find_next()

    def action_find_next(self):
        """ 找下一個 """
        flags = QTextDocument.FindFlag() # 預設為向前尋找 (FindBackward=False)
        self._action_find_base(flags, QTextCursor.MoveOperation.Start)

    def action_find_prev(self):
        flags = QTextDocument.FindFlag.FindBackward # 向後尋找 
        self._action_find_base(flags, QTextCursor.MoveOperation.End)

    def action_replace_one(self):
        """ 取代 """
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        cursor = self.main_window.text_edit.textCursor()
        # 尋找欄為空則返回
        if not search_text: return
        if not cursor.hasSelection(): 
            return self.action_find_next()
        # 替換並設定光標位置
        origin_pos = cursor.position()
        cursor.insertText(replace_text)
        cursor.setPosition(origin_pos+len(replace_text))
        self.main_window.text_edit.setTextCursor(cursor)
        self.action_find_next()
        self.update_search_results()
        # dirty
        self.main_window.is_dirty = True
        self.main_window._update_tab_title()

    def action_replace_all(self):
        """ 全部取代 """
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not search_text: return
        flags = QTextDocument.FindFlags()
        if self.case_sensitive: flags |= QTextDocument.FindFlag.FindCaseSensitively
        original_cursor = self.main_window.text_edit.textCursor()
        temp_cursor = QTextCursor(self.main_window.text_edit.document())
        
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
        self.main_window.text_edit.setTextCursor(temp_cursor)
        while self.main_window.text_edit.find(search_text, flags):
            match_cursor = self.main_window.text_edit.textCursor()
            # 超出範圍->停止替換
            if self.search_range and match_cursor.selectionEnd() > end_pos: break 
            # 替換選取的文字
            match_cursor.insertText(replace_text)
            self.main_window.text_edit.setTextCursor(match_cursor)
            replace_count += 1
            last_position = match_cursor.position()

        # 恢復並更新
        self.main_window.text_edit.setTextCursor(original_cursor)
        if replace_count > 0:
            # 光標位置設定與反白
            final_cursor = self.main_window.text_edit.textCursor()
            final_cursor.setPosition(last_position)
            final_cursor.movePosition(
                QTextCursor.MoveOperation.Left, 
                QTextCursor.MoveMode.KeepAnchor, 
                len(replace_text)
            )
            final_cursor.setPosition(last_position)
            self.main_window.text_edit.setTextCursor(final_cursor)
            # dirty
            self.main_window.is_dirty = True
            self.main_window._update_tab_title()
        self.update_search_results()

class FindBar(FR_Bar):
    def __init__(self, main_window: "MainWindow"):
        super().init(main_window)
        super().init_find_bar()
        self.main_layout.addStretch(1)

class ReplaceBar(FR_Bar):
    def __init__(self, main_window: "MainWindow"):
        super().init(main_window)
        super().init_find_bar()
        super().init_replace_bar()
        self.main_layout.addStretch(1)

class MainWindow(QMainWindow):
    def __init__(self, file_to_open: str|None = None):
        super().__init__()
        # 建立視窗
        self.setWindowTitle("yoCrypt Editor")
        self.resize(800, 600)
        self.password: bytearray = bytearray() # 密碼
        self.current_file: str|None = None # 當前檔案名稱
        self.is_dirty: bool = False        # 檔案是否未儲存
        self.is_crypt: bool = False        # 是否為加密檔案
        self.first_FR: bool = True         # 是否尋找/取代過
        self.last_find_text = ""         # 上次的搜尋關鍵字
        self.last_replace_text = ""        # 上次的取代關鍵字
        # 初始化介面
        self.init_ui()
        self.focus_text_edit()
        # 支援直接開啟檔案
        if not self._handle_external_file(file_to_open if file_to_open else welcome_file):
            self._handle_external_file(welcome_file)

    def init_ui(self):
        # 設定 menuBar
        menubar = self.menuBar()
        if menubar is None: raise TypeError("menubar is None")

        # 在 menubar 中加入欄位
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        # 避免 _menu is None
        if file_menu is None: raise TypeError("file_menu is None")
        if edit_menu is None: raise TypeError("edit_menu is None")
        if view_menu is None: raise TypeError("view_menu is None")

        # 輸入框/提示(setStatusBar)
        self.text_edit = QPlainTextEdit(self)                   # 文字框建立
        self.text_edit.zoomIn(3)                                # 預設放大2次
        self.tabs = QTabWidget()                                # 分頁欄建立
        self.tabs.setTabsClosable(True)                         # 可以關閉
        self.tabs.addTab(self.text_edit, "")                    # 加入第一個分頁
        self.text_edit.textChanged.connect(self._handle_text_change) # 綁定文字變更事件

        self.default_font = self.text_edit.font()               # 預設字體
        self.default_point_size = self.default_font.pointSize() # 紀錄預設大小
        
        # 尋找/取代 layout
        self.FR_dock = QDockWidget("尋找/取代", self)  # 浮動視窗
        self.FR_dock.setObjectName("FindReplaceDock") # 設定名稱
        
        self.find_bar = FindBar(self)       # 尋找工具
        self.replace_bar = ReplaceBar(self) # 取代工具
        self.FR_switcher = QWidget()  # (尋找/取代)widget

        switcher_layout = QHBoxLayout(self.FR_switcher) # 水平布局
        switcher_layout.setContentsMargins(0, 0, 0, 0)  # 消除留白
        switcher_layout.addStretch(1)                   # 向右推
        switcher_layout.addWidget(self.find_bar)        # 加入find
        switcher_layout.addWidget(self.replace_bar)     # 加入replace

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

        # 主要layout (Tabs)
        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # 建立 QAction
        change_password_action = QAction("Change Password", self) # 更改主密碼

        new_action = QAction("New", self)                         # 新檔案
        open_action = QAction("Open", self)                       # 開啟普通檔案
        open_crypted_action = QAction("Open-Crypted", self)       # 開啟加密檔案
        save_action = QAction("Save", self)                       # 儲存成普通檔案
        save_crypted_action = QAction("Save-Crypted", self)       # 儲存成加密檔案
        save_as_action = QAction("Save as", self)                 # 另存為普通檔案
        save_as_crypted_action = QAction("Save as-Crypted", self) # 另存為加密檔案
        auto_save_action = QAction("auto_save", self)             # 自動化儲存

        zoom_in_action = QAction("Zoom In", self)                 # 字體放大
        zoom_out_action = QAction("Zoom Out", self)               # 字體縮小
        reset_zoom_action = QAction("Reset Zoom", self)           # 還原預設字體大小

        find_action = QAction("Find", self)
        replace_action = QAction("Replace", self)

        # 連接事件
        change_password_action.triggered.connect(self.change_master_password)

        new_action.triggered.connect(self.action_new)
        open_action.triggered.connect(self.action_open)
        open_crypted_action.triggered.connect(self.action_open_crypted)
        save_action.triggered.connect(self.action_save)
        save_crypted_action.triggered.connect(self.action_save_crypted)
        save_as_action.triggered.connect(self.action_save_as)
        save_as_crypted_action.triggered.connect(self.action_save_as_crypted)
        auto_save_action.triggered.connect(self.action_auto_save)

        zoom_in_action.triggered.connect(self.action_zoom_in)
        zoom_out_action.triggered.connect(self.action_zoom_out)
        reset_zoom_action.triggered.connect(self.action_zoom_reset)

        find_action.triggered.connect(self.action_find)
        replace_action.triggered.connect(self.action_replace)

        # 快捷鍵
        new_action.setShortcut("Ctrl+T")
        open_action.setShortcut("Ctrl+Shift+O")
        open_crypted_action.setShortcut("Ctrl+O")
        auto_save_action.setShortcut("Ctrl+S")

        zoom_in_action.setShortcut("Ctrl++")
        zoom_out_action.setShortcut("Ctrl+-")
        reset_zoom_action.setShortcut("Ctrl+0")

        find_action.setShortcut("Ctrl+F")
        replace_action.setShortcut("Ctrl+H")

        # 新增 action 至 menubar
        file_menu.addAction(change_password_action)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(open_crypted_action)
        file_menu.addAction(auto_save_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_crypted_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(save_as_crypted_action)

        edit_menu.addAction(find_action)
        edit_menu.addAction(replace_action)

        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)
        view_menu.addAction(reset_zoom_action)

    def focus_text_edit(self):
        """ active """
        self.text_edit.activateWindow()
        self.text_edit.setFocus()

    def _update_tab_title(self):
        """ 更新分頁title """
        current_index = self.tabs.currentIndex()
        if current_index == -1: return

        title = os.path.basename(self.current_file) if self.current_file else "untitled"
        title_now = self.tabs.tabText(current_index)
        title = title+' ●' if self.is_dirty else title
        if title != title_now: self.tabs.setTabText(current_index, title)

    def _ensure_password(self) -> bool:
        """ 檢查密碼是否存在 若不存在則彈出輸入框 """
        if not os.path.exists(password_file):
            QMessageBox.warning(self, "錯誤", "password.txt不存在")
            return False
        # 密碼已存在
        while (not self.password):
            login = PasswordPrompt()
            if (login.exec_() != QDialog.Accepted) or (not login.success): return False
            self.password = login.password
        return True

    def _dirty_warning_success(self) -> bool:
        """ 當檔案未儲存且會遺失時 詢問使用者是否要儲存(True代表不用cancel) """
        if (not self.is_dirty) or (self.current_file is None): return True
        reply = QMessageBox.question(self, "儲存變更",
            "檔案 ["+str(self.current_file)+"] 尚未儲存，是否要儲存變更？",
            # 提供 Yes, No, Cancel 三個選項
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel # 預設選中 Cancel 避免誤觸
        )
        if reply == QMessageBox.No: return True
        elif reply == QMessageBox.Yes: return self._auto_save()
        elif reply == QMessageBox.Cancel: return False
        else: raise ValueError(f"unexpected QMessageBox reply: {reply}")

    def _clear_master_password(self):
        """ 主密碼清理 """
        if isinstance(self.password, bytearray):
            for i in range(len(self.password)):
                self.password[i] = 0 
        self.password = bytearray()

    def action_new(self):
        """ 新檔案 """
        if not self._dirty_warning_success(): return
        self.current_file = None
        self.is_dirty = True
        self.is_crypt = False
        self.text_edit.clear()
        self._update_tab_title()

    def _read_file_from(self, file_path: str, hint: str, decrypt: bool = False) -> bool:
        """ 讀取指定位置的檔案 回傳是否成功 """
        file_name = os.path.basename(file_path)
        # 內部函數
        def msg(): 
            """ 更新statusBar """
            self.statusBar().showMessage(f"已{hint}: {file_name}", 4000) # pyright: ignore[reportOptionalMemberAccess]
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
                return False # 讀取失敗，直接返回
        if encrypted_data is None:
            QMessageBox.critical(self, "編碼錯誤", f"無法識別檔案 {file_name} 的編碼格式，開啟失敗。")
            return False
        # 解密/顯示/提示
        try: 
            plain_text = yoAES.decrypt(encrypted_data, self.password) if decrypt else encrypted_data
            self.text_edit.setPlainText(plain_text)
            self.statusBar().clearMessage() # pyright: ignore[reportOptionalMemberAccess]
            QTimer.singleShot(50, msg)
            self.current_file = file_path
            self.is_dirty = False # 寫在這裡確保只有成功開啟時才更新
            self._update_tab_title()
            self.is_crypt = decrypt
            return True
        except Exception as e: 
            QMessageBox.critical(self, "解密錯誤", f"解密檔案 {file_name} 失敗: {e}")
            self.text_edit.clear()
            return False

    def _handle_external_file(self, file_path: str) -> bool:
        """ 處理從外部傳入的檔案路徑 """
        if not self._read_file_from(file_path, "開啟檔案", False):
            self._update_tab_title()
            return False
        return True

    def _handle_text_change(self):
        """ 處理文字區的內容變更 設定is_dirty旗標並更新標題 """
        if not self.is_dirty:
            self.is_dirty = True
            self._update_tab_title()

    def _open_file(self, hint: str, decrypt: bool) -> bool:
        """ 選擇並開啟檔案 """
        if not self._dirty_warning_success(): return False
        options = QFileDialog.Options()
        # 取得路徑
        file_path, _ = QFileDialog.getOpenFileName(self, hint, "", "All Files (*)", options=options)
        if not file_path: return False # 取消
        # 開啟檔案
        return self._read_file_from(file_path, hint, decrypt)

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
            QTimer.singleShot(50, msg) # pyright: ignore[reportOptionalMemberAccess]
            self.is_dirty = False
            self._update_tab_title()
            self.is_crypt = encrypt
            return True
        # 儲存失敗
        except Exception as e: QMessageBox.critical(self, "錯誤", f"儲存{os.path.basename(file_path)}失敗: {e}")
        return False

    def action_save(self):
        """ 儲存普通檔案 """
        if self.current_file is None: return self.action_save_as()
        self._save_file(self.current_file, hint="儲存普通檔案", encrypt=False)

    def action_save_as(self):
        """ 另存普通檔案 """
        options = QFileDialog.Options()
        # 取得位址
        file_path, _ = QFileDialog.getSaveFileName(self, "另存普通檔案", "", "All Files (*)", options=options)
        if not file_path: return  # 使用者按取消
        self.current_file = file_path
        # 儲存
        self._save_file(self.current_file, hint="另存普通檔案", encrypt=False)

    def action_save_crypted(self):
        """ 儲存加密檔案 """
        if not self._ensure_password(): return
        # 尚未設定檔案位址
        if self.current_file is None: return self.action_save_as_crypted()
        # 已設定位址
        self._save_file(self.current_file, hint="儲存加密檔案", encrypt=True)

    def action_save_as_crypted(self):
        """ 另存加密檔案 """
        if not self._ensure_password(): return
        hint = "另存加密檔案"
        # 取得位址
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, hint, "", "All Files (*)", options=options)
        if not file_path: return  # 使用者按取消
        self.current_file = file_path
        # 加密儲存
        self._save_file(file_path, hint=hint, encrypt=True)

    def _auto_save(self) -> bool:
        """ 自動判斷並儲存-有回傳值 """
        if self.is_crypt: 
            if not self._ensure_password(): return False
            # 同action_save_as_crypted
            if (self.current_file is None):
                hint = "另存加密檔案"
                options = QFileDialog.Options()
                file_path, _ = QFileDialog.getSaveFileName(self, "另存加密檔案", "", "All Files (*)", options=options)
                if not file_path: return False # 使用者按取消
            # 同action_save_crypted
            else:
                hint="儲存加密檔案"
                file_path = self.current_file
            if self._save_file(file_path, hint=hint, encrypt=True):
                self.current_file = file_path
                return True
            return False
        # 同action_save
        if (self.current_file is not None):
            return self._save_file(self.current_file, hint="儲存普通檔案", encrypt=False)
        # 同action_save_as
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "另存普通檔案", "", "All Files (*)", options=options)
        if not file_path: return False # 使用者按取消
        self.current_file = file_path
        return self._save_file(self.current_file, hint="另存普通檔案", encrypt=False)
    
    def action_auto_save(self):
        """ 自動判斷並儲存-沒回傳值 """
        self._auto_save()

    def change_master_password(self):
        """ 更改主密碼 """
        if not self._ensure_password(): return
        if not self._dirty_warning_success(): return

        # 舊密碼輸入與驗證
        dialog = QInputDialog(self)
        dialog.setWindowTitle("更改主密碼")
        dialog.setLabelText("請輸入舊密碼:")
        dialog.setTextEchoMode(QLineEdit.Password)
        if not dialog.exec_(): return # cancel
        
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
            del old_password_for_verification # 驗證失敗 清除 bytearray 引用
            QMessageBox.warning(self, "錯誤", "舊密碼錯誤！")
            return
        # 驗證成功 清除 bytearray 引用
        del old_password_for_verification 
        
        # 新密碼輸入與確認
        new_password_str = ""
        confirm_password_str = ""
        while True:
            # 輸入新密碼
            dialog = QInputDialog(self)
            dialog.setWindowTitle("更改主密碼")
            dialog.setLabelText("請輸入新密碼: ")
            dialog.setTextEchoMode(QLineEdit.Password)
            if not dialog.exec_(): return # cancel
            new_password_str = dialog.textValue()
            _clear_dialog_input(dialog) # 清除 UI 輸入
            
            # 確認新密碼
            dialog = QInputDialog(self)
            dialog.setWindowTitle("更改主密碼")
            dialog.setLabelText("請確認新密碼:")
            dialog.setTextEchoMode(QLineEdit.Password)
            if not dialog.exec_(): return # cancel
            confirm_password_str = dialog.textValue()
            _clear_dialog_input(dialog) # 清除 UI 輸入

            # 驗證與錯誤處理
            if not new_password_str or not confirm_password_str: 
                QMessageBox.warning(self, "錯誤", "密碼不能為空")
                new_password_str = ""
                confirm_password_str = ""
                continue
            if new_password_str != confirm_password_str:
                QMessageBox.warning(self, "錯誤", "兩次輸入的密碼不一致")
                new_password_str = ""
                confirm_password_str = ""
                continue
            break
        
        # 密碼轉換與清除
        new_password_bytearray = bytearray(new_password_str, encoding)
        del confirm_password_str # 清除臨時 str 變數的引用
        
        # 更新 Files 內所有 txt 檔案
        for fname in os.listdir(os.path.join(filedirname, "Files")):
            if (not fname.endswith(".txt")) or (fname == password_file_name): 
                continue
            fpath = os.path.join(filedirname, "Files", fname)
            try:
                # 解密&重新加密
                with open(fpath, "r", encoding="utf-8") as f:
                    encrypted_data = f.read()
                plain_text = yoAES.decrypt(encrypted_data, self.password)
                new_encrypted = yoAES.encrypt(plain_text, new_password_bytearray)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_encrypted)
            except Exception as e:
                # 問使用者是否繼續
                reply = QMessageBox.question(
                    self,
                    "檔案加密失敗",
                    f"檔案 {fname} 重新加密失敗: {e}\n是否繼續更新剩下的檔案? \n注意: 更新後 {fname} 將無法讀取",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No: # 停止整個更改流程
                    QMessageBox.information(self, "取消", "主密碼更改已取消")
                    # 錯誤發生時 也確保所有密碼被清除
                    del new_password_bytearray
                    del new_password_str
                    return 
                continue

        # 更新密碼與清理
        self._clear_master_password() 
        self.password = new_password_bytearray
        with open(os.path.join(filedirname, "password.txt"), "w", encoding="utf-8") as f:
            f.write(hash_password(new_password_str))
        del new_password_str
        
        QMessageBox.information(self, "完成", "主密碼已更新 所有txt已重新加密")

    def action_zoom_in(self):
        """ 字體放大 """
        self.text_edit.zoomIn(1)

    def action_zoom_out(self):
        """ 字體縮小 """
        self.text_edit.zoomOut(1)
    
    def action_zoom_reset(self):
        """ 還原預設字體大小 """
        font = self.text_edit.font()
        font.setPointSize(self.default_point_size)
        self.text_edit.setFont(font)

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
        self._set_FR_pos()
        # 顯示上次搜尋的關鍵字
        if self.last_find_text:
            self.find_bar.find_input.setText(self.last_find_text)
            self.find_bar.action_find_next()
            self.find_bar.find_input.selectAll()
        # 激活輸入框
        self.FR_dock.activateWindow()
        self.find_bar.find_input.setFocus()
        self.find_bar.update_search_results()
        self.FR_dock.adjustSize()
        self.FR_dock.show()

    def action_replace(self):
        """ 尋找+取代 """
        self.FR_dock.hide()
        self.replace_bar.show()
        self.find_bar.hide()
        self._set_FR_pos()
        # 顯示上次搜尋的關鍵字
        if self.last_find_text:
            self.find_bar.find_input.setText(self.last_find_text)
            self.find_bar.action_find_next()
        # 顯示上次取代的關鍵字
        if self.last_replace_text:
            self.replace_bar.replace_input.setText(self.last_replace_text)
            self.replace_bar.replace_input.selectAll()
        # 激活視窗
        self.FR_dock.activateWindow()
        self.replace_bar.replace_input.setFocus()
        self.replace_bar.update_search_results()
        self.FR_dock.adjustSize()
        self.FR_dock.show()

    def closeEvent(self, a0):
        """ 關閉時的動作 """
        if a0 is None: raise ValueError("in closeEvent: a0 is None")
        if not self._dirty_warning_success():
            a0.ignore()
            return
        self._clear_master_password()
        a0.accept()

# pyinstaller --onefile --windowed --icon=main_icon.ico main.py
if __name__ == "__main__":
    with Code_Timer("init"):
        file_to_open = None
        app = QApplication(sys.argv)
        qdarktheme.setup_theme("dark")
        # 被開啟檔案的路徑
        if len(sys.argv) > 1: file_to_open = sys.argv[1]
        # 傳遞file_to_open
        window = MainWindow(file_to_open=file_to_open)
    window.show()
    sys.exit(app.exec_())
# tabs?
# color themes?
