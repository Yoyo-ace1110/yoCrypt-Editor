# Feature Guide

yoCrypt-Editor focuses on a seamless encryption experience. Below are the detailed operations available under the **File** menu:

## 📂 Open & Save Operations
The editor manages both plain text and encrypted files based on your security needs.

- **Open (Ctrl+Shift+O)**: Open standard unencrypted text files.
- **Open Crypted (Ctrl+O)**: Open AES-256 protected files. A password prompt will appear for verification.
- **Save / Save As**: Save or export content as plain text.
- **Save Crypted / Save Crypted As**: Encrypt and save current content. You will be prompted for a password if not already verified.
- **Auto Save (Ctrl+S)**: **Recommended**. Intelligently detects the file's initial state:
    - Encrypts and saves if the file was opened as encrypted.
    - Saves as plain text if the file was opened as unencrypted (default).

## 🔐 Key Management
- **Change Master Password**: 
    A core maintenance tool that updates your security credentials. Upon execution, the system prompts for a new password and automatically **re-encrypts all files** within the "Project/Files" directory using the new key.

---
[👈 Back to Home](./home) | [👉 Encryption Details](./encryption_detail)
