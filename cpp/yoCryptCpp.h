#ifndef YO_CRYPT_CPP_H
#define YO_CRYPT_CPP_H
#pragma once

#include <pybind11/pybind11.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>
#include <algorithm>
#include <stdexcept>
#include <sstream>
#include <vector>

namespace yo {

static int _g_count;
static int _g_salt_size;
static int _g_hash_len;
static bool _g_already_init = false;

// 確保初始化 
void _ensure_init() {
    if (!_g_already_init) {
        throw std::runtime_error("yoCryptCpp hasn't init");
    }
} 

// 初始化設定
void yoCryptCpp_init(int count = 360000, int salt_size = 16, int hash_len = 32) {
    _g_count = count;
    _g_salt_size = salt_size;
    _g_hash_len = hash_len;
    _g_already_init = true;
}

// 覆寫記憶體
void secure_clear(pybind11::bytearray data) {
    // 取得長度跟指標
    char* buf = PyByteArray_AsString(data.ptr());
    ssize_t len = PyByteArray_Size(data.ptr());
    // 清除
    std::fill(buf, buf + len, 0);
}

// 密碼雜湊與驗證
std::vector<unsigned char> hash_password(pybind11::bytearray password) {
    _ensure_init();
    // 密鹽
    std::vector<unsigned char> salt(_g_salt_size);
    // 呼叫 OpenSSL 的隨機數產生器
    if (RAND_bytes(salt.data(), _g_salt_size) != 1) {
        throw std::runtime_error("RAND_bytes failed");
    }
    // 輸出key
    std::vector<unsigned char> key_out(_g_hash_len);
    int success = PKCS5_PBKDF2_HMAC(
        PyByteArray_AsString(password.ptr()), // 密碼指標
        PyByteArray_Size(password.ptr()),     // 密碼長度
        salt.data(),                          // Salt 指標
        salt.size(),                          // Salt 長度
        _g_count,                               // 疊代次數
        EVP_sha256(),                         // 指定 SHA256 演算法
        _g_hash_len,                            // 預計輸出的長度
        key_out.data()                        // 結果存放地
    );
    if (success != 1) throw std::runtime_error("PBKDF2 calculation failed");
    std::vector<unsigned char> result;
    // 先放salt再放key
    result.reserve(salt.size() + key_out.size());
    result.insert(result.end(), salt.begin(), salt.end());
    result.insert(result.end(), key_out.begin(), key_out.end());
    // 回傳
    return result;
}

bool verify_password( 
    pybind11::bytearray password, 
    const std::vector<unsigned char>& salt, 
    const std::vector<unsigned char>& expected_key, 
    int iterations
) {
    _ensure_init();
    // 準備計算新key
    size_t key_len = expected_key.size();
    std::vector<unsigned char> computed_key(key_len);
    // 計算PBKDF2
    int success = PKCS5_PBKDF2_HMAC(
        PyByteArray_AsString(password.ptr()), 
        PyByteArray_Size(password.ptr()), 
        salt.data(), 
        salt.size(),
        iterations, // 使用從字串拆出來的次數
        EVP_sha256(),
        static_cast<int>(key_len),
        computed_key.data()
    );
    if (success != 1) return false;
    // (Constant-time comparison)
    int is_different = CRYPTO_memcmp(computed_key.data(), expected_key.data(), key_len);
    // 覆寫臨時計算結果
    std::fill(computed_key.begin(), computed_key.end(), 0);
    return is_different == 0;
}

// AES加密與解密
std::vector<unsigned char> AES_encrypt(const std::vector<unsigned char>& plain_text, pybind11::bytearray password) {
    _ensure_init();
    // 產生隨機數 (GCM標準)
    std::vector<unsigned char> salt(_g_salt_size);
    std::vector<unsigned char> nonce(16); 
    RAND_bytes(salt.data(), _g_salt_size);
    RAND_bytes(nonce.data(), nonce.size());
    // PBKDF2
    std::vector<unsigned char> key(32); // AES-256 -> 32 bytes
    PKCS5_PBKDF2_HMAC(
        PyByteArray_AsString(password.ptr()), PyByteArray_Size(password.ptr()),
        salt.data(), salt.size(), _g_count, EVP_sha256(), 32, key.data()
    );
    // 設定加密context
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_EncryptInit_ex(ctx, NULL, NULL, key.data(), nonce.data());
    // 執行加密
    std::vector<unsigned char> ciphertext(plain_text.size());
    int len, final_len;
    EVP_EncryptUpdate(ctx, ciphertext.data(), &len, reinterpret_cast<const unsigned char*>(plain_text.data()), plain_text.size());
    EVP_EncryptFinal_ex(ctx, ciphertext.data() + len, &final_len);
    // 取得 GCM Tag (16 bytes)
    std::vector<unsigned char> tag(16);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag.data());
    // 銷毀金鑰
    EVP_CIPHER_CTX_free(ctx);
    std::fill(key.begin(), key.end(), 0);
    // salt + nonce + tag + ciphertext
    std::vector<unsigned char> result;
    result.insert(result.end(), salt.begin(), salt.end());
    result.insert(result.end(), nonce.begin(), nonce.end());
    result.insert(result.end(), tag.begin(), tag.end());
    result.insert(result.end(), ciphertext.begin(), ciphertext.end());
    return result;
}

std::vector<unsigned char> AES_decrypt(const std::vector<unsigned char>& encrypted_text, pybind11::bytearray password) {
    _ensure_init();
    // 拆解資料 (salt:16, nonce:16, tag:16, cipher:其餘)
    auto it = encrypted_text.begin();
    std::vector<unsigned char> salt(it, it + 16); it += 16;
    std::vector<unsigned char> nonce(it, it + 16); it += 16;
    std::vector<unsigned char> tag(it, it + 16); it += 16;
    std::vector<unsigned char> ciphertext(it, encrypted_text.end());
    // 衍生金鑰 (必須跟加密時的 salt 一致)
    std::vector<unsigned char> key(32);
    PKCS5_PBKDF2_HMAC(
        PyByteArray_AsString(password.ptr()), PyByteArray_Size(password.ptr()),
        salt.data(), salt.size(), _g_count, EVP_sha256(), 32, key.data()
    );
    // 設定解密context
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_DecryptInit_ex(ctx, NULL, NULL, key.data(), nonce.data());
    // 執行解密
    std::vector<unsigned char> plaintext(ciphertext.size());
    int len;
    EVP_DecryptUpdate(ctx, plaintext.data(), &len, ciphertext.data(), ciphertext.size());
    // 設定預期的 Tag (驗證資料完整性)
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, 16, tag.data());
    // 結束解密並驗證
    int ret = EVP_DecryptFinal_ex(ctx, plaintext.data() + len, &len);
    EVP_CIPHER_CTX_free(ctx);
    std::fill(key.begin(), key.end(), 0);
    if (ret <= 0) {
        std::fill(plaintext.begin(), plaintext.end(), 0);
        throw std::runtime_error("解密失敗：資料可能被篡改或密碼錯誤");
    }
    return std::vector<unsigned char>(plaintext.begin(), plaintext.end());
}

} // namespace yo end

#endif
