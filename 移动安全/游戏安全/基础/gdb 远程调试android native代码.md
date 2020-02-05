# 准备工作


android 上运行的调试工具：gdbserver，该程序位于ndk目录/prebuilt/android-arm/gdbserver/gdbserver

pc上的调试工具：gdb，该程序位于ndk目录/prebuilt/linux-x86_64/bin/gdb

# 部署环境
```
adb push gdbserver /data/local/tmp
adb push hooktest /data/local/tmp
```
# 运行代码
```
/gdbserver  :8123 /data/local/tmp/hooktest 
//adb 端口转发
adb forward tcp:12345 tcp:8123
```
# 调试
arm-linux-androideabi-gdb

```
file ×××
target remote:1234 
```