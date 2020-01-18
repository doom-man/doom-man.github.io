# 环境说明
内核版本2.6.32.1
busybos版本 1.19.4
gcc版本4.7
实验环境ubunut 16.04 64位
# 更新gcc
内核2.6.x只支持gcc 3.x 和 4.x.y，较高版本不支持老版本kernel 语法

gcc下降
```
sudo apt-get install -y gcc-4.7
sudo apt-get install -y g++-4.7
# 重新建立软连接
cd /usr/bin    #进入/usr/bin文件夹下
sudo rm -r gcc  #移除之前的软连接
sudo ln -sf gcc-4.7 gcc #建立gcc4.7的软连接
sudo rm -r g++  #同gcc
sudo ln -sf g++-4.7 g++
```
安装依赖
```
$ sudo apt-get install git fakeroot build-essential ncurses-dev xz-utils libssl-dev bc qemu qemu-system
$ sudo apt-get install bison flex libncurses5-dev
```
    
# 源码下载
官网：https://mirrors.edge.kernel.org/pub/linux/kernel/


国内镜像：https://mirrors.tuna.tsinghua.edu.cn/kernel/

```
$ wget https://www.kernel.org/pub/linux/kernel/v2.6/linux-2.6.32.1.tar.gz -O linux-2.6.32.1.tar.gz
$ tar -xvf linux-2.6.32.1.tar.gz
```

# 编译过程
```
$ cd linux-2.6.32.1/
$ make menuconfig
$ make
$ make all
$ make modules
```
# 编译错误
```
Can‘t use ‘defined(@array)‘ (Maybe you should just omit the defined()?) at kernel/timeconst.pl line 373.
/opt/ARM/mini6410/linux/linux-2.6.38/kernel/Makefile:140: recipe for target ‘kernel/timeconst.h‘ failed
make[1]: * [kernel/timeconst.h] Error 255
Makefile:916: recipe for target ‘kernel‘ failed
make: * [kernel] Error 2

将kernel/timeconst.pl中第373行的defined()去掉只留下@val就可以正常编译了。

unrecognized command line option '-m'
打开 linux-2.6.30/arch/x86/vdso/Makefile 文件，

1  修改28行，将-m elf_x86_64 修改为-m64;

2  修改72行，将-m elf_i386 修改为-m32

In file included from drivers/net/igbvf/ethtool.c:36:0:
drivers/net/igbvf/igbvf.h: At top level:
drivers/net/igbvf/igbvf.h:128:15: error: duplicate member ‘page’
scripts/Makefile.build:229: recipe for target 'drivers/net/igbvf/ethtool.o' failed
make[3]: *** [drivers/net/igbvf/ethtool.o] Error 1
scripts/Makefile.build:365: recipe for target 'drivers/net/igbvf' failed
make[2]: *** [drivers/net/igbvf] Error 2
scripts/Makefile.build:365: recipe for target 'drivers/net' failed
make[1]: *** [drivers/net] Error 2
Makefile:878: recipe for target 'drivers' failed
make: *** [drivers] Error 2

1. 根据linux社区的建议，此错误是由于gcc版本与内核版本的冲突导致的。他们的建议是更换新版本的内核，但是某些特殊条件下，我们不能更换内核版本，于是我们修改内核代码适应当前的编译器。

2. 按照错误的指示，错误的代码是在drivers/net/igbvf/igbvf.h文件的第128行。

3. 打开文件，看128行，代码为：struct page *page;再往上看，第123行，也有struct page *page这行代码，这个结构定义在内部的一个结构体中。就是他的名字与128行的重复了，而4.6.3的编译器对不支持这种方式的定义，我们修改128行的代码为struct page *pagep；保存退出；

4. 重新编译，编译通过。
```
[参考链接](https://www.anquanke.com/post/id/85837)



# 增加syscall
## 在syscall table 中添加信息
arch/x86/kernel/syscall_table_32.S 添加自己的调用
```
.long sys_pareto_test
.long sys_hello
```

## 定义syscall的宏
32位 arch/x86/include/asm/unistd_32.h
```
#define __NR_hello              337
#define __NR_pareto_test        338
#ifdef __KERNEL__
```
将NR_syscalls 修改成现有的调用数目，从337 修改为339
```
#define NR_syscalls 339

```
64位 修改arch/x86/include/asm/unistd_64.h
```
#define __NR_hello                              299
__SYSCALL(__NR_hello,sys_hello)
#define __NR_pareto_test                                300
__SYSCALL(__NR_pareto_test,sys_muhe_test)

#define NR_syscalls (__NR_syscall_max + 1)
```
## 添加函数定义
在include/linux/syscalls.h
```
asmlinkage long sys_pareto_test(int arg0);
asmlinkage long sys_hello(void);
```

## 编写syscall代码
新建目录放自定义syscall的代码， ./linux-2.26.32.1/pareto_test
```
#include <linux/kernel.h>
asmlinkage long sys_pareto_test(int arg0){
    printk("I am syscall");
    printk("syscall arg %d",arg0);
    return ((long)arg0);
}
asmlinkage long sys_hello(void){
    printk("hello my kernel worldn");
    return 0;
}

```
目录中写Makefile
```
obj-y := pareto_test.o
```

## 修改Makefile
添加目录
```
core-y		+= kernel/ mm/ fs/ ipc/ security/ crypto/ block/ pareto_test/

```

## 编译
```
make -j2
```
# busybox 下载安装

## 安装
下载[busybox](https://busybox.net/downloads/busybox-1.30.0.tar.bz2)压缩包解压
```
make menuconfig
```

进入settings ，选择build static binary (no shared libs)
```
make install 
```
## 配置
```
#!/bin/sh
echo "INIT SCRIPT"
mount -t proc none /proc
mount -t sysfs none /sys
mount -t debugfs none /sys/kernel/debug
mkdir /tmp
mount -t tmpfs none /tmp
mdev -s
echo -e "nBoot toos $(cut -d' ' -f1 /proc/uptime) secondsn"
exec /bin/sh
```

