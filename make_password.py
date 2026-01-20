from yoCryptCpp import yoCrypt_init, hash_password
yoCrypt_init(360000, 16, 32)

password = bytearray("abc", "utf-8")

print(hash_password(password))
