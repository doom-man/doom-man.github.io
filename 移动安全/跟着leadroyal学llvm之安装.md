最近应要求做代码保护，在网上搜索相关资料，找到一位大佬做的文章在这里准备复现一遍，并在学习过程中加上自己的理解。
# llvm和clang 编译安装
clang 是gcc的替代和升级，llvm负责处理代码优化可以对中间代码进行操作。
## 环境：
ubuntu16 
cmake 3.18.0

## 源码安装

### 安装cmake

因为使用的是ubuntu16 cmake的版本太低，就用源码编译高版本的cmake。==>https://cmake.org/download/ 下载需要的版本

```
tar -xf cmake****
./bootstrap --prefix=/usr
make && make install 
```

中间可能遇到openssl相关的问题,通过以下命令可以解决。
```
sudo apt-get install libssl-dev
```
### 安装llvm

还是按照官网提供的方案进行安装

```
git clone https://github.com/llvm/llvm-project.git
cd llvm-project
mv clang llvm/tools/
mkdir build
cd build
cmake -G "Unix MakeFiles" -DCMAKE_BUILD_TYPE=Release ../llvm
make && make install 
```



# 编译、加载单独的Pass

## 编写CMakeLists.txt

```
cmake_minimum_required(VERSION 3.4)
# 检查环境变量
if(NOT DEFINED ENV{LLVM_HOME})
    message(FATAL_ERROR "$LLVM_HOME is not defined")
endif()
# 设置LLVM_DIR 环境变量这个目录要指向LLVMConfig.cmake
if(NOT DEFINED ENV{LLVM_DIR})
    set(ENV{LLVM_DIR} ENV{LLVM_HOME}/lib/cmake/llvm)
endif()
# 此处是一个链接************
find_package(LLVM REQUIRED CONFIG)
# 
add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})
# 加入自己的pass
add_subdirectory(skeleton)  # Use your pass name here.
```

## 加载so文件

使用clang加载so

```
$LLVM_HOME/bin/clang -Xclang -load -Xclang llvm-pass-tutorial/b/skeleton/libSkeletonPass.so -w test.c -o test.bin
```

出现错误
```
error: unable to load plugin 'llvm-pass-tutorial/b/skeleton/libSkeletonPass.so':
      'llvm-pass-tutorial/b/skeleton/libSkeletonPass.so: undefined symbol:
      _ZN4llvm23EnableABIBreakingChecksE'

```




> https://www.leadroyal.cn/?p=645 大佬原文
> https://www.jianshu.com/p/b08b338d0c62 clang和llvm解释
> https://releases.llvm.org/7.0.0/docs/GettingStarted.html 官方安装文档
>
> https://www.leadroyal.cn/?p=1014 解决_ZN4llvm23EnableABIBreakingChecksE