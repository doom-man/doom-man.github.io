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

然后就可以使用ndk来编译你要用来混淆的项目了， 简单的HelloWorld ，使用字符串加密方案，-mllvm -enable-strcry 。 

```
#include <stdio.h>
#include <unistd.h>

int main(void){
        int a = 0;
        printf("Hello world %d \n",a);
        return 0;
}
```

放到IDA，发现特征比较明显， 运行时检查解密标志，一段内存存加密字符串通过异或运算解密到解密字符串区域。

```
int __cdecl main(int argc, const char **argv, const char **envp)
{
  __int64 v4; // [rsp+0h] [rbp-10h]

  if ( !_TMC_END__ )
  {
    format = byte_601030 ^ 0x77;
    byte_601051 = byte_601031 ^ 0x9E;
    byte_601052 = byte_601032 ^ 0x95;
    byte_601053 = byte_601033 ^ 0x94;
    byte_601054 = byte_601034 ^ 0x4B;
    byte_601055 = byte_601035 ^ 0xEE;
    byte_601056 = byte_601036 ^ 0x42;
    byte_601057 = byte_601037 ^ 0x55;
    byte_601058 = byte_601038 ^ 0xF0;
    byte_601059 = byte_601039 ^ 0xB3;
    byte_60105A = byte_60103A ^ 0x55;
    byte_60105B = byte_60103B ^ 0xC7;
    byte_60105C = byte_60103C ^ 0x62;
    byte_60105D = byte_60103D ^ 0xA;
    byte_60105E = byte_60103E ^ 0xAE;
    byte_60105F = byte_60103F ^ 0x26;
    byte_601060 = byte_601040 ^ 0x60;
  }
  _TMC_END__ = 1;
  *((_DWORD *)&v4 - 4) = 0;
  *((_DWORD *)&v4 - 4) = 0;
  printf(&format, *((unsigned int *)&v4 - 4), envp);
  return 0;
}
```

可以尝试做一手破解。

> https://github.com/HikariObfuscator/Hikari github hikari官网
>
> https://api-caller.com/2019/03/30/hikari/   整合到NDK

