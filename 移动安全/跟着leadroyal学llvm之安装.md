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
mkdir build
cd build
cmake -G "Unix MakeFiles" -DCMAKE_BUILD_TYPE=Release ../llvm

```



使用源码来编译安装 https://releases.llvm.org/download.html#7.0.0 ， 下载llvm 和 clang，下载完成后两个文件llvm-7.0.0.src.tar.xz  和 cfe-7.0.0.src.tar.xz   解压并将clang移动到llvm的tools目录下

```
tar -xf llvm-7.0.0.src.tar.xz
tar -xf cfe-7.0.0.src.tar.xz
mv cfe-7.0.0.src.tar.xz clang
mv clang ./llvm-7.0.0.src.tar.xz/tools
```
参照leadroyal的安装方法
```
mkdir b
cd b
cmake ../llvm-7.0.0.src.tar.xz
cmake --build . -- -j4
```
这是debug版本编译过程可能出memory exhausted 等错误，表示内存不足。debug版本打开需要50g左右空间，没办法换成release 版本。
```
cmake llvm-7.0.0.src DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_ASSERTIONS=ON
cmake --build . --target install 
```
这里按照leadroyal安装我出了问题 ，选择了官方的安装方法。这里安装好以后与大佬原文有出入，安装后的可执行文件不在.../i/bin目录下而在..../b/bin下了。
设置环境变量
```
export LLVM_HOME=`pwd`/b
```
测试一下,是目标目录就成功了

```
ls $LLVM_HOME 
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
$LLVM_HOME/bin/clang -I//home/pareto/llvm-7.0.0.src/include -Xclang -load -Xclang llvm-pass-tutorial/b/skeleton/libSkeletonPass.so -w test.c -o test.bin
```

出现错误
```
//home/pareto/llvm-7.0.0.src/include/llvm/Support/Compiler.h:20:10: fatal error: 'new' file not found
```




> https://www.leadroyal.cn/?p=645 大佬原文
> https://www.jianshu.com/p/b08b338d0c62 clang和llvm解释
> https://releases.llvm.org/7.0.0/docs/GettingStarted.html 官方安装文档