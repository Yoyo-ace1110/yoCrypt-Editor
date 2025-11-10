from yotools200.yoCrypt import yoCrypt_init, hash_password
yoCrypt_init(360000, 16, 32, 'utf-8')

print(hash_password("abc"))
