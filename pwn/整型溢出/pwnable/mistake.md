[TOC]

# 程序源码
    
```
#include <stdio.h>
#include <fcntl.h>

#define PW_LEN 10
#define XORKEY 1

void xor(char* s, int len){
	int i;
	for(i=0; i<len; i++){
		s[i] ^= XORKEY;
	}
}

int main(int argc, char* argv[]){
	
	int fd;
	if(fd=open("/home/mistake/password",O_RDONLY,0400) < 0){
		printf("can't open password %d\n", fd);
		return 0;
	}

	printf("do not bruteforce...\n");
	sleep(time(0)%20);

	char pw_buf[PW_LEN+1];
	int len;
	if(!(len=read(fd,pw_buf,PW_LEN) > 0)){
		printf("read error\n");
		close(fd);
		return 0;		
	}

	char pw_buf2[PW_LEN+1];
	printf("input password : ");
	scanf("%10s", pw_buf2);

	// xor your input
	xor(pw_buf2, 10);

	if(!strncmp(pw_buf, pw_buf2, PW_LEN)){
		printf("Password OK\n");
		system("/bin/cat flag\n");
	}
	else{
		printf("Wrong Password\n");
	}

	close(fd);
	return 0;
}

```

# 解题思路
刚看这道题发现一脸懵逼认真看了半个小时，这道题似乎误解。网上去看相关exp发现漏掉了最重要的部分，题目给出了提示有关操作符优先权， <  的优先权高于=所以if(fd=open("/home/mistake/password",O_RDONLY,0400) < 0) fd 的值要不为0 要不为1 ，文件打开成功则 fd == 0 ，所以从标准输入中读取数据。

![image](22883C99AF5048EBBC0D8FD2E891AF1E)

