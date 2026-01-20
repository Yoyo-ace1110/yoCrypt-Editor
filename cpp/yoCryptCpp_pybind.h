#ifndef YO_CRYPT_CPP_PYBIND_H
#define YO_CRYPT_CPP_PYBIND_H
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "yoCryptCpp.h"

// 定義模組名稱為 yoCryptCpp_pybind_module
PYBIND11_MODULE(yoCryptCpp_pybind_module, core) {
    core.doc() = "yoCryptCpp's Core\n";

    // 匯出初始化函數
    core.def("yoCrypt_init", &yo::yoCryptCpp_init, 
          pybind11::arg("count") = 360000, 
          pybind11::arg("salt_size") = 16, 
          pybind11::arg("hash_len") = 32,
          "Initialize global crypto parameters");

    // 匯出密碼雜湊與驗證
    core.def("hash_password", &yo::hash_password, "Hash password and return raw bytes (salt + key)");
    core.def("verify_password", &yo::verify_password, 
          pybind11::arg("password"), pybind11::arg("salt"), pybind11::arg("expected_key"), pybind11::arg("iterations"),
          "Verify password with constant-time comparison");

    // 匯出 AES 加密與解密
    core.def("AES_encrypt", &yo::AES_encrypt, "Encrypt plaintext using AES-256-GCM");
    core.def("AES_decrypt", &yo::AES_decrypt, "Decrypt ciphertext using AES-256-GCM");

    // 匯出手動覆寫記憶體的工具
    core.def("secure_clear", &yo::secure_clear, "Directly zero out a Python bytearray's memory");
}

#endif 
