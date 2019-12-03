# 安装shadowsocks
```
pip install shadowsocks
```
# 配置文件
cat /etc/shadowsocks.json
```
{
        "server":"0.0.0.0",
        "local_port":1080,
        "port_password":{
                "443":"Man1314",
                "7899":"Man1314"
        },
        "timeout":300,
        "method":"aes-256-cfb",
        "fast_open": false

}
```
# 报错信息
```
Traceback (most recent call last):
  File "/usr/local/bin/ssserver", line 8, in <module>
    sys.exit(main())
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/server.py", line 34, in main
    config = shell.get_config(False)
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/shell.py", line 262, in get_config
    check_config(config, is_local)
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/shell.py", line 124, in check_config
    encrypt.try_cipher(config['password'], config['method'])
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/encrypt.py", line 44, in try_cipher
    Encryptor(key, method)
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/encrypt.py", line 83, in __init__
    random_string(self._method_info[1]))
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/encrypt.py", line 109, in get_cipher
    return m[2](method, key, iv, op)
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/crypto/openssl.py", line 76, in __init__
    load_openssl()
  File "/usr/local/lib/python2.7/dist-packages/shadowsocks/crypto/openssl.py", line 52, in load_openssl
    libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
  File "/usr/lib/python2.7/ctypes/__init__.py", line 379, in __getattr__
    func = self.__getitem__(name)
  File "/usr/lib/python2.7/ctypes/__init__.py", line 384, in __getitem__
    func = self._FuncPtr((name_or_ordinal, self))
AttributeError: /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1: undefined symbol: EVP_CIPHER_CTX_cleanup

```
openssl 升级导致的错误

是因为openssl1.1.0f版本中，废弃了EVP_CIPHER_CTX_cleanup函数，可以用EVP_CIPHER_CTX_reset来代替此函数

此文件  sudo vim /usr/local/lib/python2.7/dist-packages/shadowsocks/crypto/openssl.py中搜索所有的EVP_CIPHER_CTX_cleanup以EVP_CIPHER_CTX_reset代替即可，总共有两处。


```
ssserver -c /etc/shadowsocks.json -d start
```


