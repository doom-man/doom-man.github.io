# ANTI-DISASSEMBLY 技术

Preet kamal 介绍不少能反IDA f5的手段，我主要说明其中我比较喜欢的方案（简单好实现）。

## 乱用返回指针

![image-20200805125330102](..\res\pic\image-20200805125330102.png)

这是一段用汇编写的代码 ， 入口在0x8048230 ， call $ + 5 调用到0x8048230 + 5 = 0x8048235 并且将0x8048235 放入栈顶，然后栈顶的值+5 ，0x8048235 + 5 = 0x8048240 ，栈顶的值为0x8048240  ，ret 指令跳转到0x8048240  进入正常的流程，而IDA 在ret处 将会判断函数结束，导致F5 反编译失败。但是被过也很简单，所以可以在跳转偏移和返回上做些随机插入。

## 混淆栈分析

![Image for post](G:\gitproject\doom-man.github.io\res\pic\1_MT7B7Oc85CvKh18qmwNLvA.png)

出问题的代码就出现在00401549，当栈顶指针和0x1000h比较，为真时，esp-104h ,继续执行发现IDA分析的栈顶偏移为-F8 ,这样就摧毁了栈帧并且他会以为有62个参数配压入栈。出现问题的原因就在比较指令上，401549的cmp指令要求IDA对两个分支进行预测，实际上错误的分支永远不会被执行，就看上面两个的例子可以猜测，这是由于动态执行修正地址后导致出现条件语句的结果和静态分析时不同，同样的问题在arm 上有个指令adrl于PC相关的指令同样可以用在IDA反f5上。通过修改这个例子的汇编代码，我注意到，其实直接修改esp指针也能达到效果。如下：

```
pus eax
mov eax,esp
add esp,0ff0H
mov esp,eax
pop eax
```

提前保存esp指针，然后修改esp指针最后还原，IDA同样也会认为栈不平衡。

## 错误的反汇编

![1_-sm2XT95w7-1kQMfbhYOew](G:\gitproject\doom-man.github.io\res\pic\1_-sm2XT95w7-1kQMfbhYOew.png)

第一句jmp指令，跳转到401216 ,就是jump指令的第二个字节，但是IDA把EB FF 看作为一句指令，并继续向下解析。

解决方案就是401215给nop掉。





>http://staff.ustc.edu.cn/~bjhua/courses/security/2014/readings/anti-disas.pdf anti-disas
>
>https://medium.com/@preetkamal1012/anti-disassembly-techniques-e012338f2ae0 anti-disas
>
>https://blog.csdn.net/shallnet/article/details/45544271 AT&T汇编 helloworld
>
>http://docs.linuxtone.org/ebooks/C&CPP/c/ch19s02.html 汇编与C之间的关系，main函数和启动例程
>
>https://llvm.org/docs/ProgrammersManual.html#passing-functions-and-other-callable-objects pass 手册

