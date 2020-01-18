# unable
```
unable to access Android SDK add-on list
```
第一次使用未检测到SDK包，cancel 后安装SDK.
# 踩坑

```
INFO - .project.GradleProjectResolver - Gradle project resolve error
org.gradle.tooling.GradleConnectionException: Could not install Gradle distribution from ‘https://services.gradle.org/distributions/gradle-2.10-all.zip.
```
删除报错地址的gradle-xxxx-xx.zip，将自己下载的对应版粘贴进去。
sync project。

## 使用过程中的所有目录都不要有空格。。。。。。
```
ERROR: Cause: executing external native build for ndkBuild G:\VirtualApp\lib\src\main\jni\Android.mk

```

****ndk版本问题****（ndk 应该可以说是一个集成的编译开发环境，*.mk 负责指定编译的文件、参数、库文件）

ndk17以后不再支持gnu

```
///VirtualApp/lib/src/main/jni/Application.mk
APP_ABI := armeabi-v7a x86
APP_PLATFORM := android-14
APP_STL := gnustl_static # 这一行在作妖
APP_OPTIM := release
VA_ROOT          := $(call my-dir)
NDK_MODULE_PATH  := $(NDK_MODULE_PATH):$(VA_ROOT)
```
因为下载的ndk版本为20，可以修改APP_STL:=c++_static ,修改以后语法会错误。还是下载老版本更是在。



# couldn't find "*.so"
	在gradle.properties 文件增加
```
android.useDeprecatedNdk=true
```
	同级目录build.gradle中
```
android {
	defaultConfig {
		ndk {
			abiFilters "armeabi-v7a" , "x86" //, "armeabi"  按需设置
		}
	}
}
```

