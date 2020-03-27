# 测试用代码

```
#include <stdio.h>
#include <stdlib.h>

int main(void){
    char buf[20];
    int a;
    gets(buf);
    printf(buf);
    a=1;
    return 0;
}
```
编译代码
	afl-gcc a.c -o afla 
	gcc a.c -o a



# 代码流程

find_as (argv[0]) 
    使用afl-as 来完成插桩和汇编
edit_params(argc , argv)
	遍历所有的选项并添加选项
execvp(cc_params[0], (char**)cc_params);
```
afl-gcc 执行的命令
gcc	 a.c  -o  afla  -B  /usr/local/lib/afl  -g  -O3  -funroll-loops  -D__AFL_COMPILER=1  -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1
afl-as 执行的命令
as --64 -o /tmp/ccEZ3blM.o /tmp/.afl-1664-1584697446.s input_file /tmp/ccS1s4lO.s
```

# 差异
将gcc 和afl-gcc 的二进制文件进行对比

objdump -d a   
```
00000000000006fa <main>:
 6fa:   55                      push   %rbp
 6fb:   48 89 e5                mov    %rsp,%rbp
 6fe:   48 83 ec 30             sub    $0x30,%rsp
 702:   64 48 8b 04 25 28 00    mov    %fs:0x28,%rax
 709:   00 00
 70b:   48 89 45 f8             mov    %rax,-0x8(%rbp)
 70f:   31 c0                   xor    %eax,%eax
 711:   48 8d 45 e0             lea    -0x20(%rbp),%rax
 715:   48 89 c7                mov    %rax,%rdi
 718:   b8 00 00 00 00          mov    $0x0,%eax
 71d:   e8 ae fe ff ff          callq  5d0 <gets@plt>
 722:   48 8d 45 e0             lea    -0x20(%rbp),%rax
 726:   48 89 c7                mov    %rax,%rdi
 729:   b8 00 00 00 00          mov    $0x0,%eax
 72e:   e8 8d fe ff ff          callq  5c0 <printf@plt>
 733:   c7 45 dc 01 00 00 00    movl   $0x1,-0x24(%rbp)
 73a:   b8 00 00 00 00          mov    $0x0,%eax
 73f:   48 8b 55 f8             mov    -0x8(%rbp),%rdx
 743:   64 48 33 14 25 28 00    xor    %fs:0x28,%rdx
 74a:   00 00
 74c:   74 05                   je     753 <main+0x59>
 74e:   e8 5d fe ff ff          callq  5b0 <__stack_chk_fail@plt>
 753:   c9                      leaveq
 754:   c3                      retq
 755:   66 2e 0f 1f 84 00 00    nopw   %cs:0x0(%rax,%rax,1)
 75c:   00 00 00
 75f:   90                      nop
```
 objdump -d afla
 ```
0000000000000890 <main>:
 890:   48 8d a4 24 68 ff ff    lea    -0x98(%rsp),%rsp
 897:   ff
 898:   48 89 14 24             mov    %rdx,(%rsp)
 89c:   48 89 4c 24 08          mov    %rcx,0x8(%rsp)
 8a1:   48 89 44 24 10          mov    %rax,0x10(%rsp)
 8a6:   48 c7 c1 61 5d 00 00    mov    $0x5d61,%rcx
 8ad:   e8 ee 01 00 00          callq  aa0 <__afl_maybe_log>
 8b2:   48 8b 44 24 10          mov    0x10(%rsp),%rax
 8b7:   48 8b 4c 24 08          mov    0x8(%rsp),%rcx
 8bc:   48 8b 14 24             mov    (%rsp),%rdx
 8c0:   48 8d a4 24 98 00 00    lea    0x98(%rsp),%rsp
 8c7:   00
 8c8:   53                      push   %rbx
 8c9:   48 83 ec 20             sub    $0x20,%rsp
 8cd:   64 48 8b 04 25 28 00    mov    %fs:0x28,%rax
 8d4:   00 00
 8d6:   48 89 44 24 18          mov    %rax,0x18(%rsp)
 8db:   31 c0                   xor    %eax,%eax
 8dd:   48 89 e3                mov    %rsp,%rbx
 8e0:   48 89 df                mov    %rbx,%rdi
 8e3:   e8 38 ff ff ff          callq  820 <gets@plt>
 8e8:   31 c0                   xor    %eax,%eax
 8ea:   48 89 de                mov    %rbx,%rsi
 8ed:   bf 01 00 00 00          mov    $0x1,%edi
 8f2:   e8 39 ff ff ff          callq  830 <__printf_chk@plt>
 8f7:   48 8b 54 24 18          mov    0x18(%rsp),%rdx
 8fc:   64 48 33 14 25 28 00    xor    %fs:0x28,%rdx
 903:   00 00
 905:   75 41                   jne    948 <main+0xb8>
 907:   90                      nop
 908:   48 8d a4 24 68 ff ff    lea    -0x98(%rsp),%rsp
 90f:   ff
 910:   48 89 14 24             mov    %rdx,(%rsp)
 914:   48 89 4c 24 08          mov    %rcx,0x8(%rsp)
 919:   48 89 44 24 10          mov    %rax,0x10(%rsp)
 91e:   48 c7 c1 d5 28 00 00    mov    $0x28d5,%rcx
 925:   e8 76 01 00 00          callq  aa0 <__afl_maybe_log>
 92a:   48 8b 44 24 10          mov    0x10(%rsp),%rax
 92f:   48 8b 4c 24 08          mov    0x8(%rsp),%rcx
 934:   48 8b 14 24             mov    (%rsp),%rdx
 938:   48 8d a4 24 98 00 00    lea    0x98(%rsp),%rsp
 93f:   00
 940:   48 83 c4 20             add    $0x20,%rsp
 944:   31 c0                   xor    %eax,%eax
 946:   5b                      pop    %rbx
 947:   c3                      retq
 948:   48 8d a4 24 68 ff ff    lea    -0x98(%rsp),%rsp
 94f:   ff
 950:   48 89 14 24             mov    %rdx,(%rsp)
 954:   48 89 4c 24 08          mov    %rcx,0x8(%rsp)
 959:   48 89 44 24 10          mov    %rax,0x10(%rsp)
 95e:   48 c7 c1 2a 3a 00 00    mov    $0x3a2a,%rcx
 965:   e8 36 01 00 00          callq  aa0 <__afl_maybe_log>
 96a:   48 8b 44 24 10          mov    0x10(%rsp),%rax
 96f:   48 8b 4c 24 08          mov    0x8(%rsp),%rcx
 974:   48 8b 14 24             mov    (%rsp),%rdx
 978:   48 8d a4 24 98 00 00    lea    0x98(%rsp),%rsp
 97f:   00
 980:   e8 6b fe ff ff          callq  7f0 <__stack_chk_fail@plt>
 985:   66 2e 0f 1f 84 00 00    nopw   %cs:0x0(%rax,%rax,1)
 98c:   00 00 00
 98f:   90                      nop
 ```
 明显的差异，抬高栈，保存寄存器，调用__afl_maybe_log , 还原寄存器，还原栈
 ```
 890:   48 8d a4 24 68 ff ff    lea    -0x98(%rsp),%rsp
 897:   ff
 898:   48 89 14 24             mov    %rdx,(%rsp)
 89c:   48 89 4c 24 08          mov    %rcx,0x8(%rsp)
 8a1:   48 89 44 24 10          mov    %rax,0x10(%rsp)
 8a6:   48 c7 c1 61 5d 00 00    mov    $0x5d61,%rcx
 8ad:   e8 ee 01 00 00          callq  aa0 <__afl_maybe_log>
 8b2:   48 8b 44 24 10          mov    0x10(%rsp),%rax
 8b7:   48 8b 4c 24 08          mov    0x8(%rsp),%rcx
 8bc:   48 8b 14 24             mov    (%rsp),%rdx
 8c0:   48 8d a4 24 98 00 00    lea    0x98(%rsp),%rsp
 ```
__afl_maybe_log 过程分析 

```
0000000000000aa0 <__afl_maybe_log>:
 aa0:   9f                      lahf   //保留ax低八位寄存器
 aa1:   0f 90 c0                seto   %al //如果of = 1 ， 则al = 1
 aa4:   48 8b 15 6d 15 20 00    mov    0x20156d(%rip),%rdx        # 202018 <__afl_area_ptr>
 aab:   48 85 d2                test   %rdx,%rdx
 aae:   74 20                   je     ad0 <__afl_setup>

```

__afl_setup

```
0000000000000ad0 <__afl_setup>:
 ad0:   80 3d 59 15 20 00 00    cmpb   $0x0,0x201559(%rip)        # 202030 <__afl_setup_failure>
 ad7:   75 ef                   jne    ac8 <__afl_return>
 ad9:   48 8d 15 58 15 20 00    lea    0x201558(%rip),%rdx        # 202038 <__afl_global_area_ptr>
 ae0:   48 8b 12                mov    (%rdx),%rdx
 ae3:   48 85 d2                test   %rdx,%rdx
 ae6:   74 09                   je     af1 <__afl_setup_first>
 ae8:   48 89 15 29 15 20 00    mov    %rdx,0x201529(%rip)        # 202018 <__afl_area_ptr>
 aef:   eb bf                   jmp    ab0 <__afl_store>
```







 还有个小差异

 ```
  8f2:   e8 39 ff ff ff          callq  830 <__printf_chk@plt>
 ```
