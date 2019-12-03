[TOC]

# 程序源码
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char* argv[], char* envp[]){
	printf("Welcome to pwnable.kr\n");
	printf("Let's see if you know how to give input to program\n");
	printf("Just give me correct inputs then you will get the flag :)\n");

	// argv
	if(argc != 100) return 0;
	if(strcmp(argv['A'],"\x00")) return 0;
	if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
	printf("Stage 1 clear!\n");	

	// stdio
	char buf[4];
	read(0, buf, 4);
	if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
	read(2, buf, 4);
        if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
	printf("Stage 2 clear!\n");
	
	// env
	if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
	printf("Stage 3 clear!\n");

	// file
	FILE* fp = fopen("\x0a", "r");
	if(!fp) return 0;
	if( fread(buf, 4, 1, fp)!=1 ) return 0;
	if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
	fclose(fp);
	printf("Stage 4 clear!\n");	

	// network
	int sd, cd;
	struct sockaddr_in saddr, caddr;
	sd = socket(AF_INET, SOCK_STREAM, 0);
	if(sd == -1){
		printf("socket error, tell admin\n");
		return 0;
	}
	saddr.sin_family = AF_INET;
	saddr.sin_addr.s_addr = INADDR_ANY;
	saddr.sin_port = htons( atoi(argv['C']) );
	if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
		printf("bind error, use another port\n");
    		return 1;
	}
	listen(sd, 1);
	int c = sizeof(struct sockaddr_in);
	cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
	if(cd < 0){
		printf("accept error, tell admin\n");
		return 0;
	}
	if( recv(cd, buf, 4, 0) != 4 ) return 0;
	if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
	printf("Stage 5 clear!\n");

	// here's your flag
	system("/bin/cat flag");	
	return 0;
}

```


# 解题思路

此题分为五个阶段：

## step 1
    命令行参数 ：个数为100 ， 检验以ascii码为索引的值，是否正确。

## step 2
    使用linux 的管道pipe() 函数  向管道的写端写入数据，将读端复制为 0 ， 2 然后执行程序。
    

## step 3
    使用getenv() 函数， 我们使用execve() 函数添加程序环境。
    
## step 4
    IO操作

## step 5 
    socket 编程， 服务端代码看input.c 客户端 exp.c  踩坑saddr.sin_addr.s_addr 的赋值。
    struct sockaddr_in 
    {
        sa_family_t sin_family;     //地址族
        uint16_t sin_port;          //16位TCP/UDP端口号
        struct in_addr sin_addr;    //32位ip地址
        char sin_zero[8];   //不使用
    }
    
    struct in_addr
    {
        In_addr_t s_addr;       //32位IPv4地址
    }
    
    inet_addr() 将点分十进制数 转化位长整型数
    
    ![image](BDD820E9523C4BCEBA6619A4B4B9EAE0)
    
    

# exp 
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(void){
	char * arg[101] ;
	arg[100]=NULL;
	int pid ;
	int pipefd[2];
	int errpipefd[2];
	char * env[2]  ={"\xde\xad\xbe\xef=\xca\xfe\xba\xbe",NULL};
	struct sockaddr_in sock_addr;
	int sockfd;
	for(int i = 0 ; i < 100 ;i++)
	{
		arg[i] = "a";
	}
	arg['A']="\x00";
	arg['B']="\x20\x0a\x0d";
	if(pipe(pipefd)<0 || pipe(errpipefd)<0)
		exit(0);
	write(pipefd[1] , "\x00\x0a\x00\xff", 4);
	write(errpipefd[1] , "\x00\x0a\x02\xff",4);

	FILE * fp = fopen("\x0a","w");
	if(!fp) return 0;
	if(fwrite("\x00\x00\x00\x00",4,1,fp)!=1) return 0;
	fclose(fp);
	arg['C'] = "8000";
	if((pid = fork())<0) exit(0);
// 	child
	 if(pid == 0) 
	{
		sleep(1);
		struct sockaddr_in saddr;
		int fd;
		fd = socket(AF_INET , SOCK_STREAM , 0);
		if(fd == -1)
		{
			printf("scoket error \n");
			return 0;
		}
		saddr.sin_family = AF_INET;
		saddr.sin_addr.s_addr = inet_addr("127.0.0.1");
		saddr.sin_port = htons(8000);
		if(-1 == connect(fd , (struct sockaddr *)&saddr , sizeof(saddr)))
		{
			printf("connect error\n");
			return 0;
		}
		write(fd , "\xde\xad\xbe\xef",4);
		printf("printf message sending \n");
	}
	else
	{
		dup2(pipefd[0],0);
		dup2(errpipefd[0],2);
        execve("input",arg,env);
	}
	return 0;
}

```