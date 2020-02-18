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
## Android-inline-Hook 核心源码解读
```
enum ele7en_status registerInlineHook(uint32_t target_addr, uint32_t new_addr, uint32_t **proto_addr);
```
1. 判断目标地址和替换地址是否可执行，是否已被hook 。
2. 存储3个函数指针。
3. 复制目标函数指令 。
4. 分配mmap空间迁移指令
5. 标记状态为REGISTERED
```
enum ele7en_status inlineHook(uint32_t target_addr){
//..........仅仅保留关键代码.........
	if (item->status == REGISTERED) {
		pid_t pid;

		pid = freeze(item, ACTION_ENABLE);

		doInlineHook(item);

		unFreeze(pid);

		return ELE7EN_OK;
	}
	//.................
}
	
```
1. 从全局变量中查找目标地址是否存在
2. 检查状态为REGISTERED ,则调用doinlinehook
```
static void doInlineHook(struct inlineHookItem *item)
```
<<<<<<< HEAD

1. 使用mprotect() 修改动态链接库地址权限可读可写可执行。
2. 将proto_addr (注册函数时第三个参数) 指向目标函数指令
3. 修复目标地址为可执行 


   ```
   		if (TEST_BIT0(item->target_addr)) {
   		int i;
   
   		i = 0;
   		if (CLEAR_BIT0(item->target_addr) % 4 != 0) {
   			((uint16_t *) CLEAR_BIT0(item->target_addr))[i++] = 0xBF00;  // NOP
   		}
   		((uint16_t *) CLEAR_BIT0(item->target_addr))[i++] = 0xF8DF;
   		((uint16_t *) CLEAR_BIT0(item->target_addr))[i++] = 0xF000;	// LDR.W PC, [PC]  实现指令跳转
   		((uint16_t *) CLEAR_BIT0(item->target_addr))[i++] = item->new_addr & 0xFFFF;  // 保留目标地址低四位
   		((uint16_t *) CLEAR_BIT0(item->target_addr))[i++] = item->new_addr >> 16;  // 保留目标地址高四位 
   	}
   	else {
   		((uint32_t *) (item->target_addr))[0] = 0xe51ff004;	// LDR PC, [PC, #-4]
   		((uint32_t *) (item->target_addr))[1] = item->new_addr;
   	}
   ```

   

3. 恢复地址权限。

4. 设置状态。

### 核心内容

修改当前地址的地址的指令，使PC寄存器指向下一条指令，下一条指令为目标地址。

## 其余代码解读
```
static pid_t freeze(struct inlineHookItem *item, int action)
```
猜测冻结进程，然后开始修改已加载动态链接库代码内容，完成后unfree（）。
```
	if (count > 0) {
		pid = fork();

		if (pid == 0) {
			int i;

			for (i = 0; i < count; ++i) {
				if (ptrace(PTRACE_ATTACH, tids[i], NULL, NULL) == 0) {
					waitpid(tids[i], NULL, WUNTRACED);
					processThreadPC(tids[i], item, action);
				}
			}
			
			(SIGSTOP);

			for (i = 0; i < count; ++i) {
				ptrace(PTRACE_DETACH, tids[i], NULL, NULL);
			}

			raise(SIGKILL);
		}
		else if (pid > 0) {
			waitpid(pid, NULL, WUNTRACED);
		}
	}

```

