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

> reference xz.aliyun.com/t/4314