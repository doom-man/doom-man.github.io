# 实例代码
```
#include <stdio.h>
#include "inlineHook.h"
int (*old_puts)(const char *) = NULL;
int new_puts(const char *string){
    old_puts("inlineHook success");
}
int hook(){
    if (registerInlineHook((uint32_t) puts, (uint32_t) new_puts, (uint32_t **) &old_puts) != ELE7EN_OK) {
        return -1;
    }
    if (inlineHook((uint32_t) puts) != ELE7EN_OK) {
        return -1;
    }
    return 0;
}
int unHook(){
    if (inlineUnHook((uint32_t) puts) != ELE7EN_OK) {
        return -1;
    }
    return 0;
}
int main(){
    puts("test");
    hook();
    puts("test");
	getchar();
    unHook();
    puts("test");
}
```
## Android-inline-Hook 源码解读
### 函数解析
```
enum ele7en_status registerInlineHook(uint32_t target_addr, uint32_t new_addr, uint32_t **proto_addr);
```
1. 判断目标地址和替换地址是否可执行，是否已被hook 。
2. 存储3个函数指针。
3. 复制目标函数指令 。
4. 分配mmap空间迁移指令
5. 标记状态为REGISTERED
```
enum ele7en_status inlineHook(uint32_t target_addr)
```
1. 从全局变量中查找目标地址是否存在
2. 检查状态为REGISTERED ,则调用doinlinehook
```
static void doInlineHook(struct inlineHookItem *item)
```
1. 使用mprotect() 修改动态链接库地址权限可读可写可执行。
2. 将proto_addr (注册函数时第三个参数) 指向目标函数指令
3. 修复目标地址为可执行 
