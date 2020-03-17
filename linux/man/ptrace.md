函数定义
```
       #include <sys/ptrace.h>
       long ptrace(enum __ptrace_request request, pid_t pid,
                   void *addr, void *data);
```
# flags
## PTRACE_PEEKTEXT
从内存addr读取一个字长的数据作为返回值返回
## PTRACE_POKETEXT 
将data复制进addr 
## PTRACE_GETREGS
将对应得通用寄存器或浮点寄存器复制到data中
## PTRACE_SETREGS
从data中修改对应的通用寄存器或浮点寄存器
## PTRACE_CONT
重启停止的追踪进程
## PTRACE_ATTACH
附加指定进程
## PTRACE_DETACH
和PTRACE_COUNT相同，但从附加进程中分离。