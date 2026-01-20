<link rel="shortcut icon" type="image/x-icon" href="https://yoyo-ace1110.github.io/yoCrypt-Editor/assets/favicon.ico">

## [yoCrypt-Editor](https://yoyo-ace1110.github.io/yoCrypt-Editor/en/home)
# Encryption Technology Details

yoCrypt-Editor is dedicated to providing data protection. We do not "roll our own crypto"; instead, we implement industry-standard, battle-tested cryptographic algorithms to ensure your privacy.

## 🛡️ Core Encryption Standard

The editor utilizes **AES-256-GCM** (Advanced Encryption Standard with Galois/Counter Mode):

- **AES-256**: The gold standard for symmetric encryption, featuring a 256-bit key length.

- **GCM Mode**: Provides both **confidentiality** and **integrity**. It ensures that if an encrypted file is tampered with, the editor will detect the anomaly and refuse to decrypt it, preventing "bit-flipping" attacks.

## 🔐 Key Derivation Function (KDF)

To protect against brute-force and dictionary attacks, we use **PBKDF2** (Password-Based Key Derivation Function 2) with **SHA-256**:

- **High Iteration Count**: We default to **360,000 iterations**, significantly increasing the computational cost for attackers using GPUs or ASICs.

- **Random Salting**: A unique, cryptographically secure salt is generated for every file. This ensures that even if two files have the same password, their encrypted ciphertexts will be completely different.

## 🧠 Memory Security

- **Immediate Zeroing**: Upon completing an encryption task or closing the application, the internal C++ core immediately overwrites the memory regions that held the master password.

- **Safety Tip**: For maximum security when handling extremely sensitive data, we recommend **restarting your computer** to clear potential data remnants of encrypted information from memory and to avoid security risks associated with Memory Dumps.

---
[👈 Back to Home](./home) | [👉 Encryption Features Guide](./encryption_features)
