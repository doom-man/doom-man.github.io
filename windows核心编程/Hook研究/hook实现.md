**重要的不是代码 ， 是思想**

# 通过控制台实现键盘鼠标hook
### 知识储备
- SetWindowsHookEx
```
HHOOK WINAPI SetWindowsHookEx(
int idHook,
HOOKPROC lpfn,
HINSTANCE hMod,
DWORD dwThreadId);
/*
idHook：钩子的类型，即它处理的消息类型
lpfn：指向dll中的函数或者指向当前进程中的一段代码
hMod：dll的句柄
dwThreadId：线程ID，当此参数为0时表示设置全局钩子
*/
```
- 回调函数同SetWindowsHookEx一起使用，
```
LRESULT CALLBACK GetMsgProc(
  _In_ int    code,
  _In_ WPARAM wParam,
  _In_ LPARAM lParam
);
```
