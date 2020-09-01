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

# 目标寄存器

你必须用TargetRegistry 来注册你的目标，提供其他LLVM工具使用。TargetRegistry可以被直接使用，但是对于绝大多数的目标有辅助模板来帮助你的工作。

所有的目标应该定义一个全局Target对象用来表示注册阶段的对象。然后，在目标的TargetInfo库中，应该定义对象并且用RegisterTarget模板来注册对象。例如，Sparc 注册代码：

```
Target llvm::getTheSparcTarget();

extern "C" void LLVMInitializeSparcTargetInfo() {
  RegisterTarget<Triple::sparc, /*HasJIT=*/false>
    X(getTheSparcTarget(), "sparc", "Sparc");
}
```

这样允许TargetRegistry通过名称和三元数组来查找目标。另外，大多数目标还会注册其他功能这样其他单独库也可以使用。这些注册步骤是单独的，因为一些客户端可能希望仅仅链接部分目标，就像JIT代码生成器不要求打印汇编代码，以下有个注册Sparc 汇编打印器的例子:

```
extern "C" void LLVMInitializeSparcAsmPrinter() {
  RegisterAsmPrinter<SparcAsmPrinter> X(getTheSparcTarget());
}
```

For more information, see “[llvm/Target/TargetRegistry.h](https://llvm.org/doxygen/TargetRegistry_8h-source.html)”.

#  寄存器集和寄存器类

你应该描述一个具备的目标类来表示目标机器的寄存器文件。这个类被叫做XXXRegisterInfo并且表示用来寄存器分配的类寄存器文件数据。也可以被叫做寄存器间的接口。

你也需要去定义一个寄存器类来分类相关寄存器。给一些相同作用的寄存器分配一个类。尤其是整形 、浮点型、矢量寄存器。一个寄存器分配器允许一个指令使用特定寄存器类的所有寄存器来运行指令。寄存器类从集合中分配虚拟寄存器来来使用，并且寄存器类允许目标独立寄存器自动分配选择实际的寄存器。

寄存器类中很多代码 ，包括寄存器定义，寄存器别名和寄存器类 ，都是通过XXXRegisterinfo.td输入文件的TableGen产生并放在XXXGenRegisterInfo.h.inc 和XXXGenRegisterInfo.inc 输出文件。一些在XXXRegister实现的代码要求手写。

# 定义一个寄存器

XXXRegisterInfo.td 文件以一个目标机器寄存器定义开头。寄存器类用来给每个寄存器定义一个对象。指定的字符串n 是寄存器名称。基础的寄存器对象没有任何子类寄存器对象并不会指定别名。

```
class Register<string n> {
  string Namespace = "";
  string AsmName = n;
  string Name = n;
  int SpillSize = 0;
  int SpillAlignment = 0;
  list<Register> Aliases = [];
  list<Register> SubRegs = [];
  list<int> DwarfNumbers = [];
}
```

例如，在X86RegisterInfo.td文件，有寄存器定义来使用Regiser类，例如

```
def AL : Register<"AL">, DwarfRegNum<[0, 0, 0]>;
```

这定义了AL寄存器并且分配了可以被gdb，gcc 使用的值。对于寄存器AL，DwarfRegNum 使用有三个值的数组表示三个不同的模式：第一个元素对应X86-64,第二个对应X86-32的异常处理，第三个是通用的。-1 是一个特殊的Dwarf数表示gcc number 未定义，-2表示这个模式中寄存器数是无效的。

在之前描述的X86RegisterInfo.td文件，TableGen在X86GenRegisterInfo.inc

TableGen在X86GenRegisterInfo.inc 文件中产生这段代码。

```
static const unsigned GR8[] = {X86::AL , ...};
const unsigned AL_AliasSet[] = { X86::AX, X86::EAX, X86::RAX, 0 };

const TargetRegisterDesc RegisterDescriptors[] = {
  ...
{ "AL", "AL", AL_AliasSet, Empty_SubRegsSet, Empty_SubRegsSet, AL_SuperRegsSet }, ...
```

 从寄存器信息文件，TableGen 产生一个TargetRegisterDesc对象给每个寄存器。TargetRegisterDesc定义在include/llvm/Target/TargetRegisterInfo.h文件下，有这些字段：

```
struct TargetRegisterDesc {
  const char     *AsmName;      // Assembly language name for the register
  const char     *Name;         // Printable name for the reg (for debugging)
  const unsigned *AliasSet;     // Register Alias Set
  const unsigned *SubRegs;      // Sub-register set
  const unsigned *ImmSubRegs;   // Immediate sub-register set
  const unsigned *SuperRegs;    // Super-register set
};
```

TableGen使用整个目标描述文件来决定寄存器的目标名称(AsmName 和TargetRegisterDesc 的Name字段)和与其他寄存器之间的关系(TargetRegisterDesc )，在这个例子中，其他定义建立在寄存器"AX" , "EAX" 和"RAX" 作为另一个的别名，所以TableGen产生了一个NULL结束的数组对应这个寄存器别名集合。

Register类通常用作更复杂类的基类。在Target.td , Register类就是RegisterWithSubRegs的基类，RegisterWithSubRegs用来定义SubRegs列表中需要去指定的寄存器，例如：

```
class RegisterWithSubRegs<string n, list<Register> subregs> : Register<n> {
  let SubRegs = subregs;
}
```

在SparcRegisterInfo.td ，额外的寄存器类定义给SPARC：一个Register子类，SparcReg，和更多子类：Ri,Rf 和Rd 。SPARC寄存器被5字节长的数据标记，是这些子类常有的特征。记住let 表达式的使用重载了父类最初定义的值。（例如 RD 类中SubRegs字段）。

```
class SparcReg<string n> : Register<n> {
  field bits<5> Num;
  let Namespace = "SP";
}
// Ri - 32-bit integer registers
class Ri<bits<5> num, string n> :
SparcReg<n> {
  let Num = num;
}
// Rf - 32-bit floating-point registers
class Rf<bits<5> num, string n> :
SparcReg<n> {
  let Num = num;
}
// Rd - Slots in the FP register file for 64-bit floating-point values.
class Rd<bits<5> num, string n, list<Register> subregs> : SparcReg<n> {
  let Num = num;
  let SubRegs = subregs;
}
```

在SparcRegisterInfo.td文件，有寄存器定义利用这些Register的子类：

```
def G0 : Ri< 0, "G0">, DwarfRegNum<[0]>;
def G1 : Ri< 1, "G1">, DwarfRegNum<[1]>;
...
def F0 : Rf< 0, "F0">, DwarfRegNum<[32]>;
def F1 : Rf< 1, "F1">, DwarfRegNum<[33]>;
...
def D0 : Rd< 0, "F0", [F0, F1]>, DwarfRegNum<[32]>;
def D1 : Rd< 2, "F2", [F2, F3]>, DwarfRegNum<[34]>;
```

最后两个寄存器是双精度浮点寄存器是两个单精度浮点数的子类的别名。除了别名已定义的子寄存器和父寄存器之间的关系位于TargetRegisterDesc字段中