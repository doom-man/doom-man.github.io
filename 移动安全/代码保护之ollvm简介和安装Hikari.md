# ollvm简介和hikari安装

# ollvm

就是利用llvm框架来实现的一种混淆技术，原理。。。就后面再慢慢看吧。

## hikari安装

hikari 应该就可以算是ollvm的一种，根据官网安装方法简单快捷。

```
git clone --recursive -b release_80 https://github.com/HikariObfuscator/Hikari.git Hikari && cd Hikari && git submodule update --remote --recursive && cd ../ && mkdir Build && cd Build && cmake -G "Ninja" -DCMAKE_BUILD_TYPE=MinSizeRel -DLLVM_APPEND_VC_REV=on ../Hikari && ninja && ninja install && git clone https://github.com/HikariObfuscator/Resources.git ~/Hikari
```

# 接入NDK

```
# HikariOut 是编译输出目录
cp $HikariOut/bin/clang        toolchains/llvm/prebuilt/linux-x86_64/bin/clang
cp $HikariOut/bin/clang++      toolchains/llvm/prebuilt/linux-x86_64/bin/clang++
cp $HikariOut/bin/clang-format toolchains/llvm/prebuilt/linux-x86_64/bin/clang-format

# Hikari 是源码目录
cp $Hikari/tools/clang/lib/Headers/__stddef_max_align_t.h sysroot/usr/include/
cp $Hikari/tools/clang/lib/Headers/stddef.h sysroot/usr/include/
cp $Hikari/tools/clang/lib/Headers/stdbool.h sysroot/usr/include/
cp $Hikari/tools/clang/lib/Headers/stdarg.h sysroot/usr/include/
cp $Hikari/tools/clang/lib/Headers/float.h sysroot/usr/include/
```

然后就可以使用ndk来编译你要用来混淆的项目了。 



> https://github.com/HikariObfuscator/Hikari github hikari官网
>
> https://api-caller.com/2019/03/30/hikari/   整合到NDK

