# 简单的pass分析

## pass 实例

上一章节，配置好了clang 和llvm的环境，用了llvm-pass-tutorial来测试环境，这个章节参照官网的教程简单做个翻译。

GitHub：  https://github.com/banach-space/llvm-tutor 

课件地址： https://llvm.org/devmtg/2019-10/slides/Warzynski-WritingAnLLVMPass.pdf

用InjectFuncCall实例来分析pass  

```
//==============================================================================
// FILE:
//    InjectFuncCall.h
//
// DESCRIPTION:
//    Declares the InjectFuncCall pass for the new and the legacy pass managers.
//
// License: MIT
//==============================================================================
#ifndef LLVM_TUTOR_INSTRUMENT_BASIC_H
#define LLVM_TUTOR_INSTRUMENT_BASIC_H

#include "llvm/IR/PassManager.h"
#include "llvm/Pass.h"

//------------------------------------------------------------------------------
// New PM interface
//------------------------------------------------------------------------------
struct InjectFuncCall : public llvm::PassInfoMixin<InjectFuncCall> {
  llvm::PreservedAnalyses run(llvm::Module &M,
                              llvm::ModuleAnalysisManager &);
  bool runOnModule(llvm::Module &M);
};

//------------------------------------------------------------------------------
// Legacy PM interface
//------------------------------------------------------------------------------
struct LegacyInjectFuncCall : public llvm::ModulePass {
  static char ID;
  LegacyInjectFuncCall() : ModulePass(ID) {}
  bool runOnModule(llvm::Module &M) override;

  InjectFuncCall Impl;
};

#endif
```

头文件中提供了两种接口，legacy 和 new ，先分析new pm manager 继承模板类llvm::PassInfoMixin<InjectFuncCall> ，其中两个成员函数 。run 和runOnModule 。

```
//========================================================================
// FILE:
//    InjectFuncCall.cpp
//
// DESCRIPTION:
//    For each function defined in the input IR module, InjectFuncCall inserts
//    a call to printf (from the C standard I/O library). The injected IR code
//    corresponds to the following function call in ANSI C:
//    ```C
//      printf("(llvm-tutor) Hello from: %s\n(llvm-tutor)   number of arguments: %d\n",
//             FuncName, FuncNumArgs);
//    ```
//    This code is inserted at the beginning of each function, i.e. before any
//    other instruction is executed.
//
//    To illustrate, for `void foo(int a, int b, int c)`, the code added by InjectFuncCall
//    will generated the following output at runtime:
//    ```
//    (llvm-tutor) Hello World from: foo
//    (llvm-tutor)   number of arguments: 3
//    ```
//
// USAGE:
//    1. Legacy pass manager:
//      $ opt -load <BUILD_DIR>/lib/libInjectFuncCall.so `\`
//        --legacy-inject-func-call <bitcode-file>
//    2. New pass maanger:
//      $ opt -load-pass-plugin <BUILD_DIR>/lib/libInjectFunctCall.so `\`
//        -passes=-"inject-func-call" <bitcode-file>
//
// License: MIT
//========================================================================
#include "InjectFuncCall.h"

#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"

using namespace llvm;

#define DEBUG_TYPE "inject-func-call"

//-----------------------------------------------------------------------------
// InjectFuncCall implementation
//-----------------------------------------------------------------------------
bool InjectFuncCall::runOnModule(Module &M) {
  bool InsertedAtLeastOnePrintf = false;
  //获取llvmContext
  auto &CTX = M.getContext();
  //参数类型
  PointerType *PrintfArgTy = PointerType::getUnqual(Type::getInt8Ty(CTX));

  // STEP 1: Inject the declaration of printf
  // ----------------------------------------
  // Create (or _get_ in cases where it's already available) the following
  // declaration in the IR module:
  //    declare i32 @printf(i8*, ...)
  // It corresponds to the following C declaration:
  //    int printf(char *, ...)
  //函数类型
  FunctionType *PrintfTy = FunctionType::get(
      IntegerType::getInt32Ty(CTX),
      PrintfArgTy,
      /*IsVarArgs=*/true);
  //查询或创建printf的函数定义 ， PrintfTy 为函数类型包括返回值类型、参数个数和类型。
  FunctionCallee Printf = M.getOrInsertFunction("printf", PrintfTy);
  
  // Set attributes as per inferLibFuncAttributes in BuildLibCalls.cpp
  //转换为一个函数。
  Function *PrintfF = dyn_cast<Function>(Printf.getCallee());
  errs()<<PrintfF.getCallee()<<"\n";
  PrintfF->setDoesNotThrow();
  PrintfF->addParamAttr(0, Attribute::NoCapture);
  PrintfF->addParamAttr(0, Attribute::ReadOnly);


  // STEP 2: Inject a global variable that will hold the printf format string
  // ------------------------------------------------------------------------
  //声明一个字符串
  llvm::Constant *PrintfFormatStr = llvm::ConstantDataArray::getString(
      CTX, "(llvm-tutor) Hello from11: %s\n(llvm-tutor)   number of arguments: %d\n");
  //创建字符串
  Constant *PrintfFormatStrVar =
      M.getOrInsertGlobal("PrintfFormatStr", PrintfFormatStr->getType());
  /*这段注释了会提示
  LVM ERROR: Program used external function 'PrintfFormatStr' which could not be resolved!
    */
  dyn_cast<GlobalVariable>(PrintfFormatStrVar)->setInitializer(PrintfFormatStr);

  // STEP 3: For each function in the module, inject a call to printf
  // ----------------------------------------------------------------
  for (auto &F : M) {
    //用来区分是否为引用函数。
    if (F.isDeclaration())
      continue;

    // Get an IR builder. Sets the insertion point to the top of the function
    IRBuilder<> Builder(&*F.getEntryBlock().getFirstInsertionPt());

    // Inject a global variable that contains the function name
    auto FuncName = Builder.CreateGlobalStringPtr(F.getName());

    // Printf requires i8*, but PrintfFormatStrVar is an array: [n x i8]. Add
    // a cast: [n x i8] -> i8*
    // 创建指向PrintfFormatStrVar 参数值 PrintfArgTy 参数类型的指针。 第三个参数似乎是可选参数，删除后不影响操作。
    llvm::Value *FormatStrPtr =
        Builder.CreatePointerCast(PrintfFormatStrVar, PrintfArgTy, "formatStr");

    // The following is visible only if you pass -debug on the command line
    // *and* you have an assert build.
    LLVM_DEBUG(dbgs() << " Injecting call to printf inside " << F.getName()
                      << "\n");

    // 这段代码比较明显，创建一个函数调用，结合参数了解到创建函数调用我们需要调用的函数和函数参数。
    Builder.CreateCall(
        Printf, {FormatStrPtr, FuncName, Builder.getInt32(F.arg_size())});

    InsertedAtLeastOnePrintf = true;
  }

  return InsertedAtLeastOnePrintf;
}

PreservedAnalyses InjectFuncCall::run(llvm::Module &M,
                                       llvm::ModuleAnalysisManager &) {
  bool Changed =  runOnModule(M);

  return (Changed ? llvm::PreservedAnalyses::none()
                  : llvm::PreservedAnalyses::all());
}

bool LegacyInjectFuncCall::runOnModule(llvm::Module &M) {
  bool Changed = Impl.runOnModule(M);

  return Changed;
}

//-----------------------------------------------------------------------------
// New PM Registration
//-----------------------------------------------------------------------------
llvm::PassPluginLibraryInfo getInjectFuncCallPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "inject-func-call", LLVM_VERSION_STRING,
          [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                  if (Name == "inject-func-call") {
                    MPM.addPass(InjectFuncCall());
                    return true;
                  }
                  return false;
                });
          }};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getInjectFuncCallPluginInfo();
}

//-----------------------------------------------------------------------------
// Legacy PM Registration
//-----------------------------------------------------------------------------
char LegacyInjectFuncCall::ID = 0;

// Register the pass - required for (among others) opt
static RegisterPass<LegacyInjectFuncCall>
    X(/*PassArg=*/"legacy-inject-func-call", /*Name=*/"LegacyInjectFuncCall",
      /*CFGOnly=*/false, /*is_analysis=*/false);

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

测试目标test.c

```
#include <stdio.h>
#include <stdlib.h>
int FuncCall(int a , int b ){
	printf("this is a FuncCall \n");
	return a+b;
}
int main(void){
	printf("hello world\n");
	FuncCall(1,2);
	return 0;
}
```

编译成中间llvm binary code文件

```
clang -O3 -emit-llvm test.c -c -o test.bc
```

opt 是llvm的一个模块，llvm的源文件作为输入，使用特定的优化和分析，输出优化后的文件或者分析结果。

```
pareto@ubuntu:~/llvm-tutor/build$ $LLVM_DIR/bin/opt -load-pass-plugin ./lib/libInjectFuncCall.so -passes=inject-func-call ./test.bc -f -o test.ll -debugify
 Injecting call to printf inside FuncCall
 Injecting call to printf inside main
```

运行的结果

```
(llvm-tutor) Hello from: main
(llvm-tutor)   number of arguments: 0
hello world
(llvm-tutor) Hello from: FuncCall
(llvm-tutor)   number of arguments: 2
this is a FuncCall 
```

产生的文件为llvm 字节码，可以通过llc编译成汇编代码。



# 改良目标的实例

我们也需要函数开头增加函数调用，但是是我们自己的内联汇编函数。有公司的混淆方案就不具体展示了。

```
//========================================================================
// FILE:
//    InjectFuncCall.cpp
//
// DESCRIPTION:
//    For each function defined in the input IR module, InjectFuncCall inserts
//    a call to printf (from the C standard I/O library). The injected IR code
//    corresponds to the following function call in ANSI C:
//    ```C
//      printf("(llvm-tutor) Hello from: %s\n(llvm-tutor)   number of arguments: %d\n",
//             FuncName, FuncNumArgs);
//    ```
//    This code is inserted at the beginning of each function, i.e. before any
//    other instruction is executed.
//
//    To illustrate, for `void foo(int a, int b, int c)`, the code added by InjectFuncCall
//    will generated the following output at runtime:
//    ```
//    (llvm-tutor) Hello World from: foo
//    (llvm-tutor)   number of arguments: 3
//    ```
//
// USAGE:
//    1. Legacy pass manager:
//      $ opt -load <BUILD_DIR>/lib/libInjectFuncCall.so `\`
//        --legacy-inject-func-call <bitcode-file>
//    2. New pass maanger:
//      $ opt -load-pass-plugin <BUILD_DIR>/lib/libInjectFunctCall.so `\`
//        -passes=-"inject-func-call" <bitcode-file>
//
// License: MIT
//========================================================================
#include "InjectFuncCall.h"
#include "llvm/IR/InlineAsm.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"

using namespace llvm;

#define DEBUG_TYPE "inject-func-call"

//-----------------------------------------------------------------------------
// InjectFuncCall implementation
//-----------------------------------------------------------------------------
bool InjectFuncCall::runOnModule(Module &M) {
  bool InsertedAtLeastOnePrintf = false;

  auto &CTX = M.getContext();
  PointerType *PrintfArgTy = PointerType::getUnqual(Type::getInt8Ty(CTX));

  // STEP 1: Inject the declaration of printf
  // ----------------------------------------
  // Create (or _get_ in cases where it's already available) the following
  // declaration in the IR module:
  //    declare i32 @printf(i8*, ...)
  // It corresponds to the following C declaration:
  //    int printf(char *, ...)
  FunctionType *PrintfTy = FunctionType::get(
      IntegerType::getInt32Ty(CTX),
      PrintfArgTy,
      /*IsVarArgs=*/true);

  FunctionCallee Printf = M.getOrInsertFunction("printf", PrintfTy);

  // Set attributes as per inferLibFuncAttributes in BuildLibCalls.cpp
  Function *PrintfF = dyn_cast<Function>(Printf.getCallee());

  PrintfF->setDoesNotThrow();
  PrintfF->addParamAttr(0, Attribute::NoCapture);
  PrintfF->addParamAttr(0, Attribute::ReadOnly);


  // STEP 2: Inject a global variable that will hold the printf format string
  // ------------------------------------------------------------------------
  llvm::Constant *PrintfFormatStr = llvm::ConstantDataArray::getString(
      CTX, "(llvm-tutor) 112Hello from: %s\n(llvm-tutor)   number of arguments: %d\n");

  Constant *PrintfFormatStrVar =
      M.getOrInsertGlobal("PrintfFormatStr", PrintfFormatStr->getType());
  dyn_cast<GlobalVariable>(PrintfFormatStrVar)->setInitializer(PrintfFormatStr);

  // STEP 3: For each function in the module, inject a call to printf
  // ----------------------------------------------------------------
  for (auto &F : M) {
    errs() << "isDeclaration " << F.isDeclaration() <<"  Function Name "<< F.getName() << "\n";
    if (F.isDeclaration())
      continue;
    // Get an IR builder. Sets the insertion point to the top of the function
    IRBuilder<> Builder(&*F.getEntryBlock().getFirstInsertionPt());

    errs() << " Injecting call to printf inside " << F.getName() << "\n";
    Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "pushq %rax", "", true));
    Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "movq %rsp ,%rax", "", true));
    Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "addq $$0xff0 , %rsp", "", true));
    Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "movq %rax , %rsp", "", true));
    Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "popq %rax", "", true));


    InsertedAtLeastOnePrintf = true;
  }

  return InsertedAtLeastOnePrintf;
}

PreservedAnalyses InjectFuncCall::run(llvm::Module &M,
                                       llvm::ModuleAnalysisManager &) {
  bool Changed =  runOnModule(M);

  return (Changed ? llvm::PreservedAnalyses::none()
                  : llvm::PreservedAnalyses::all());
}

bool LegacyInjectFuncCall::runOnModule(llvm::Module &M) {
  bool Changed = Impl.runOnModule(M);

  return Changed;
}

//-----------------------------------------------------------------------------
// New PM Registration
//-----------------------------------------------------------------------------
llvm::PassPluginLibraryInfo getInjectFuncCallPluginInfo() {
  return {LLVM_PLUGIN_API_VERSION, "inject-func-call", LLVM_VERSION_STRING,
          [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager &MPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                  if (Name == "inject-func-call") {
                    MPM.addPass(InjectFuncCall());
                    return true;
                  }
                  return false;
                });
          }};
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getInjectFuncCallPluginInfo();
}

//-----------------------------------------------------------------------------
// Legacy PM Registration
//-----------------------------------------------------------------------------
char LegacyInjectFuncCall::ID = 0;

// Register the pass - required for (among others) opt
static RegisterPass<LegacyInjectFuncCall>
    X(/*PassArg=*/"legacy-inject-func-call", /*Name=*/"LegacyInjectFuncCall",
      /*CFGOnly=*/false, /*is_analysis=*/false);

```





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



经过两天的学习，了解一些中间语言语法，再看helloworld 的IR语句。

```
; ModuleID = 'a.c'
source_filename = "a.c"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"
; 3个全局变量 两个字符串和一个函数。
@.str = private unnamed_addr constant [13 x i8] c"Hello World\0A\00", align 1
@.str.1 = private unnamed_addr constant [13 x i8] c"World Hello\0A\00", align 1
; 定义函数 ：dso_local 表示将解析为同一链接单元中的符号，i32 返回值， #0 表示属性组，具体的值在下面。
define dso_local i32 @main() #0 {
; alloca 在栈中分配32位空间按 4bit 对齐。
  %1 = alloca i32, align 4
；%1 = 0
  store i32 0, i32* %1, align 4
； 调用printf ， i32 表示返回值， (i8* ,...) 表示参数为char *且参数个数不定，其中"i8* getelementptr inbounds ([13 x i8], [13 x i8]* @.str, i32 0, i32 0)",i8 * 为返回值, getelementptr inbounds 表示获取@.str 的地址，主要说后两个参数表示索引，第一个为间接索引，第二个为直接索引。其中详见https://llvm.org/docs/LangRef.html#getelementptr-instruction 。
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
> https://llvm.org/docs/LangRef.html  IR 指令reference
>
> https://blog.csdn.net/rikeyone/article/details/100020145 clang 编译命令
>
> https://releases.llvm.org/2.2/docs/tutorial/JITTutorial1.html  getOrInsertFunction的使用。

