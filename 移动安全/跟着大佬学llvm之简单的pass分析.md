# 简单的pass分析

## pass 实例

上一章节，配置好了clang 和llvm的环境，用了llvm-pass-tutorial来测试环境，这个章节参照官网的教程简单做个翻译。

创建一个目录hello-pass,进入目录编写CMakeFiles.txt,官方提供的cmkaelists.txt 没有跑起来，参照llvm-pass-tutorial来改makelists

```
# If we don't need RTTI or EH, there's no reason to export anything
# from the hello plugin.
cmake_minimum_required(VERSION 3.18)
project(hellollvm)


set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)


find_package(LLVM REQUIRED CONFIG)
add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})


add_library(hellollvm MODULE
    # List your source files here.
    hello.cpp
)
set_target_properties(hellollvm PROPERTIES COMPILE_FLAGS "-D__GLIBCXX_USE_CXX11_ABI=0 -fno-rtti" )
target_compile_features(hellollvm PRIVATE cxx_range_for cxx_auto_type) 
```
最后一句不要会报错。

```
error: unable to load plugin '/home/pareto/Templates/hello-pass/b/libhellollvm.so': '/home/pareto/Templates/hello-pass/b/libhellollvm.so: undefined symbol: _ZTIN4llvm12FunctionPassE'
```

创建hello.cpp,代码如下


```
//必须的头文件
#include "llvm/ADT/Statistic.h"
#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"
//声明要用的命名空间
using namespace llvm;

#define DEBUG_TYPE "hello"

STATISTIC(HelloCounter, "Counts number of functions greeted");
// 声明一个匿名空间仅对当前文件有效。
namespace {

  struct Hello : public FunctionPass {
    static char ID; 
    Hello() : FunctionPass(ID) {}//每个函数都会调用一次
	//重载FunctionPass的抽象函数，
    bool runOnFunction(Function &F) override {
      ++HelloCounter;
      errs() << "Hello: ";
      errs().write_escaped(F.getName()) << '\n';
      return false;
    }
  };
}
//初始化pass id，但是llvm用id的地址来确定pass，所以初始化不重要。。。。官网给的说法。
char Hello::ID = 0;
//注册我们的类，
static RegisterPass<Hello> X("hello", "Hello World Pass");

namespace {
  // Hello2 - The second implementation with getAnalysisUsage implemented.
  //定义一个FunctionPass的子类
  struct Hello2 : public FunctionPass {
    static char ID; // Pass identification, replacement for typeid
    Hello2() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
      ++HelloCounter;
      errs() << "Hello: ";
      errs().write_escaped(F.getName()) << '\n';
      return false;
    }

    // We don't modify the program, so we preserve all analyses.
    void getAnalysisUsage(AnalysisUsage &AU) const override {
    //保留所有分析???看到后面应该就晓得什么意思
      AU.setPreservesAll();
    }
  };
}

char Hello2::ID = 0;
static RegisterPass<Hello2> Y("hello2", "Hello World Pass (with getAnalysisUsage implemented)");

```

测试目标helloworld.c

```
#include <iostream>
using namespace std;
int main(void){
        printf("hello world printf \n");
        cout << "hello world cout" << endl;
        return 0;
}
```

编译成中间二进制文件

```
clang -O3 -emit-llvm helloworld.c -c -o helloworld.bc
```

opt 是llvm的一个模块，llvm的源文件作为输入，使用特定的优化和分析，输出优化后的文件或者分析结果。

```
opt -load lib/LLVMHello.so -hello < hello.bc > /dev/null
```

展示的结果

```
Hello: main
Hello: _GLOBAL__sub_I_helloworld.cpp
```

嗯。。。。。不太懂这个输出表达的意思，"hello:main"可以理解进入了一次函数调用了一次runonfunction ，但是"hello: _GLOBAL__sub_I_helloworld.cpp"是为什么呢。留个疑问。

## 介绍几种类和方法

### ImmutablePass 类







> https://llvm.org/docs/WritingAnLLVMPass.html#writing-an-llvm-pass-looppass 官方提供的pass教程
>
> https://blog.csdn.net/rikeyone/article/details/100020145 clang 编译命令

