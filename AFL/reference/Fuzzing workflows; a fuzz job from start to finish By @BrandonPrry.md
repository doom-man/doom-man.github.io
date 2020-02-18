# Fuzzing workflows; a fuzz job from start to finish

在这篇文章中，我们希望从头到尾完成一项模糊的工作。 这到底是什么意思？ 首先，即使找到一个好的软件来进行模糊测试似乎也令人生畏，但是您可以遵循某些标准，这些标准可以帮助您确定在模糊测试中什么是有用且容易上手的。 有了软件后，对它进行模糊处理的最佳方法是什么？ 那我们应该使用哪些测试用例呢？ 我们如何知道我们做得如何，或者目标软件中可能缺少哪些代码路径？



我们希望涵盖所有这些内容，以提供全彩色的360度视图，说明如何从头到尾有效，高效地执行完整的模糊工作流程。 为了易于使用，我们将重点介绍AFL框架。



# 我该fuzz什么？ 找到正确的软件

AFL在C或C ++应用程序上效果最好，因此这是我们应该在想要模糊的软件中寻找的一项标准。 在寻找模糊软件时，我们可以问自己几个问题。



1. 有示例代码吗
   * 该项目附带的任何实用程序都有可能过于繁重，可以出于模糊的目的而进行精简。 如果项目具有简单的示例代码，这将使我们的工作变得更加轻松。
2. 我能自己编译吗
   * 当您能够从源代码构建软件时，AFL效果最佳。 它确实支持使用QEMU即时检测黑匣子二进制文件，但这超出了范围，并且性能往往很差。 在理想的情况下，我可以轻松地使用afl-clang-fast或afl-clang-fast ++构建软件。
3. 是否有容易获得的和独特的测试用例？
   * 我们可能会模糊文件格式（尽管可以进行一些调整，但可以模糊网络应用程序），并且有一些独特而有趣的测试用例可以为我们提供一个良好的开端。 如果项目具有包含文件测试用例的单元测试（或将文件包含先前已知的错误用于回归测试），那么这也是一个的胜利。



这些问题会帮助我们节约很多时间，如果你直接开始一会儿就会很头痛。



好的，但是如何找到有关这些问题的软件？ Github是最适合的地方，因为您可以轻松地搜索最近更新的并用C或C ++编写的项目。 例如，在Github中搜索所有200星以上的C ++项目，使我们找到了一个显示出很大希望的项目：yaml-cpp（https://github.com/jbeder/yaml-cpp）。 让我们用三个问题来研究它，看看我们有多容易得到这种模糊测试。

1. 我可以自己编译吗？
   * yaml-cpp使用cmake作为其构建系统。 当我们可以定义要使用的编译器时，这看起来很棒，而且afl-clang-fast ++很有可能会运行Just™。 yaml-cpp的README文件中的一个有趣注释是，它默认情况下会构建一个静态库，这对我们来说是完美的，因为我们希望为AFL提供一个静态编译和检测到的二进制文件。
2. 有示例代码吗？
   * 在项目根目录（https://github.com/jbeder/yaml-cpp/tree/master/util）的util文件夹中，有一些小的cpp文件，它们是简明的实用程序，展示了以下功能： yaml-cpp库。 特别感兴趣的是parse.cpp文件。 这个parse.cpp文件非常完美，因为它已经被编写为可以接收来自stdin的数据，并且我们可以轻松地使其适应AFL的持久模式，这将大大提高速度。
3. 有容易获得的和独特/有趣的测试用例吗？
   * 在项目根目录的test文件夹中，有一个名为specexamples.h的文件，其中包含许多独特而有趣的YAML测试用例，每个用例似乎都在yaml-cpp库中执行特定的代码段。 同样，对于我们来说，这非常适合作为模糊测试的种子。



程序看起来很简单来开始fuzz 测试，lets‘s do it。

# 开始fuzz

我们将不介绍安装或设置AFL，因为我们假定已经完成了。 我们还假设还已经构建并安装了afl-clang-fast和afl-clang-fast ++。 尽管afl-g ++应该可以正常工作（尽管您不会使用出色的持久模式），但afl-clang-fast ++无疑是首选。 让我们获取yaml-cpp代码库，并使用AFL进行构建。

```
# git clone https://github.com/jbeder/yaml-cpp.git
# cd yaml-cpp
# mkdir build
# cd build
# cmake -DCMAKE_CXX_COMPILER=afl-clang-fast++ ..
# make
```

or afl-g++

```
cmake -DCMAKE_CXX_COMPILER=afl-g++
```



一旦我们知道一切都可以成功构建，就可以对某些源代码进行一些更改，以便AFL可以提高速度。 从项目的根目录/util/parse.cpp中，我们可以更新main()。
```
int main(int argc, char** argv) {
  Params p = ParseArgs(argc, argv);

  if (argc > 1) {
    std::ifstream fin;
    fin.open(argv[1]);
    parse(fin);
  } else {
    parse(std::cin);
  }

  return 0;
}
```

使用这个简单的main（）方法，我们可以更新if语句的else子句，以包括一个while循环和一个称为__AFL_LOOP（）的特殊AFL函数，该函数使AFL可以通过某种内存向导基本上对进程中的二进制文件进行模糊处理。 ，而不是为我们要测试的每个新测试用例启动一个新流程。 让我们看看会是什么样子。
```
if (argc > 1) {
  std::ifstream fin;
  fin.open(argv[1]);
  parse(fin);
} else {
  while (__AFL_LOOP(1000)) {
    parse(std::cin);
  }
}
```

注意else子句中的新while循环，我们将1000传递给__AFL_LOOP（）函数。 这告诉AFL在启动一个新的过程以进行同样的测试之前，最多要模糊处理1000个测试用例。 通过指定更大或更小的数字，您可以增加执行次数，但以牺牲内存使用为代价（或者受内存泄漏的支配），并且可以根据正在使用的应用程序进行高度可调。 添加这种类型的代码以启用持久模式也不总是那么容易。 由于启动期间产生的资源或其他因素，某些应用程序可能没有支持轻松添加while循环的体系结构。

回到build目录，重新编译  。 重新编译遇到问题 afl-clang-fast++ compile 失败，error 003 。 索性直接用afl-g++ 

# 测试二进制文件
程序编译好以后可以使用afl附加的工具afl-showmap，afl-showmap 会运行一个给定的二进制文件（通过标准输入将输入传给二进制文件）并且打印程序运行期间的反馈报告。

```
# afl-showmap -o /dev/null -- ./parse < <(echo hi)
afl-showmap 2.56b by <lcamtuf@google.com>
[*] Executing './parse'...

-- Program output begins --
hi
-- Program output ends --
[+] Captured 1748 tuples in '/dev/null'.

```
通过将输入更改为应该使用新代码路径的内容，你会看到报告末尾出现的元组数量增加或减少。
```
# afl-showmap -o /dev/null -- ./parse < <(echo hi:blah)
afl-showmap 2.56b by <lcamtuf@google.com>
[*] Executing './parse'...

-- Program output begins --
hi:blah
-- Program output ends --
[+] Captured 1771 tuples in '/dev/null'.


```



正如所看到的， 发送了一个yaml 键 hi 展示了1748个反馈元祖，第二次发送了 hi:blah 展示了1771个反馈元祖。



# 使用更好的测试用例

最初为您的Fuzzer注入测试的用例是（如果不是）最重要的方面之一，即是否会看到Fuzz运行是否导致一些良好的崩溃。 如前所述，yaml-cpp测试目录中的specexamples.h文件具有出色的测试用例，供我们开始使用，但它们甚至可以更好。 为此，我手动将示例从头文件复制并粘贴到测试用例中，以节省读者的时间，此处链接的是我用于复制目的的原始种子文件。



afl 附带的两个工具我们可以用来确定：

* 测试语料库中的文件尽可能有效地唯一
* 每个测试文件都尽可能有效地表示其唯一的代码路径

afl-cmin和afl-tmin这两个工具完成所谓的“最小化”。 afl-cmin提取给定的潜在测试用例文件夹，然后运行每个用例并将接收到的反馈与所有其余测试用例进行比较，以找到最佳的测试用例。 有效地表达最独特的代码路径。 最好的测试用例将保存到新目录。



另一方面，afl-tmin工具仅适用于指定的文件。 在进行模糊测试时，我们不想浪费CPU周期来摆弄相对于测试用例可能表示的代码路径无用的位和字节。 为了将每个测试用例最小化到表示与原始测试用例相同的代码路径所需的最低限度，afl-tmin遍历测试用例中的实际字节，逐渐删除越来越小的数据块，直到删除了所有 不影响所采用的代码路径。 有点多，但是这些是有效进行模糊测试的非常重要的步骤，是需要理解的重要概念。 让我们来看一个例子。

git仓库中我创建了从specexample.h文件中的原始测试用例， 我们用两个文件来开始。

1

```
Mark McGwire
Sammy Sosa
Ken Griffey

```

2

```
hr:  65    # Home runs
avg: 0.278 # Batting average
rbi: 147   # Runs Batted In
```

```
# afl-tmin -i in/1 -o in/1.min -- ./parse
afl-tmin 2.56b by <lcamtuf@google.com>

[+] Read 36 bytes from 'in/1'.
[*] Performing dry run (mem limit = 50 MB, timeout = 1000 ms)...
[+] Program terminates normally, minimizing in instrumented mode.
[*] Stage #0: One-time block normalization...
[+] Block normalization complete, 12 bytes replaced.
[*] --- Pass #1 ---
[*] Stage #1: Removing blocks of data...
    Block length = 2, remaining size = 36
    Block length = 1, remaining size = 36
[+] Block removal complete, 0 bytes deleted.
[*] Stage #2: Minimizing symbols (16 code points)...
[+] Symbol minimization finished, 13 symbols (18 bytes) replaced.
[*] Stage #3: Character minimization...
[+] Character minimization done, 0 bytes replaced.
[*] --- Pass #2 ---
[*] Stage #1: Removing blocks of data...
    Block length = 2, remaining size = 36
    Block length = 1, remaining size = 36
[+] Block removal complete, 0 bytes deleted.

     File size reduced by : 0.00% (to 36 bytes)
    Characters simplified : 83.33%
     Number of execs done : 96
          Fruitless execs : path=79 crash=0 hang=0

[*] Writing output to 'in/1.min'...
[+] We're done here. Have a nice day!

# cat 1.min
0000 0000000
00000 0000
000 0000000
```



这是AFL功能强大的一个很好的例子。 AFL不知道YAML是什么或它的语法是什么，但是它实际上能够将不是用于表示键值对的特殊YAML字符的所有字符归零。 通过确定更改这些特定字符将极大地改变已检测二进制文件的反馈，便可以做到这一点，并且应将它们单独放置。 它还从原始文件中删除了四个字节，这些字节不会影响所采用的代码路径，因此，这将减少四个字节，这将浪费CPU周期。

为了快速最小化开始的测试语料库，我通常使用quick for循环将每个最小化为一个新文件，并将其扩展为.min。

```
# for i in *; do afl-tmin -i $i -o $i.min -- ~/parse; done;
# mkdir ~/testcases && cp *.min ~/testcases
```



此for循环将遍历当前目录中的每个文件，并使用afl-tmin将其最小化为一个与第一个文件同名的新文件，只是在文件后添加.min。 这样，我可以仅将cp * .min cp到用于将AFL用作种子的文件夹。

# 开始fuzz

这是大多数令人费解的演练的结尾部分，但是我向您保证，这仅仅是开始！既然我们已经有了一套高质量的测试用例来作为AFL的种子，那么我们就可以开始了。可选地，我们还可以利用字典标记功能为YFL特殊字符添加AFL种子，以增加效力，但我将其作为练习留给读者。

AFL有两种模糊测试策略，一种是确定性策略，另一种是随机且混乱的策略。启动afl-fuzz实例时，可以指定希望该fuzz实例遵循的策略类型。一般而言，您只需要一个确定性（或主）模糊器，但是您可以使用盒子可以处理的任意数量（或从属）模糊器。如果您过去曾经使用过AFL，但不知道这是在说什么，那么您以前可能只运行过一个afl-fuzz实例。如果未指定模糊测试策略，则afl-fuzz实例将在每个策略之间来回切换。

```
afl-fuzz -i in -o out ./parse -M fuzzer1 -- ./parse
afl-fuzz -i in -o out ./parse -S fuzzer2 -- ./parse
```

命令中使用的参数-M和-S。 通过将-M fuzzer1传递给afl-fuzz，我告诉它是Master fuzzer（使用确定性策略），并且fuzz实例的名称为fuzzer1。 另一方面，传递给第二个命令的-S fuzzer2表示使用随机，混乱的策略并以fuzzer2的名称运行实例。 这两个模糊器将彼此配合工作，并在发现新的代码路径时来回传递新的测试用例。

# 什么时候结束

一旦模糊测试器运行了相对较长的时间（我想等到主模糊测试器至少完成它的第一个周期，从属实例通常到那时才完成许多周期），我们不应该只是停止工作并开始查看崩溃。在进行模糊测试时，AFL有望创建大量新的测试用例集，其中仍然可能存在漏洞。我们应该尽可能地减少这种新语料，然后重新播种我们的模糊器，让它们运行更多。这是没有演练讨论的过程，因为它很无聊，乏味并且可能需要很长时间，但是对于高效的模糊测试至关重要。

yaml-cpp解析二进制文件的主模糊器完成第一个周期（对我来说，这大约花了10个小时，对于一个普通的工作站来说，它可能要花24个小时），我们可以继续并停止我们的afl-fuzz实例。我们需要合并并最小化每个实例的队列，然后再次重新开始模糊测试。当使用多个模糊测试实例运行时，AFL将在您指定为afl-fuzz的参数的输出文件内部为每个模糊测试维护一个单独的同步目录。每个单独的模糊器输出文件都包含一个队列目录，其中包含AFL能够生成的所有测试用例，这些测试用例导致了值得检查的新代码路径。

我们需要合并每个模糊实例的队列目录，因为它们会有很多重叠，然后将这组新的测试数据最小化。

```
# cd out
# ls
fuzzer1 fuzzer2
# mkdir queue_all
# afl-cmin -i queue_all/ -o queue_cmin -- ../parse
corpus minimization tool for afl-fuzz by <lcamtuf@google.com>

[*] Testing the target binary...
[+] OK, 1780 tuples recorded.
[*] Obtaining traces for input files in 'queue_all/'...
    Processing file 7483/7483... 
[*] Sorting trace sets (this may take a while)...
[+] Found 37265 unique tuples across 7483 files.
[*] Finding best candidates for each tuple...
    Processing file 7483/7483... 
[*] Sorting candidate list (be patient)...
[*] Processing candidates and writing output files...
    Processing tuple 37265/37265... 
[+] Narrowed down to 1252 files, saved in 'queue_cmin'.

```

通过afl-cmin运行生成的队列后，我们需要最小化每个生成的文件，以免将CPU周期浪费在不需要的字节上。 但是，与仅仅最小化开始的测试用例相比，现在的文件要多得多。 一个用于最小化数千个文件的简单for循环可能需要几天的时间，而且没有人有时间这样做。 随着时间的流逝，我写了一个叫做afl-ptmin的小型bash脚本，该脚本将afl-tmin并行化为一定数量的进程，并被证明可以极大地提高速度。

```
#!/bin/bash

cores=$1
inputdir=$2
outputdir=$3
pids=""
total=`ls $inputdir | wc -l`

for k in `seq 1 $cores $total`
do
  for i in `seq 0 $(expr $cores - 1)`
  do
    file=`ls -Sr $inputdir | sed $(expr $i + $k)"q;d"`
    echo $file
    afl-tmin -i $inputdir/$file -o $outputdir/$file -- ~/parse &
  done

  wait
done
```

与afl-fuzz实例一样，我建议仍在屏幕会话中运行此实例，以免网络故障或关闭的终端引起您的痛苦和痛苦。 它的用法很简单，只需三个参数，即要启动的进程数，要最小化测试用例的目录以及要写入最小化的测试用例的输出目录。

```
~/afl-ptmin 8 ./queue_cmin/ ./queue/
```

即使进行了并行化，此过程仍可能需要一段时间（24小时以上）。 对于使用yaml-cpp生成的语料库，它应该能够在一个小时左右内完成。 完成后，我们应该从各个模糊器syncdir中删除先前的队列目录，然后复制队列/文件夹以替换旧的队列文件夹。

```
# rm -rf fuzzer1/queue
# rm -rf fuzzer2/queue
# cp -r queue/ fuzzer1/queue
# cp -r queue/ fuzzer2/queue

```

当有了新的队列是，我们可以重新开始fuzz.

````
#afl-fuzz -i- -o syncdir/ -S fuzzer2 -- ./parse
#afl-fuzz -i- -o syncdir/ -M fuzzer1 -- ./parse
````

如果您注意到了，我们没有在每次调用afl-fuzz时都将-i参数传递给目录以读取测试用例，而是简单地传递了一个连字符。 这告诉AFL仅将该模糊器的syncdir中的queue /目录用作种子目录，然后从那里开始备份。

整个过程可以启动模糊测试作业，然后停止以最小化队列，然后重新启动作业，可以根据您的需要进行多次（通常直到感到无聊或停止寻找新的代码路径为止）。 还应该经常这样做，因为否则您将浪费电费，浪费字节，以后再也不会付给您任何费用。

# 崩溃分类

模糊测试生命周期中另一个传统乏味的部分是对您的发现进行分类。 幸运的是，已经编写了一些很棒的工具来帮助我们。

一个很好的工具 crashwalk （by @rantyben），  它会自动执行gdb和一个特殊的gdb插件，以快速确定哪些崩溃可能导致可利用的条件，也可能不会导致可利用的条件。 无论如何，这并不是万无一失的方法，但是确实可以让您有一些先发制人的机会，在这种情况下，首先要集中精力应对崩溃。 安装它相对简单，但是我们首先需要一些依赖。

```
# apt-get install gdb golang
# mkdir src
# cd src
# git clone https://github.com/jfoote/exploitable.git
# cd && mkdir go
# export GOPATH=~/go
# go get -u github.com/bnagy/crashwalk/cmd/…
```



当crashwalk 安装在 ~/go/bin/ , 我们可以分析文件看它是否可能有可利用的bug。

```
# ~/go/bin/cwtriage -root syncdir/fuzzer1/crashes/ -match id -- ~/parse @@
```



# 确定有效性和代码覆盖率

查找崩溃是一件非常有趣的事情，但是，如果无法量化二进制文件中可用代码路径的运行状况，就像在黑暗中拍照一样。通过确认代码的哪个你没有到达你可以更好的调整测试用例来达到你没到达的地方。



一款名为afl-cov 的出色工具（by @michaelrash ） ， 以通过在查找新路径时观察模糊目录并立即运行测试用例来查找您可能遇到的代码库的新覆盖范围，从而帮助您解决此确切问题。它使用lcov完成此操作，因此在继续之前，我们实际上必须使用一些特殊选项重新编译解析二进制文件。

```
# cd ~/yaml-cpp/build/
# rm -rf ./*
# cmake -DCMAKE_CXX_FLAGS="-O0 -fprofile-arcs -ftest-coverage" \
-DCMAKE_EXE_LINKER_FLAGS="-fprofile-arcs -ftest-coverage" ..
# make
# cp util/parse ~/parse_cov
```

有了这个新的解析二进制文件，afl-cov可以将给定输入中二进制文件中采用的代码路径与文件系统上的代码链接起来。

```
afl-cov/afl-cov -d ~/syncdir/ --live --coverage-cmd "~/parse_cov AFL_FILE" --code-dir ~/yaml-cpp/ 
```



完成后，afl-cov在名为cov的目录中的根syncdir中生成报告信息。 这包括可以在Web浏览器中轻松查看的HTML文件，其中详细说明了哪些功能和代码行被命中，以及哪些功能和代码行未被命中。

# 最后


在花了三天的时间充实了这些之后，我发现yaml-cpp中没有潜在的可利用错误。 这是否意味着不存在任何错误，也不值得进行模糊测试？ 当然不是。 在我们的行业中，我认为关于漏洞发现方面的失败，我们发表的文章不够多。 许多人可能不想承认他们付出了很多精力和时间来完成某些事情，而其他人可能认为这是徒劳的。 本着开放的精神，下面链接的是所有生成的语料库（完全最小化），种子和代码覆盖率结果（约70％的代码覆盖率），以便其他人可以使用它们并确定是否值得进行模糊测试 。






> https://github.com/brandonprry/yaml-fuzz
>
> https://foxglovesecurity.com/2016/03/15/fuzzing-workflows-a-fuzz-job-from-start-to-finish/
