[TOC]



# 安装

https://forum.xda-developers.com/showthread.php?t=3034811
下载apk 和对应sdk版本
https://blog.csdn.net/my_it_road/article/details/54666822

# sample
方便演示创建了一个empty activity项目

## 目录结构

![Snipaste_2020-04-24_10-35-57](J:\gitproject\doom-man.github.io\res\pic\Snipaste_2020-04-24_10-35-57.png)

## 代码

HookMain

```
package com.example.myapplication;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;
import android.util.Log;
public class HookMain implements IXposedHookLoadPackage {
    public static final String TAG = "MyHook";
    @Override

    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
        Log.d(TAG,"重启手机后，我执行了，说明这个 Xposed 模块生效了");
        if(!lpparam.packageName.equals("com.example.myapplication")) return; // 包名
        XposedHelpers.findAndHookMethod("com.example.myapplication.MainActivity", lpparam.classLoader, "getInfmation", new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                super.afterHookedMethod(param);
                Log.d(TAG,"重启手机后，我执行了，说明这个 Xposed 模块生效了");
                param.setResult("破解成功——by 一夜梦惊人");

            }
        });
    }
}
```

xposed_init

```
com.example.myapplication.HookMain
```

AndroidMainifest.xml

```
<meta-data
    android:name="xposedmodule"
    android:value="true" />
<meta-data
    android:name="xposeddescription"
    android:value="XposedProject" />
<meta-data
    android:name="xposedminversion"
    android:value="30" />
```

![Snipaste_2020-04-24_10-39-00](C:\Users\macl02\Desktop\doom-man.github.io\res\pic\Snipaste_2020-04-24_10-39-00.png)

build.gradle

```
compileOnly 'de.robv.android.xposed:api:82'
compileOnly 'de.robv.android.xposed:api:82:sources'
```

![Snipaste_2020-04-24_10-40-28](C:\Users\macl02\Desktop\doom-man.github.io\res\pic\Snipaste_2020-04-24_10-40-28.png)

# Xposed 原理

参考[Xpose框架分析]([https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/454904/#outline__3](https://codertw.com/程式語言/454904/#outline__3))   

1.Xposed：獨立實現了一版Xposed版的zyogte，即生成用來替換/system/bin/app_process的可執行檔案，該档案在系統啟動時在init.rc中被呼叫，啟動Zygote程序，init.zygote.rc中原始碼如下：

```
service zygote /system/bin/app_process -Xzygote /system/bin --zygote --start-system-server
class main
socket zygote stream 660 root system
onrestart write /sys/android_power/request_state wake
onrestart write /sys/power/state on
onrestart restart media
onrestart restart netd
```

## zyogte进程

作用：

1. 负责启动java虚拟机
2. 加载很多需要预加载的类
3. 负责启动systemServer ，systemServer 会启动android中的所有服务，基本上完成了上层框架的所有功能。
4. 负责初始化新进程，其实就是fork java的独立进程，比如启动一个act，那么zygote 就负责为新启动的act 建立进程，并调用act中的main，或者OnCreate，这样或许大家更容易理解。

【目的】所以hook Zygote 进程就可以达到全局hook。

参考[初识Zygote进程](https://www.jianshu.com/p/3dbe46439359)可以知道 Zygote是由java编写而成的, 所以也要先初始化虚拟机, 由app_process进程装载并运行ZygoteInit类. 

## app_process 

app_process创建一个AppRuntime变量，然后调用它的start成员函数, 由于AppRuntime类没有重写start函数, 所以调用的是其父类AndroidRuntime中的start函数. 在这个start函数中, 它干了三件事: 一是调用函数startVM启动虚拟机，二是调用函数startReg注册运行ZygoteInit时需要调用的JNI本地方法，三是调用了com.android.internal.os.ZygoteInit类的main函数.



## APP_RUNTIME

功能：java 运行时环境，



# 源码分析

## Xposed



## XposedBridge



## XposedInstaller





> https://blog.csdn.net/yzzst/article/details/47659987
>
> https://blog.csdn.net/yzzst/article/details/47829657