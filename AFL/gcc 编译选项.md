afl-gcc 对gcc 进行封装并使用众多的参数,通过这个文档对参数进行解释

## 杂项
```
-O3 编译优化
-funro 循环优化
-Wall
-D_FOR
-Wno-p
-DAFL_
-DDOC_
-DBIN_

-B <> 添加编译器搜索路径
```
## 栈防护机制
```
-D_FORTIFY_SOURCE=2 检测字符串操作是否存在溢出问题,1 轻微检测仅在编译时检查,2 在运行时检查
-U_FORTIFY_SOURCE
```
## gcc 检查机制
```
-fsanitize=address 检查栈,堆,全局变量的边界值,UAF,Double free  ,Use after return , user after scope ,memory leak.
-fomit-frame-point  gcc 不产生栈帧
-fno-omit-frame-pointer gcc 产生栈帧
```


> [addressfsanitizer](https://clang.llvm.org/docs/AddressSanitizer.html)
> [linux 下Call stack 追溯机制](http://blog.sina.com.cn/s/blog_a558c25a0101l9yd.html)
> 

