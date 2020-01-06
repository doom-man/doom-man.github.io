# 解锁

想要做下面这些事，需要先**在开发者选项里打开oem解锁**
如果你的手机是V版（运营商定制版），请看这里：[oem解锁选项灰色](http://blog.luen.me/2018/07/07/Pixel-Verizon-unlock/index.html)

#### 1.2 进入bootloader模式

开机打开调试模式，连接数据线，执行下面的命令，需要[安装Android SDK](https://developer.android.com/studio/releases/platform-tools.html)以及配置环境变量

```
adb  reboot bootloader
```

然后在手机上操作解锁

> 如果SDK成功安装而fastboot命令无法正常执行，请确认SDK版本是23.0.1及以上版本，[最新SDK下载](https://developer.android.com/studio/releases/platform-tools.html)

如果是更旧的设备，请用下面命令

```
fastboot oem unlock
```

如果还不行，试试这个

```
fastboot flashing unlock_critical1
```

再不行就得确认你的OEM有没有正确解锁了。

###  刷Rom

####  刷映像（所谓的强刷）：

#####  映像下载

[官网镜像下载](https://developers.google.com/android/images)

##### 2.1.2 缺点

删除所有数据，包括SD卡数据

##### 2.1.3 刷机步骤

1. 手机进入bootloader模式（`adb reboot bootloader`）

2. 在电脑上解压映像压缩文件，并使用命令行进入解压后的映像目录

3. 命令行执行`./flash-all.sh`(Mac/Linux) 或者 `./flash-all.bat`(Windows)

4. 等待重启

   ### 3. ROOT

   > 该方式我只在Pixel系列手机上验证过，nexus系列手机未验证

   #### 3.1 下载TWRP的recovery

   [下载地址](https://twrp.me/Devices/)

   ##### 3.1.1 进去后搜索你的设备

   ##### 3.1.2 然后进入自己的设备页面，选择自己手机的产地

   ##### 3.1.3 接着下载zip文件和img文件，这两个版本得一致，下载最新的就好。

   3.2 下载Magisk
   下载地址，这是一个root管家，进网页后往下拖到网页中部会有一个download按钮

   3.3 把资源推送到手机
   把下载好的twrp-pixel-installer-sailfish-3.2.2-0.zip文件push到手机上的sdcard
   把下载好的Magisk-v16.0.zip文件push到手机上的sdcard3.4 进入临时的TWRP模式
   进入bootloader模式，然后运行

   fastboot boot ./twrp-3.2.2-0-sailfish.img
   1
   手机会进入twrp的recovery页面

   3.5 安装TWRP
   在临时的TWRP模式首页，点击install按钮
   找到twrp-pixel-installer-sailfish-3.2.2-0.zip文件并点击文件进行安装
   安装好后按返回键退回到主页，不需要重启
   3.6 安装Magisk
   安装完TWRP后会退回到首页，再次点击install按钮
   找到Magisk-v16.0.zip安装
   安装好之后重启到系统



启动后点击magisk 调出设置给shell root 权限.