# 加载动态链接库 dlopen dlsym dlclose
## dlopen
```
void * dlopen( const char * pathname, int mode ); 


在dlopen的（）函数以指定模式打开指定的动态连接库文件，并返回一个句柄给调用进程。使用dlclose（）来卸载打开的库。 
mode：分为这两种 
RTLD_LAZY 暂缓决定，等有需要时再解出符号 
RTLD_NOW 立即决定，返回前解除所有未决定的符号。 
RTLD_LOCAL 
RTLD_GLOBAL 允许导出符号 
RTLD_GROUP 
RTLD_WORLD 
```

## dlsys 
从动态链接库中找出这个符号的地址。
```
void* dlsym(void* handle,const char* symbol) 
```

## dlclo
```
int dlclose (void *handle); 
```

## 简单示例
```
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
int main(int argc , char ** argv){
void * handle;
void * (*new_malloc)(size_t size);
handle = dlopen("libstdc++.so.6",RTLD_LAZY);
if(!handle){
	printf("err\n");
	exit(0);
}
new_malloc = dlsym(handle,"malloc");
void * a = new_malloc(0x20);
return 0;
}

```