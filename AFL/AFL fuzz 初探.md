# 起因

hxb 的50道简单pwn，手撕重新性工作没有意义想要写个自动化脚本，看看fuzz 的插桩技术，二进制fuzz 测试时怎么进行的，其中是否可以捕捉到后门函数的运行。

## 插桩编译
```
afl-gcc -g -o afl_test a.c
```
建立两个文件fuzz_in 和 fuzz_out ，用来存放程序的输入和输出

编译项目文件时， 修改makefile。
gcc/g++重新编译目标程序的方法是：

```

CC=/path/to/afl/afl-gcc ./configure
make clean all
对于一个C++程序，要设置:
CXX=/path/to/afl/afl-g++.

```

## fuzz
创建输入输出文件,输入样例,开始fuzz
```
mkdir in out

root@iZj6c4v2sdd3vg27t7zi3mZ:~/fuzz_test_2/fuzz_in# cat case 
klajs
%p
%n
%hnn
$hn
$n
adadsad123


afl-fuzz -i fuzz_in/ -o fuzz_out/ ./a
```
捕捉到两个crash
```
00000000: 6b6c 616a 8a25 6e0a                      klaj.%n.

00000000: 2828 28b4 b4b4 bcb4 7fb4 b4ab b4b3 b6b4  (((.............
00000010: b47f 3b00 e1b4 b4b4 d3b4 b4b4 4d10 d3b4  ..;.........M...
00000020: b47f b4b4 abb4 b3b6 b0b4 7f3b 00e1 b4b4  ...........;....
00000030: 4d10                                     M.

```
一个溢出一个格式化


> reference xz.aliyun.com/t/4314

