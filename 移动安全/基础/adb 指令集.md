## 起因
雷神模拟器进入开发者模式，usb调试。

本地cmd 
```
adb connect 127.0.0.1
C:\Users\Drag0n>adb devices
List of devices attached
emulator-5554   device
127.0.0.1:5555  offline
```
## 解决方法关闭重启abd.exe
1. 5037为abd默认端口
2. 查看占用端口进程ip
```
netstat -ano | findstr 5037
```
3. 通过pid 看进程
```
tasklist /fi "PID eq 87568"
```
4. 杀死占用端口进程
```
taskkill /pid 87568 /f
```
## 指令
1. 查看系统软件包
```
adb shell pm list packages
```
2. 软件包地址
```
adb shell pm path com.jnmo.emp.jjgame
```

