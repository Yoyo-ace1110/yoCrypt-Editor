<link rel="shortcut icon" type="image/x-icon" href="https://yoyo-ace1110.github.io/yoCrypt-Editor/assets/favicon.ico">

## [yoCrypt-Editor](https://yoyo-ace1110.github.io/yoCrypt-Editor/en/home)
# Feature Guide

yoCrypt-Editor focuses on a seamless encryption experience. Below are the detailed operations available under the **File** menu:

## 📂 Open & Save Operations
The editor manages both plain text and encrypted files based on your security needs.

- **Open (Ctrl+O)**: Open standard unencrypted text files.
- **Open Crypted (Ctrl+Shift+O)**: Open AES-256 protected files. A password prompt will appear for verification.
- **Save / Save As**: Save or export content as plain text.
- **Save Crypted / Save Crypted As**: Encrypt and save current content. You will be prompted for a password if not already verified.

- **Auto-Save (Ctrl+S)**: Behavior based on initial file state. The system automatically determines the saving method based on the state of the file when it was first opened:
    - Encrypted Files: If the file was encrypted upon opening, it will be automatically re-encrypted using the Master Password when saved.
    - Plaintext Files: If the file was a standard document upon opening, it will be saved as plaintext (unencrypted).
    - New Files: Newly created files will also be saved as plaintext by default.

## 🔐 Key Management
- **Change Master Password**: 
    A core maintenance tool that updates your security credentials. Upon execution, the system prompts for a new password and automatically **re-encrypts all files** within the "Project/Files" directory using the new key.

---
[👈 Back to Home](./home) | [👉 Encryption Details](./encryption_detail)
