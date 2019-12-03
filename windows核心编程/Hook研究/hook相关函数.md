

回调函数同SetWindowsHookEx一起使用，
```
LRESULT CALLBACK GetMsgProc(
  _In_ int    code,
  _In_ WPARAM wParam,
  _In_ LPARAM lParam
);
```

SetWindowsHookEx
    
了解 Windows 窗口程序的朋友都知道-窗口程序是靠消息驱动的，一切过程皆是消息，原本的消息传递过程是：系统接收到消息-将消息放入系统消息队列-将消息放入线程消息队列-线程中处理该消息，而钩子函数SetWindowsHookEx的作用就是拦截消息，用自定义的函数处理消息
1. 设置全局钩子，会拦截所有窗口线程的消息
2. 设置线程钩子，则只会拦截特定线程的消息

** 注意：当拦截当前线程消息时可以在当前代码中写回调函数，当拦截其它线程消息时则必须调用dll中回调函数**


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
- 
- 1 SetWindowsHookEx() 函数绑定回调函数后什么时候调用回调函数 
- 2 回调函数使用打印pritnf打印在哪里
- 3 callnexthookex 是什么作用   
- 

![image](13069581155047F690F3CB8A856AC20E)

查找了整个项目的文件都没有找到这个变量的声明?
答： 这是定义在动态链接库里面的共享数据段
![image](1D5570BFFB9543429AB186243AA27A2D)

