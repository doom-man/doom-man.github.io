# 修改内核源码

参考patch [文件](https://github.com/doom-man/doom-man.github.io/kernel/patch.md)

常见错误[列表](https://github.com/doom-man/doom-man.github.io/kernel/error.md)

# 运行mykernel

```
qemu-system-i386 -kernel bzImage
```

# mykernel 运行过程分析

重新修改内核代码使之具有简单的进程运行环境和进程上下文切换，分析其运行过程。
## 进程相关结构体
结构体存放在mypcb.h 文件内容中，


> https://github.com/mengning/mykernel

