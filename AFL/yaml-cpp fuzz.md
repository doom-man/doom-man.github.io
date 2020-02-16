参照 fuzzing workflows 流程成功出了两个crash 

接下来

1. cmake 添加ASAN 标志 ，查看溢出类型 。 

使用网上两种cmake 添加asan标志均失败

```
set (CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address")
set (CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address")
```

```
cmake -DCMAKE_CXX_COMPILER=afl-g++ -DCMAKE_CXX_FLAGS=-O0 -fsanitize=address ..
```
暂时不纠结这个不影响分析。


2. 查看源码，进行漏洞分析 。

