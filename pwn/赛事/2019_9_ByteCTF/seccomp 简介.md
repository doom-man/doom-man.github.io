
[师傅链接](https://veritas501.space/2018/05/05/seccomp%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/)
# seccomp

测试代码：
```
//gcc -g simple_syscall_seccomp.c -o simple_syscall_seccomp -lseccomp
#include <unistd.h>
#include <seccomp.h>
#include <linux/seccomp.h>

int main(void){
	scmp_filter_ctx ctx;
	ctx = seccomp_init(SCMP_ACT_ALLOW);
	seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execve), 0); //添加规则
	seccomp_load(ctx); //应用规则

	char * filename = "/bin/sh";
	char * argv[] = {"/bin/sh",NULL};
	char * envp[] = {NULL};
	write(1,"i will give you a shell\n",24);
	syscall(59,filename,argv,envp);//execve
	return 0;
}
```
运行结果：
```
i will give you a shell
Bad system call
```

# prctl
```
#include <sys/prctl.h>

int prctl(int option, unsigned long arg2, unsigned long arg3,
          unsigned long arg4, unsigned long arg5);
```

option == PR_SET_NO_NEW_PRIVS(38) ，且arg2 ==1 ，无法获得特权

```
#include <unistd.h>
#include <sys/prctl.h>

int main(void){
	prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0);

	char * filename = "/bin/sh";
	char * argv[] = {"/bin/sh",NULL};
	char * envp[] = {NULL};
	write(1,"i will give you a shell\n",24);
	syscall(59,filename,argv,envp);//execve
	return 0;
}
```
运行结果
```
# veritas @ ubuntu in ~/test/seccomp
$ ./prctl_test                  
i will give you a shell
$ sudo sh
sudo: effective uid is not 0, is sudo installed setuid root?
$ whoami
veritas
$ id
uid=1000(veritas) gid=1000(veritas) groups=1000(veritas),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare)
$ sudo
sudo: effective uid is not 0, is sudo installed setuid root?
$
```
option == PR_SET_SECCOMP(22) , 效果就是secccomp ，只是格式不同。


解释一下,如果arg2为SECCOMP_MODE_STRICT(1),则只允许调用read,write,_exit(not exit_group),sigreturn这几个syscall.如果arg2为SECCOMP_MODE_FILTER(2),则为过滤模式,其中对syscall的限制通过arg3用BPF(Berkeley Packet Filter)的形式传进来,是指向struct sock_fprog数组的指针.