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

这个类提供给哪些不用运行、不用改变状态并且不会更新的pass。这不是转化或分析的常规类型，但是可以提供当前编译配置信息。ImmutablePass 永远不会被无效，也不会无效其他类。

### The ModulePass class

ModulePass 类是所有父类中你可以使用的最通用的类，继承ModulePass 意味着你的pass将整个程序作为单元（而不是随机顺序的函数）或者增加删除删除。因为不知道ModulePass子类的行为，没有优化可以执行过程中完成。

modulepass 可以通过 getAnalysis接口getAnalysis<DominatorTree>(llvm::Function *)函数检索分析结果来使用function level passes。
#### runOnModule 方法

```
virtual bool runOnModule(Module &M) = 0;
```

如果模块被修改返回true，否则false。

### CallGraphSCCPass类

CallGraphSCCPass 可以被用来遍历程序上下文(被调用者调用之前调用)。



## IR 语法

*怎么说看，看完官方给的文档还是云里雾里，用了leadroyal的pass，但是没有他展示的效果，如果还是先学习llvm的IR语法， BasicBlock ，GlobalVariable ，IRBuilder<> ，Function ，AllocaInst  的功能是什么 ？ 带着疑问去学习。*

```
#include <stdio.h>
int main(void){
        printf("Hello World\n");
        printf("World Hello\n");
        return 0;
}           
```
仅预处理和编译，生成中间文件IR。
clang a.c -emit-llvm -S -o a.ll  

```
; ModuleID = 'a.c'
source_filename = "a.c"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"
; 全局变量
@.str = private unnamed_addr constant [13 x i8] c"Hello World\0A\00", align 1
@.str.1 = private unnamed_addr constant [13 x i8] c"World Hello\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  %2 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @.str, i32 0, i32 0))
  %3 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @.str.1, i32 0, i32 0))
  ret i32 0
}

declare dso_local i32 @printf(i8*, ...) #1

attributes #0 = { noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }

; 元数据
!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"clang version 8.0.0 (tags/RELEASE_800/final) (https://github.com/HikariObfuscator/Hikari.git ecdf30fa1a4635a76c3b528a41eb48d791f4be95)"}
```

## 标识符

LLVM标识符有两种基本类型：全局和局部。 全局标识符(函数和全局变量)以"@"开头。局部标识符(寄存器名称，类型)以"%"开头。另外，有三种不同格式的标识符，对于不同的目的。

	1. 已命名的值以带有前缀的名称展示。@foo ,@a.really.long.identifier 以上面代码为例的话有@printf ，@main 。实际的正则表达式用的是‘`[%@][-a-zA-Z$._][-a-zA-Z$._0-9]*`’
 	2. 未命名的值以无符号整形前缀来表示  ，例如，%12 ，@2
 	3. 常量，在常量节区下定义

LLVM要求值要有前缀的原因有两个：编译器不需要担心保留字的名称冲突，并且将来拓展保留字集合不会带来任何损失。另外，未命令的标识符允许编译器很快的提出一个临时变量不需要避免符号冲突。

LLVM的保留字和其他语言的保留字很相似。有一些关键对于不同的操作码('add','bitcast', 'ret' ,etc...) , 对于原始类型名称(‘void’, ‘i32’, etc…) 。这些保留字不会和变量名称冲突，因为他们不会带有% 或 @ 前缀。

有个LLVM的代码的例子，来计算整形值 ’%x' 乘以 8：

The easy way:

```
%result = mul i32 %x , 8
```

降低点运算强度

```
%result = shl i32 %x , 3
```

And the hard way :

```
%0 = add i32 %x , %x	; yields i32:%0
%1 = add i32 $0 , %0	; yields i32:%1
%result = add i32 %1 , %1
```

最后一中%x 乘 8 的方法 阐述了几个LLVM 重要的词法分析的特征：

	1. 注释从；开始到一行结束
 	2. 未命令的临时变量在计算结果没有被分配给已命名值 时创建。
 	3. 未命名的变量是顺序的从零开始。注意基础块和未命名函数参数也是这个规律。例如，如果在一个没有给出标签的基础块中所有的函数参数都被命名了，那么就会得到标签0。

# 高等级结构

## 模块结构

LLVM 由模块构成，每个模块都是输入程序的传输单元。每个模块有函数，全局值和符号表记录。 模块可能被LLVM linker组和到一起，LLVM连接器来合并函数、定义、解析之前的定义和合并符号表记录。以一个"hello world"模块为例子：（这个代码和我们前面编译出来的中间代码很像）

```
; Declare the string constant as a global constant.
@.str = private unnamed_addr constant [13 x i8] c"hello world\0A\00"

; External declaration of the puts function
declare i32 @puts(i8* nocapture) nounwind

; Definition of main function
define i32 @main() {   ; i32()*
  ; Convert [13 x i8]* to i8*...
  %cast210 = getelementptr [13 x i8], [13 x i8]* @.str, i64 0, i64 0

  ; Call puts function to write out the string to stdout.
  call i32 @puts(i8* %cast210)
  ret i32 0
}

; Named metadata
!0 = !{i32 42, null, !"string"}
!foo = !{!0}
```

例子中有一个全局值".str" ,一个外部定义的函数puts ，和一个函数定义main 和一个已命名的元数据"foo" 。

通常，一个模块由一系列的全局值（包括函数和全局变量）。 全局值通过一个指向内存地址的指针来表示，在这个例子中是一个指向字符数组的指针和一个指向函数的指针，并且有下述linkage_types 中的其中一种。

## LinKage Types

所有的全局变量和函数都有以下链接属性的一种：(列举了一些常见的，更多的看官方文档)

private

​	表示仅能被当前模块的对象访问。特别是，链接带有private 全局值的代码到一个模块可能造成私有符号被重命名来避免碰撞。因为符号对于模块是私有的，所有的引用都要更新。

internal 

​	和private相似，但是在对象文件中之是以一个局部符号显示(在elf文件中是STB_LOCAl)。对应C语言的关键字'static'

available_externally

​	这个标识了的全局值永远都不会出现在对应的LLVM模块的对象文件(????)。从链接器的角度来看，available_externally 全局值 和外部定义是等价的。他们的存在是当在模块外已知全局值的定义时允许内联和其他优化发生。

linkonce 

​	linkonce 的全局值会在链接发生时和其他同名的全局值合并。这可以用来实现一些内联函数，模板或者一些在使用它的传输单元中产生，但是之后可能被一个更具体的定义覆盖。没有被引用的linkonce 全局值可以被丢弃。注意linkonce 全局值实际上不允许函数体内联到调用者，因为不知道函数的定义会不会被其他更强的定义覆盖。为了允许内联和其他优化，使用"linkonce_odr"。

weak

​	weak 和linkonce 有同样的合并语义，除了未被引用的weak全局值可能不会被丢弃。这是给C语言源代码中被定义未weak的全局值使用。

common

​	common  和 weak 相似，有点像C语言中全局范围的"int X;"。common 和weak有同样的合并语义兵器也不会在未被引用是删除。common 符号可能没有显式部分，必须具有零初始值设定项，并且可能未标记为“常量”。 函数和别名可能没有 common 声明。

external

​	如果其他标识符都没有被使用，全局值就是外部可见的，意味着它可以参与到链接过程，并且被用来解析外部符号引用。



# 全局值

全局变量定义必须被初始化。

全局变量在其他传输单元也可以被定义，但是不需要初始化。

全局变量可以可选的指定为linkage类型。

全局变量定义或声明放置在一个明确的节区，并且可以指定显式的对齐方式。对于变量定义来如果显示或推断的节区信息和它的定义不匹配那么行为的结果是未定义的。

可以定位全局变量为const ，我感觉和C语言一模一样。

全局变量可以被unnamed_addr 标记表示地址不重要，只关心内容。这样标记的常量可以被合并到其他常量如果他们初始化的值一样。


> https://llvm.org/docs/WritingAnLLVMPass.html#writing-an-llvm-pass-looppass 官方提供的pass教程
>
> https://blog.csdn.net/rikeyone/article/details/100020145 clang 编译命令

