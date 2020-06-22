# Android 虚拟机简单介绍——ART、Dalvik、启动流程分析

## LLVM

全称是 Low Level Virtual Machine ,LLVM 框架如下所示：

![2176079-08f875927aa3c8ef](J:\gitproject\doom-man.github.io\res\pic\2176079-08f875927aa3c8ef.webp)

Frontend：负责分析源代码、检查错误，然后将源码编译成抽象语法树

Optimizer：通过多种优化手段来提高代码的运行效率，在一定程度上独立于具体的语言和目标平台

Backend：也被称为代码生成器，用于将前述的源码转化为目标前台的指令集



## Art 虚拟机整体框架

无论是 Dalvik 还是 Art，或者未来可能出现的新型虚拟机，它们提供的功能将全部封装在一个 so 库中，并且对外需要暴露 JNI_GetDefaultVMInitArgs、JNI_CreateVM 和 JNI_GetCreatedJavaVMs 三个接口，使用者（比如 Zygote）只需要按照统一的接口标准就可以控制和使用所有类型的虚拟机了.

## Android 虚拟机的典型启动流程

![2176079-81a4f79cb2c5987f](J:\gitproject\doom-man.github.io\res\pic\2176079-81a4f79cb2c5987f.webp)









# app_process

int main(int argc , char * const argv[]): [code link](https://android.googlesource.com/platform/frameworks/base/+/android-4.4.4_r2.0.1/cmds/app_process/app_main.cpp)

 1. 处理参数，将参数交给runtime

 2. runtime.start("com.android.internal.os.ZygoteInit", args, zygote);

runtime.start("com.android.internal.os.ZygoteInit", args, zygote)：[code link](https://android.googlesource.com/platform/frameworks/base/+/android-4.4.4_r2.0.1/core/jni/AndroidRuntime.cpp)

​	runtime 是一个AppRuntime 对象，调用AppRuntime.start函数。查看源码（frameworks\base\core\jni\AndroidRuntime.cpp）
​	1. 设置各种功能环境变量

 	2. startVm(&mJavaVM, &env, zygote, primary_zygote)   //启动虚拟机
 	3. onVmCreated(env);
 	4. startReg(env)
 	5. 调用参数中指定的类的main

AndroidRuntime::startVm (javaVM ** , JNIEnv ** , bool , bool) //同样的
	1. 参数解析
 	2. JNI_CreateJavaVM(pJavaVM, pEnv, &initArgs)函数里面需要设置pJavaVM, pEnv指针，是为了后续的销毁虚拟机等操作。

extern "C" jint JNI_CreateJavaVM(JavaVM** p_vm, JNIEnv** p_env, void* vm_args)
	1. 根据参数，填充了gDvm中的相关参数，关于gDvm:它的定义在Globals.h，其作用是保存许许多多的全局变量，在整个虚拟机中使用
	2. 初始化了JavaVMExt、JNIEnvExt等指针，这些分别对应的JNI中的JavaVM、JNIEnv，在JNI调用中必不可少。
	3. dvmStartup 继续启动，重点是这个
dvmStartup [codelink](https://android.googlesource.com/platform/dalvik/+/android-4.4.4_r1/vm/Init.cpp)


​	






> https://www.jianshu.com/p/75334b5058fa