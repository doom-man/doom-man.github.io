# 简介

描述将中间语言转换为特定机器的汇编语言和二进制代码。

llvm后端具有目标无关代码生成器可以生成几种类型的目标cpu创建输出。包括X86 ,PowerPC ,ARM  和 SPARC 。

文档关注在llvm/lib/Target 下已有的例子在llvm release下载。该文档尤其关注为SPARC目标创建静态编译器。因为SPARC有相对标准的特征，例如RISC指令集和直接调用协议。

# 基本步骤

* 创建TargetMachine类的子类来描述目标机器的特征。复制已有的TargetMachine类和头文件；例如已SparcTargetMachine.cpp开头和SparcTargetMachine.h ，但是改变文件名称为你的目标机器。
* 描述目标的寄存器，有TableGen来产生寄存器定义的代码，寄存器别名和特定机器的RegisterInfo.td输入文件的寄存器类。你应该也写TargetRegisterInfo子类的额外代码来表示要用的寄存器和寄存器间交互。
* 描述目标的指令集，有TableGen从TargetInstrFormats.td 的版本和TargetInstrInfo.td 来产特定机器的代码。你应该写额外的TargetInstrInfo子类代码来表示目标机器支持的机器指令。
* 描述中间指令从有向无环图表示到目标指令的选择和转换。用TableGen来产生机器模式的代码并且基于目标机器特定版本的TargetInstrInfo.td。写XXXISelDAGToDAG.cpp ,XXX标识目标机器，来运行特定机器和DAG-to-DAG指令选择。另外在XXXISelLowering.cpp写了代码来取代或者移除在SelectoionDag不支持的操作和数据类型。
* 写汇编大打印机转换LLVM IR到目标机器的GAS形式。你应该在目标机器版本的TargetInstrInfo.td 中定义的指令增加汇编指令。你应该写AsmPriter的子类来运行LLVM-to-assemble 的转换还有一个不重要的子类TArgetAsmInfo.
* 可选的，增加子目标的支持。你也应该写TargetSubtarget的子类代码来允许你用-mcpu= 和-mattr= 命令行选项。
* 可选的，增加jit支持并且创建机器代码产生器用来直接从内存产生二进制代码。

在.cpp 和.h 文件中，首先保存这些方法然后再实现他们，起初，你可能不知道那个类会需要私有成员和哪些组件会被子类化。



# 前提

为了实际创建一个编译器后端，你需要创建和修改一些文件。这里仅讨论较小的部分。但是为了实际使用LLVM 目标独立代码生成器，你必须按照[LLVM Target-Indepent Code Generator]('https://llvm.org/docs/CodeGenerator.html')文档。

首先，你应该创建lib/Target的子目录来保存目标机器的所有相关代码。如果你的目标叫做"Dummy" ,创建目录lib/Target/Dummy.

在这个新目录，创建CmakeList.txt。从另一个目标目录复制修改CmakeList.txt 是最简单的方法。应该至少有LLVM_TARGET_DEFINITIONS 变量。库可以叫做LLVMDummy(例如 MPS目标) 。可选的你可以将库分进LLVMDummyCodeGen和LLVMDummyAsmPriter , 然后应该再lib/Target/Dummy子目录下实现。

记住，有两个命名的方案被硬编码进llvm-config。用其他的命名方案会迷惑llvm-config 和在llc链接过程产生很多链接错误。

为了确保你的目标实际发挥作用，你需要实现TargetMachine的子类。这个实现应该在lib/Target/DummyTargetMachine.cpp,但在lib/Target目录下任何文件会被建立和工作。为了使用LLVM 目标特定代码生成器，你应该创建LLVMTArgetMachine 的子类。

为了让LLVM实际生成和链接进你的目标，你需要运行带有-DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=Dummy参数的cmake命令。这样会创建你的目标机器代码而不需要将它添加到所有目标的列表中。

一旦你的目标稳定以后，你可以将它增加到main CMakeLists.txt 的LLVM_ALL_TARGETS 变量中。



# 目标机器

LLVMTargetMachine 被设计为一个为llvm 目标独立代码生成器的基类。LLVMTargtMachine类应该通过实现各种虚拟方法的具体目标类实现。LLVMTargetmachine 被定义为一个TargetMachine的子类，在include/llvm/Target/Targetmachine.h下。TargetMachine类实现(TargetMachine.cpp)也处理了大量的命令行选项。

为了创建一个具体的LLVMTargetMachine目标特定子类，首先复制已有的TargetMachine 类和头文件。你应该命名这些文件对应特定的目标。

例如，对于SPARC目标，命名文件SparcTargetMachine.h 和SparcTargetMachine.cpp。定义了几个简单返回类成员的get*Info的原型和getDataLayout方法。

```
namespace llvm {

class Module;

class SparcTargetMachine : public LLVMTargetMachine {
  const DataLayout DataLayout;       // Calculates type size & alignment
  SparcSubtarget Subtarget;
  SparcInstrInfo InstrInfo;
  TargetFrameInfo FrameInfo;

protected:
  virtual const TargetAsmInfo *createTargetAsmInfo() const;

public:
  SparcTargetMachine(const Module &M, const std::string &FS);

  virtual const SparcInstrInfo *getInstrInfo() const {return &InstrInfo; }
  virtual const TargetFrameInfo *getFrameInfo() const {return &FrameInfo; }
  virtual const TargetSubtarget *getSubtargetImpl() const{return &Subtarget; }
  virtual const TargetRegisterInfo *getRegisterInfo() const {
    return &InstrInfo.getRegisterInfo();
  }
  virtual const DataLayout *getDataLayout() const { return &DataLayout; }
  static unsigned getModuleMatchQuality(const Module &M);

  // Pass Pipeline Configuration
  virtual bool addInstSelector(PassManagerBase &PM, bool Fast);
  virtual bool addPreEmitPass(PassManagerBase &PM, bool Fast);
};

} // end namespace llvm
```

- `getInstrInfo()`
- `getRegisterInfo()`
- `getFrameInfo()`
- `getDataLayout()`
- `getSubtargetImpl()`

对于一些目标，你也应该支持以下的方法：

- `getTargetLowering()`
- `getJITInfo()`

一些架构，例如GPUs ，不支持跳转到任意程序位置和标记的执行分支

并且循环在循环体中使用特殊的指令。为了避免CFG修改引入不可简化的控制流不能被这样的硬件处理，目标在初始化时必须调用setRequiresStructuresCFG(true)。

另外，XXXTargetMachine constructor 应该指定TargetDescription字符串来决定目标机制的数据视图，包括一些特征例如指针尺寸，对齐 和端序。例如，以下SparcTargetmachine 的constructot 包括：

```
SparcTargetMachine::SparcTargetMachine(const Module &M, const std::string &FS)
  : DataLayout("E-p:32:32-f128:128:128"),
    Subtarget(M, FS), InstrInfo(Subtarget),
    FrameInfo(TargetFrameInfo::StackGrowsDown, 8, 0) {
}
```

连字符分开TargetDescription字符串。

* 字符串中大写的E标志大端， 小写的e表示小端。
* "p:"后是指针信息：尺寸，ABI alignment，和preferred alignment。如果"p:"后仅有两个数字，那么第一个数字表示指针大写，第二个值表示ABI 和preferred alignment。
* 然后一个字母用于数字类型对齐："i","f","v" or "a"。"i","v"or”a“后接着ABI对齐和首选(偏好)对齐。"f" 后接三个数字第一个表示long double 的尺寸，ABI对齐和ABI首选对齐。





