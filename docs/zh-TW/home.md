<link rel="shortcut icon" type="image/x-icon" href="https://yoyo-ace1110.github.io/yoCrypt-Editor/assets/favicon.ico">

# [yoCrypt-Editor](https://yoyo-ace1110.github.io/yoCrypt-Editor/)

<p align="center">
  <a href="https://github.com/Yoyo-ace1110/yoCrypt-Editor/releases"><img src="https://img.shields.io/github/v/release/Yoyo-ace1110/yoCrypt-Editor?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/Yoyo-ace1110/yoCrypt-Editor/blob/main/.github/LICENSE"><img src="https://img.shields.io/badge/license-Custom-important?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/github/languages/top/Yoyo-ace1110/yoCrypt-Editor?style=flat-square" alt="Top Language">
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=flat-square&logo=windows" alt="Platform">
  <a href="https://Yoyo-ace1110.github.io/yoCrypt-Editor/"><img src="https://img.shields.io/badge/Official%20Site-Live%20Demo-green?style=flat-square&logo=github" alt="View Site"></a>
</p>

**yoCrypt-Editor** 是一款旨在建立**輕量、快速、介面簡潔**，並整合**加密功能**的文字編輯器。它結合了 Python 的開發彈性與 C++ 的運算效能，為您的私人文件提供可靠的保護。

### 🎨 Screenshot

<p align="left">
  <img src="../assets/main_ui.png" alt="yoCrypt-Editor Main UI" width="90%">
</p>

## ✨ 主要特性 (Features)

- **極致輕量與快速**: 優化的啟動速度與低資源佔用，讓文字處理流暢無負擔。
- **簡潔 UI 設計**: 基於 **PySide6** 與 **QDarkTheme**，提供現代化且專注的作業環境。
- **內建強大加密**: 整合 **OpenSSL 3** 核心技術，確保您的資料安全性達到工業級標準。
- **無縫執行體驗**: 內建所有必要的 DLL，使用者無需額外安裝 OpenSSL 或 C++ 運行庫即可直接執行。
- **開發者工具整合**: 使用自有的 `yotools200.utils` 優化內部運作邏輯與資料處理。

## 🚀 快速開始 (Getting Started)

前往 [GitHub Releases](https://github.com/Yoyo-ace1110/yoCrypt-Editor/releases) 下載最新的版本，解壓後直接執行 `main/main.exe` 即可開始使用。

## 📖 專案文件

了解更多關於本編輯器的操作細節與技術: 

- ### [加密功能導覽](./encryption_features): 
  - Details on file operations and Master Password management.
- ### [加密技術細節](./encryption_detail): 
  - Deep dive into AES-256-GCM and memory security.
- ### [👈 返回語言選擇頁面](../index)

## 🛠️ 開發與依賴 (Dependencies)

如果你希望從源碼運行或進行開發，請確保環境中包含以下依賴: 

- **Python 3.9+**
- **PySide6**: 現代化的 Qt6 Python 綁定。
- **QDarkTheme**: 提供高品質的深色視覺主題。
- **yotools200**: 作者開發的工具集（已附於專案中）。
- **OpenSSL 3.x**: (專案已內建 libcrypto-3-x64.dll 和 libssl-3-x64.dll，開發環境編譯時需配置對應標頭檔)。

## 🐞 問題回報 (Report a Bug)

如果您在使用過程中遇到任何問題，或有功能改進建議，歡迎透過以下管道聯繫: 

1. **GitHub Issues**: [直接在這裡提交 Issue](https://github.com/Yoyo-ace1110/yoCrypt-Editor/issues)
2. **Email**: [liaojiayouy@gmail.com](mailto:liaojiayouy@gmail.com)

## 🌐 相關連結 (Websites)

- **官方專案首頁**: [yoCrypt-Editor GitHub](https://github.com/Yoyo-ace1110/yoCrypt-Editor)
- **核心技術**: [PySide6](https://pypi.org/project/PySide6/) | [OpenSSL](https://www.openssl.org/) | [QDarkTheme](https://github.com/5yutan5/PyQt-Dark-Theme)

## ⚖️ 授權與版權 (Copyright & License)

Copyright (c) 2026 Yoyo-ace1110. All Rights Reserved.

本專案採用的條款旨在確保專案的透明度與安全性: 
- **允許原樣散佈**: 允許在保持檔案原始狀態且註明出處（附帶原作者連結）的前提下進行散佈。
- **禁止商業行為**: 嚴禁任何形式的商業銷售、出租或作為收費服務的一部分。
- **免責聲明**: 本軟體按「原樣」提供，作者不承擔任何使用後果或損害賠償。
- 欲了解完整授權細節，請參閱 [License.txt](https://github.com/Yoyo-ace1110/yoCrypt-Editor/blob/main/License.txt)。

---

<p align="center">
  <small>
    © 2026 Yoyo-ace1110. All Rights Reserved.<br>
    Built with PySide6 & OpenSSL 3. 
    [<a href="mailto:liaojiayouy@gmail.com">Contact</a>] 
    [<a href="https://github.com/Yoyo-ace1110/yoCrypt-Editor">GitHub</a>]
  </small>
</p>
