[TOC]

# checksec
```
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)

```
# 程序流程
新知识点JUMPOUT指令
```
if ( v5 <= 6 )
      JUMPOUT(__CS__, (char *)dword_402100 + dword_402100[v5]);
```
调试汇编代码发现跳转到参数2 ，所在地址。

1. alloc 固定分配malloc(0x61)，idx <= 0xf ,
2. show  打印存在格式化漏洞
3. edit  
4. delete uaf
5. become vip seccomp 规则
```
  if ( prctl(38, 1LL, 0LL, 0LL, 0LL, *(_QWORD *)&v1, &v4) < 0 )
  {
    perror("prctl(PR_SET_NO_NEW_PRIVS)");
    exit(2);
  }
  if ( prctl(22, 2LL, &v1) < 0 )
  {
    perror("prctl(PR_SET_SECCOMP)");
    exit(2);
  }
  return __readfsqword(0x28u) ^ v92;
```
局部测试
```
  1 #include <unistd.h>
  2 #include <stdio.h>
  3 #include <seccomp.h>
  4 #include <linux/seccomp.h>
  5 #include <fcntl.h>
  6 #include <sys/prctl.h>
  7 int main(void){
  8         char v1 = 11;
  9         char * v2;
 10         char v4 = 32;
 11         v2 = &v4;
 12         int ret_val = prctl(38,1,0,0,0,&v1,&v4);
 13         printf("%d\n",ret_val);
 14         char * filename = "/bin/sh";
 15         char * argv[] = {"/bin/sh",NULL};
 16         char * envp[] = {NULL};
 17         write(1,"i will give you a shell\n",24);
 18         syscall(59,filename,argv,envp);//execve
 19         return 0;
 20 }
```
```
i will give you a shell
$ sudo ls
sudo: effective uid is not 0, is sudo installed setuid root?
```
无法获得特权 
# exp
