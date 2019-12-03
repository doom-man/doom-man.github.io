# ELF文件分析

## 结构分析
![image](32D48ED1DC69461493A1B6A1A09C484F)
![image](E02F7F9FD0B746D6B1615F866B9FE7E4)
### elf header
描述整个文件的组织
```
#define EI_NIDENT (16)
typedef struct
{
  unsigned char e_ident[EI_NIDENT];   /* Magic number and other info */
  Elf32_Half    e_type;               /* Object file type */
  Elf32_Half    e_machine;            /* Architecture */
  Elf32_Word    e_version;            /* Object file version */
  Elf32_Addr    e_entry;              /* Entry point virtual address */
  Elf32_Off     e_phoff;              /* Program header table file offset */
  Elf32_Off     e_shoff;              /* Section header table file offset */
  Elf32_Word    e_flags;              /* Processor-specific flags */
  Elf32_Half    e_ehsize;             /* ELF header size in bytes */
  Elf32_Half    e_phentsize;          /* Program header table entry size */
  Elf32_Half    e_phnum;              /* Program header table entry count */
  Elf32_Half    e_shentsize;          /* Section header table entry size */
  Elf32_Half    e_shnum;              /* Section header table entry count */
  Elf32_Half    e_shstrndx;           /* Section header string table index */
} Elf32_Ehdr;
```
#### e_ident
![image](F3D514D9E6BC44FABD27D5EF414C5FA3)


e_ident[EI_MAG0] 到 e_ident[EI_MAG3]，即文件的头 4 个字节，被称作 “魔数”，标识该文件是一个 ELF 目标文件。至于开头为什么是 0x7f，并没有仔细去查过。

![image](B6BF39CB06BE4689BFB1FA9D306D3D81)
e_ident[EI_CLASS] 为 e_ident[EI_MAG3]的下一个字节，标识文件的类型或容量。

![image](2649D7AE4A594FECB6EF5EE63D62984E)

e_ident[EI_DATA]字节给出了目标文件中的特定处理器数据的编码方式。下面是目前已定义的编码：

![image](2AB660D99B9C44129F7163FD244274BA)

#### e_type

![image](C1F30836D2814527935E1146BA80F74A)

#### e_machine

![image](CE7716AAC2A3435799045BFD79C44C80)

其中 EM 应该是 ELF Machine 的简写。

#### e_version

![image](AA3C88EA12D6447AA49D08DBC9395F2F)

#### e_entry

这一项为系统转交控制权给 ELF 中相应代码的虚拟地址。如果没有相关的入口项，则这一项为 0。

#### e_phoff


这一项给出程序头部表在文件中的字节偏移（Program Header table OFFset）。如果文件中没有程序头部表，则为 0。

#### e_shoff


这一项给出节头表在文件中的字节偏移（ Section Header table OFFset ）。如果文件中没有节头表，则为 0。
从ROP程序中看ROP

#### e_flags

这一项给出文件中与特定处理器相关的标志，这些标志命名格式为EF_machine_flag。

#### e_ehsize

这一项给出 ELF 文件头部的字节长度（ELF Header Size）。

#### e_phentsize


这一项给出程序头部表中每个表项的字节长度（Program Header ENTry SIZE）。每个表项的大小相同。


    
### 程序头programmer head

程序头部是描述文件中的各种segments（段），用来告诉系统如何创建进程映像的。
![image](FEC430275F0348F1B55BC07DA7378CC9)

### 节区头section header
包含节区信息
```
/* Section header.  */
typedef struct
{
  elf32_word    sh_name;        /* Section name (string tbl index) */
  elf32_word    sh_type;        /* Section type */
  elf32_word    sh_flags;       /* Section flags */
  elf32_addr    sh_addr;        /* Section virtual addr at execution */
  elf32_off     sh_offset;      /* Section file offset */
  elf32_word    sh_size;        /* Section size in bytes */
  elf32_word    sh_link;        /* Link to another section */
  elf32_word    sh_info;        /* Additional section information */
  elf32_word    sh_addralign;   /* Section alignment */
  elf32_word    sh_entsize;     /* Entry size if section holds table */
} elf32_shdr;
```
SectionType：(sh_type)

    PROGBITS:           This holds program contents including code, data, and debugger information. 
    NOBITS:             Like PROGBITS. However, it occupies no space. 
    SYMTAB and DYNSYM:  These hold symbol table.                              [See below]
    STRTAB:             This is a string table, like the one used in a.out.   [See below]
    REL and RELA:       These hold relocation information. 
    DYNAMIC and HASH:   This holds information related to dynamic linking. 

下面列举了一些常见的Section:

    .text:  (PROGBITS:ALLOC+EXECINSTR)
         可执行代码
    .data:  (PROGBITS:ALLOC+WRITE)
         初始化数据
    .rodata:(PROGBITS:ALLOC)
         只读数据
    .bss:   (NOBITS:ALLOC+WRITE)
         未初始化数据,运行时会置0
    .rel.text, .rel.data, and .rel.rodata:(REL)
         静态链接的重定位信息
    .rel.plt: (REL)
         The list of elements in the PLT, which are liable to the relocatio during the dynamic linking(if PLT is used)
    .rel.dyn: (REL)
         The relocation for dynamically linked functions(if PLT is not used)     
    .symtab: 
         符号表
    .strtab: 
         字符串表
    .shstrtab: 
       Section String Table, 段名表
    .init, .fini:   (PROGBITS:ALLOC+EXECINSTR)
         程序初始化与终结代码段
    .interp: (PROGBITS:ALLOC)
         This section holds the pathname of a program interpreter.For present,this is used to run the run-time dynamic linker to load the program and to link in any required shared libraries.
    .got, .plt:    (PROGBIT)
         动态链接的跳转表和全局入口表.
         
![image](51DCA9E091CC44AAAAE30AECBA686EE9)

https://www.freebuf.com/column/197473.html