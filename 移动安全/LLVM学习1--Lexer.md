**由于很多教程编写的pass存在问题，自己又不会改 ，本系列教程目的是学习编写llvm pass 主要跟着llvm官网提供的教程来学习。**

# 万花筒语言 - The Kaleidoscope Language

万花筒是一个允许定义函数，使用判断，数学等的程序语言，整个教程中，我们会拓展万花筒来支持 if/then/else 构建，循环，用户自定义操作符，一行命令接口的JIT 编译 ，调试信息等。

我们想让事情简单，所以在万花筒唯一的数据类型是64位的浮点类型（C语言中的double），所有的值默认都是双精度并且万花筒不需要定义。这样让万花筒非常友好，语法简单。例如一个Fibonacci number 计算的例子。

```
# Compute the x'th fibonacci number.
def fib(x)
  if x < 3 then
    1
  else
    fib(x-1)+fib(x-2)

# This expression will compute the 40th number.
fib(40)
```



LLVM JIT 也让万花筒支持调用标准库函数 变得简单，这意味着你可以用'extern' 关键词在你使用前来定义个函数。例如：

```
extern sin(arg);
extern cos(arg);
extern atan2(arg1 arg2);

atan2(sin(.4), cos(42))
```

更有趣的例子在第六章 我们写了一些万花筒的应用用来在不同的放大倍数来展现Mandelbrot 集合。

# 词法分析器 - Lexer

实现一个程序语言的时候，第一件事就是需要处理文本内容和意识到它在表达什么。传统实现方式是使用"Lexer" 词法分析器把输入分解成 "tokens" 。每个词法分析器返回的token 包括token码 和一些元数据。

```
// The lexer returns tokens [0-255] if it is an unknown character, otherwise one
// of these for known things.
enum Token {
  tok_eof = -1,

  // commands
  tok_def = -2,
  tok_extern = -3,

  // primary
  tok_identifier = -4,
  tok_number = -5,
};

static std::string IdentifierStr; // Filled in if tok_identifier
static double NumVal;             // Filled in if tok_number
```

通过词法分析器返回的每个token 会是某个Token 枚举值(Token enum values)或者是不知道(未定义)的字符像 "+" 就会返回它的Ascii值。如果当前的token是一个标识符(Token == -4)，那么全局变量IdentifierStr就会标识符的名称。如果当前koken是数字，那么全局变量NumVal 就会保存它的值。我们因为简单使用全局变量，但是对于真正的语言实现并不是一个好的选择。

词法分析的真正实现是一个叫gettok的简单函数，gettok函数被调用时返回标准输入的下一个token。它定义的开始是：

```
// gettok - Return the next token from standard input.
static int gettok() {
  static int LastChar = ' ';

  // Skip any whitespace.
  while (isspace(LastChar))
    LastChar = getchar();
```







> https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html MyfirstLanguagefrontend