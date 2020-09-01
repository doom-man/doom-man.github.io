[TOC]

# 集成自定义pass到Hikari

1. 在include/llvm/Transforms/Obfuscation/Obfuscation.h 添加目标pass的头文件。

```
#ifndef _JUST_TEST_H_
#define _JUST_TEST_H_
#include "llvm/Pass.h"
#include "llvm/IR/LegacyPassManager.h"
using namespace std;
using namespace llvm;

// Namespace
namespace llvm {
	FunctionPass* createJustTestPass();
	FunctionPass* createJustTestPass(bool flag);
	bool doInitialization(Module &M) ;
	void initializeJustTestPass(PassRegistry &Registry);
}
#endif
```



2. 在include/llvm/Transforms/Obfuscation/Obfuscation.h 添加以下代码，表示注册选项的名称。

```
static cl::opt<bool>
    EnableFunctionWrapper("enable-test", cl::init(false), cl::NotHidden,
                          cl::desc("Enable Function Test."));
```

3. 添加lib/Transforms/Obfuscation/JustTest.cpp代码。

```
#include "llvm/Transforms/Obfuscation/Obfuscation.h"
#include "llvm/Transforms/Obfuscation/JustTest.h"

#include <iostream>
#define DEBUG_TYPE "hello"

using namespace llvm;

namespace llvm{
  // Hello - The first implementation, without getAnalysisUsage.
  struct JustTest : public FunctionPass {
    static char ID; // Pass identification, replacement for typeid
    bool flag;
    int targetFlag;
    JustTest() : FunctionPass(ID) { this->flag = true; }
    JustTest(bool flag) : FunctionPass(ID){ this->flag = flag;}
    StringRef getPassName() const override {
      return StringRef("JustTest");
    }   
    bool runOnFunction(Function &F) override {
      errs() << "Hello JustTest: ";
      errs().write_escaped(F.getName()) << '\n';   
      IRBuilder<> Builder(&*F.getEntryBlock().getFirstInsertionPt());   
      if(targetFlag == 1){
        errs() << "x86 target indenpended\n";
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "push %eax", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "mov %esp ,%eax", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "add $$0xff0 , %esp", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "mov %eax , %esp", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "pop %eax", "", true));
      } 
      else if(targetFlag == 2)
      {
        errs() << "Arm target indenpended\n";
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "STMFD SP!,{R4}", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "mov  R4,SP", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "add SP , SP,#0xff0", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "mov SP , R4", "", true));
        Builder.CreateCall(InlineAsm::get(FunctionType::get(Type::getVoidTy(F.getContext()),{},false), "LDMFD SP! ,{R4}", "", true));
      }
      return true;
    }
    //judge the target machine
    virtual bool doInitialization(Module &M) override{
    Triple tri(M.getTargetTriple());
    // errs() << "targetArch == " << tri.getArch() <<"\n";
    if(tri.isAndroid()){
      if(tri.getArch() == Triple::ArchType::arm){
        if(tri.getSubArch() == Triple::SubArchType::ARMSubArch_v7) this->targetFlag =2;
      }
      else if(tri.getArch() == Triple::ArchType::x86)  this->targetFlag=1;
    }
    }
  };
}

FunctionPass *llvm::createJustTestPass() { return new JustTest(); }
FunctionPass *llvm::createJustTestPass(bool flag) {
  return new JustTest(flag);
}
char JustTest::ID = 0;
INITIALIZE_PASS(JustTest, "justtest", "just test my pass", true,
                true)

```

4. 在include/llvm/Transforms/Obfuscation/下CMakeLists.txt 添加目标。





从FunctionPass替换成ModulePass ，没有重复的插入代码，猜测在使用FunctionPass 时，把一个Module当作一个文件，由于MOdule行为不可预测，假如出现一个文件印用另一个文件，即一个module引用另一个module，是否可能出现module的重复引用，导致functionpass的重复插入，

那么问题来了，我将functionpass改为modulepass以后，重复插入的问题就消失了，但是一个文件引用另一个文件，会导致module重复引用的猜测，就错误了。

后期验证实验：

同时编译两个hikari，一个为functionpass 另一个modulepass。







