# ANTI-DISASSEMBLY 技术

IDA是当前静态代码分析工具中最流行的一款工具，但是如果IDA反汇编失败或者展示给你错误的代码段，就会大大加大静态分析能力。

其中可以导致IDA 解析错误或异常的方式有很多，我选择使用 call ret 的方式。

# 原理

![image-20200805125330102](..\res\pic\image-20200805125330102.png)

这是一段用汇编写的代码 ， 入口在0x8048230 ， call $ + 5 调用到0x8048230 + 5 = 0x8048235 并且将0x8048235 放入栈顶，然后栈顶的值+5 ，0x8048235 + 5 = 0x8048240 ，栈顶的值为0x8048240  ，ret 指令跳转到0x8048240  进入正常的流程，而IDA 在ret处 将会判断函数结束，导致F5 反编译失败。但是被过也很简单，所以可以在跳转偏移和返回上做些随机插入。







# 实现方案

利用llvm 写pass 在函数头或者函数体间插入这段代码，但是想想这样很好被过。

```


```







>http://staff.ustc.edu.cn/~bjhua/courses/security/2014/readings/anti-disas.pdf anti-disas
>
>https://medium.com/@preetkamal1012/anti-disassembly-techniques-e012338f2ae0 anti-disas
>
>https://blog.csdn.net/shallnet/article/details/45544271 AT&T汇编 helloworld
>
>http://docs.linuxtone.org/ebooks/C&CPP/c/ch19s02.html 汇编与C之间的关系，main函数和启动例程
>
>https://llvm.org/docs/ProgrammersManual.html#passing-functions-and-other-callable-objects pass 手册

