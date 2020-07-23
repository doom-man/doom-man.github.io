最近应要求做代码保护，在网上搜索相关资料，找到一位大佬做的文章在这里准备复现一遍，并在学习过程中加上自己的理解。
# llvm和clang 编译安装
clang 是gcc的替代和升级，llvm负责处理代码优化可以对中间代码进行操作。
## 环境：
ubuntu18
cmake 3.18.0

## 源码安装

### 安装cmake

 cmake的版本太低，就用源码编译高版本的cmake。==>https://cmake.org/download/ 下载需要的版本

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

还是按照官网提供的方案进行安装，官网也提供了免编译下载解压以后可以直接使用的包，建议下载下来直接使用，源码编译还是踩了不少坑。

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
cmake_minimum_required(VERSION 3.1)
project(Skeleton)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)


find_package(LLVM REQUIRED CONFIG)
add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})


add_subdirectory(skeleton)  # Use your pass name here.

set_target_properties(SkeletonPass PROPERTIES COMPILE_FLAGS "-D__GLIBCXX_USE_CXX11_ABI=0 -fno-rtti" )
```

## 编译，加载so文件

使用clang 或clang++编译Skeleton.c

```
mkdir build
cd build
cmake -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_CC_COMPILER=clang -DCMAKE_EXPORT_COMPILE_COMMANDS=1 ​​ ..
make 
```

测试代码new.cc
```
#include <new>
#include <iostream>
using namespace std;
int main(void){
	cout << "123" <<endl;
	return 0;
}

```

加载so ,看命令行就可以看出各文件指向关系。

```
clang++ -Xclang -load -Xclang ~/Templates/llvm-pass-tutorial/b/skeleton/libSkeletonPass.* ~/Templates/new.cc 
```

我的结果是这样 ，应该是成功了的。

```
I saw a function called __cxx_global_var_init!
I saw a function called main!
I saw a function called _GLOBAL__sub_I_new.cc!
```






> https://www.leadroyal.cn/?p=645 大佬原文
> https://www.jianshu.com/p/b08b338d0c62 clang和llvm解释
> https://releases.llvm.org/7.0.0/docs/GettingStarted.html 官方安装文档
>
> https://www.leadroyal.cn/?p=1014 解决_ZN4llvm23EnableABIBreakingChecksE
>
> https://quentinmayo.com/2019/12/17/1-getting-started-by-building-llvm-from-source-late-2019-edition/ 
>
> https://llvm.org/docs/WritingAnLLVMPass.html#writing-an-llvm-pass-looppass 官方提供的pass教程