

# 测试代码
```
  1 #include <stdio.h>
  2 #include <stdlib.h>
  3 int main(void){
  4         void * p[90];
  5         malloc(0x10);
  6         for (int i = 1 ; i <= 10 ; i++)
  7         {
  8                 p[i] = malloc(i*0x10);
  9         }
 10         malloc(0x10);
 11         for(int i = 1;i<=10 ; i++)
 12                 free(p[i]);
 13 
 14         //breakpoint1 
 15         for (int i = 1 ; i <= 10 ; i++)
 16         {
 17                 p[i] = malloc(i*0x10);
 18         }
 19 
 20         //breakpoint 2  modify global_max_fast
 21         for (int i = 1 ; i <= 10 ; i++)
 22         {
 23                 p[i] = malloc(i*0x10);
 24         }
 25         //b 
 26         for(int i = 1;i<=10 ; i++)
 27                 free(p[i]);
 28 
 29         //break point 3
 30         for (int i = 1 ; i <= 10 ; i++)
 31         {
 32                 p[i] = malloc(i*0x10);
 33         }
 34 
 35         //b
 36         return 0;
 37 }

```

代码中给出断点所在位置。
断点在15行时。

```
gdb-peda$ p main_arena .fastbinsY 
$1 = {0x602020, 0x602040, 0x602070, 0x6020b0, 0x602100, 0x602160, 0x6021d0, 
  0x0, 0x0, 0x0}
gdb-peda$ p main_arena .bins[1]
$2 = (mchunkptr) 0x602250
gdb-peda$ x /20gx 0x602250
0x602250:	0x0000000000000000	0x00000000000001e1
0x602260:	0x00007ffff7dd1b78	0x00007ffff7dd1b78
```

断点2处将global_max_fast 修改为一个大值。
断点3处运行结果
```
gdb-peda$ p main_arena .fastbinsY 
$4 = {0x602450, 0x602470, 0x6024a0, 0x6024e0, 0x602530, 0x602590, 0x602600, 
  0x602680, 0x602710, 0x6027b0}
gdb-peda$ p main_arena 
$5 = {
  mutex = 0x0, 
  flags = 0x0, 
  fastbinsY = {0x602450, 0x602470, 0x6024a0, 0x6024e0, 0x602530, 0x602590, 
    0x602600, 0x602680, 0x602710, 0x6027b0}, 
  top = 0x602860, 
  last_remainder = 0x602380, 
  bins = {0x7ffff7dd1b78 <main_arena+88>, 0x7ffff7dd1b78 <main_arena+88>, 
```
可以看出从fastbinY开始覆盖
运行到最后一个断点,从运行结果可以看出又依次从fastbinY中取出。
```
gdb-peda$ p main_arena 
$6 = {
  mutex = 0x0, 
  flags = 0x0, 
  fastbinsY = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  top = 0x602860, 
  last_remainder = 0x602380, 
  bins = {0x7ffff7dd1b78 <main_arena+88>, 0x7ffff7dd1b78 <main_arena+88>, 
    0x7ffff7dd1b88 <main_arena+104>, 0x7ffff7dd1b88 <main_arena+104>, 
    0x7ffff7dd1b98 <main_arena+120>, 0x7ffff7dd1b98 <main_arena+120>, 
    0x7ffff7dd1ba8 <main_arena+136>, 0x7ffff7dd1ba8 <main_arena+136>, 

```