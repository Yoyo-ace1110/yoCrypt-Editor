# ENGLISH

# Contributing to yoCrypt-Editor

First of all, thank you for considering contributing to yoCrypt-Editor! It is through the support of the community that this project continues to improve.

## 🛠️ Development Environment Setup

Before you begin developing, please ensure your environment meets the following requirements:
- **Python**: 3.9+
- **C++ Compiler**: A compiler supporting C++17 (MSVC, GCC, or Clang)
- **Qt/PySide6**: For UI development
- **OpenSSL 3.x**: Core cryptographic components

## 🚀 How to Contribute

### 1. Reporting Bugs
If you find a bug (such as the previous EmojiHighlighter crash), please report it via [GitHub Issues](https://github.com/Yoyo-ace1110/yoCrypt-Editor/issues) and include:
- Your operating system version.
- Steps to consistently reproduce the error.
- Expected vs. actual results.

### 2. Feature Requests
If you have new ideas, feel free to open an issue and tag it as an `enhancement`.

### 3. Submitting Pull Requests (PR)
1. **Fork** this repository and create your branch.
2. **Commit** your changes. Ensure the message is clear, e.g., `fix: resolve font size issue in new window`.
3. **Push** to your branch.
4. Open a **Pull Request** and describe your changes in detail.

## 📜 Coding Standards

To maintain code readability and consistency, please adhere to the following principles:

### General Structure
- **Core Logic**: Keep the C++ core and Python UI decoupled as much as possible.
- **Commenting Style**: 
  - Use standard `# ...` for Python.
  - Use `// ...` for C++.
  - Include comments in Traditional Chinese or English for critical logic.
- **Type Hinting**: Explicitly state types for non-local variables.
- **Testing**: If the cryptographic logic is modified, you must test for compatibility with `make_password.py` and core components.

### Naming Conventions
- **Variables & Functions**: Use lowercase with underscores (`snake_case`), e.g., `target_file_path`.
- **Class Names**: Use capitalized first letters (`PascalCase`), e.g., `EncryptionManager`.
- **Constants**: Use all uppercase with underscores, e.g., `MAX_BUFFER_SIZE`.

### Documentation & Formatting
- **Function Descriptions**: Immediately follow function definitions with `""" ... """` (Docstrings) to explain the function's purpose.
- **Spacing**: Leave **one empty line** between functions, classes, and global variables.
- **Parameters**: Keep parameters compact within parentheses, formatted as `(a, b, ...)`.

## 📬 Contact
If you have any questions, feel free to reach out via GitHub Issues.

# 繁體中文

# 為 yoCrypt-Editor 做出貢獻

首先，感謝你考慮為 yoCrypt-Editor 做出貢獻！正是有了社群的支持，這個專案才能不斷進步。

## 🛠️ 開發環境設置

在開始開發之前，請確保你的環境符合以下要求：
- **Python**: 3.9+
- **C++ Compiler**: 支援 C++20 的編譯器 (擁有者是使用MINGW)
- **Qt/PySide6**: 用於介面開發
- **OpenSSL 3.x**: 核心加密組件

## 🚀 如何貢獻

### 1. 回報 Bug
如果你發現了錯誤（例如之前的 Highlighter 崩潰問題），請透過 [GitHub Issues](https://github.com/Yoyo-ace1110/yoCrypt-Editor/issues) 回報，並包含：
- 你的作業系統版本。
- 穩定重現錯誤的步驟。
- 預期結果與實際結果。

### 2. 提交功能建議
如果你有任何新想法，歡迎開啟一個 Issue 並標記為 `enhancement`。

### 3. 提交 Pull Request (PR)
1. **Fork** 本倉庫並建立你的分支 (Branch)。
2. **Commit** 你的修改。請確保訊息清晰，例如：`fix: resolve font size issue in new window`.
3. **Push** 到你的分支。
4. 開啟 **Pull Request** 並詳細描述你的改動。

## 📜 程式碼規範

為了維持程式碼的可讀性與一致性，請遵守以下原則：

### 基本結構
- **核心邏輯**: 盡量保持 C++ 核心與 Python UI 的解耦。
- **註解風格**: 
  - Python 請使用標準的 `# ...`
  - C++ 請使用 `// ...`
  - 關鍵邏輯請附上繁體中文或英文註解。
- **類型標註**: 非局部（Non-local）變數請務必註明型別。
- **測試**: 如果修改了加密邏輯，請務必測試 `make_password.py` 與核心組件的相容性。

### 命名慣例 (Naming Conventions)
- **變數與函數**: 使用小寫與下底線分隔（snake_case），例如 `target_file_path`。
- **類別名稱**: 使用首字母大寫（PascalCase），例如 `EncryptionManager`。
- **常數**: 全部大寫並以底線分隔，例如 `MAX_BUFFER_SIZE`。

### 文件化與排版
- **函式說明**: 在建立函數後，請立即以 `""" ... """` (Docstrings) 說明函數用途。
- **間距規範**: 函數、類別（Class）、全域變數之間請**空一行**。
- **參數格式**: 參數與括號間請保持緊湊，形式如 `(a, b, ...)`。

## 📬 聯絡方式
如果有任何疑問，歡迎透過 GitHub Issues 或是 liaojiayouy@gmail.com 與我聯繫。
