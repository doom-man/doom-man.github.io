[TOC]
# clone
[link](https://www.tutorialspoint.com/unix_system_calls/clone.htm)
```
#include <sched.h> 

int clone(int (*fn)(void *), void *child_stack, 
          int flags, void *arg, ...   
          /* pid_t *pid, struct user_desc *tls 
", pid_t *" ctid " */ );"
```
fn 函数指针，子进程创建时执行该函数，参数为arg指向的字符串。函数结束时，子进程终止。

child_stack 为调用者为子进程分配的栈空间。

flags 
CLONE_VFORK | 直到自进程通过_exit or _execve 释放虚拟资源都suspend
---|---
CLONE_VM | 父进程和子进程运行在同样内存空间。
SIGCHID | 





