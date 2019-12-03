[TOC]
# checksec 
```
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled

```
# 溢出点
原以为是堆利用，发现对于堆空间利用的很完美，malloc以后就freel。


细看choise==1时，输入0x438大小的字符串格式化输出异常考虑是格式化溢出漏洞。

```
unsigned __int64 sub_B30()
{
  char s; // [rsp+10h] [rbp-BF0h]
  char v2; // [rsp+410h] [rbp-7F0h]
  __int64 v3; // [rsp+7F8h] [rbp-408h]
  unsigned __int64 v4; // [rsp+BF8h] [rbp-8h]

  v4 = __readfsqword(0x28u);
  memset(&s, 0, 0x400uLL);
  memset(&v3, 0, 8uLL);
  memset(&v2, 0, 0x7E8uLL);
  LOWORD(v3) = 's%';
  BYTE2(v3) = 0;
  puts("Welcome To WHCTF2017:");
  read(0, &s, 0x438uLL);
  snprintf(&v2, 0x7D0uLL, (const char *)&v3, &s);
  printf("Your Input Is :%s\n", &v2);
  return __readfsqword(0x28u) ^ v4;
}
```
当v2 长度大于1000(0x3e8)将覆盖到v3 ，格式化漏洞。
# exp
```

```