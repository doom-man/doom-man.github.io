最近应要求做代码保护，在网上搜索相关资料，找到一位大佬做的文章在这里准备复现一遍，并在学习过程中加上自己的理解。
# llvm和clang 编译安装
clang 是gcc的替代和升级，llvm负责处理代码优化可以对中间代码进行操作。
## 环境：
ubuntu16 
cmake 3.10.2
## 源码安装
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
# 编译、加载单独的Pass

> https://www.leadroyal.cn/?p=645 大佬原文
> https://www.jianshu.com/p/b08b338d0c62 clang和llvm解释
> https://releases.llvm.org/7.0.0/docs/GettingStarted.html 官方安装文档[/md]