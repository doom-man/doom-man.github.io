# 1

```
[-] PROGRAM ABORT : Pipe at the beginning of 'core_pattern'
         Location : check_crash_handling(), afl-fuzz.c:7316
```

```
echo core >/proc/sys/kernel/core_pattern
```



# 2

```
[-] PROGRAM ABORT : Suboptimal CPU scaling governor
         Location : check_cpu_governor(), afl-fuzz.c:7378
```

```
cd /sys/devices/system/cpu echo performance | tee cpu*/cpufreq/scaling_governor

```





# 3

```
-- The CXX compiler identification is unknown
-- Check for working CXX compiler: /usr/local/bin/afl-clang-fast++
-- Check for working CXX compiler: /usr/local/bin/afl-clang-fast++ -- broken
CMake Error at /usr/share/cmake-3.10/Modules/CMakeTestCXXCompiler.cmake:45 (message):
  The C++ compiler

    "/usr/local/bin/afl-clang-fast++"

  is not able to compile a simple test program.

  It fails with the following output:

    Change Dir: /home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp
    
    Run Build Command:"/usr/bin/make" "cmTC_36df1/fast"
    /usr/bin/make -f CMakeFiles/cmTC_36df1.dir/build.make CMakeFiles/cmTC_36df1.dir/build
    make[1]: Entering directory '/home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp'
    Building CXX object CMakeFiles/cmTC_36df1.dir/testCXXCompiler.cxx.o
    /usr/local/bin/afl-clang-fast++     -o CMakeFiles/cmTC_36df1.dir/testCXXCompiler.cxx.o -c /home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp/testCXXCompiler.cxx
    #0 0x000055793a204018 llvm::sys::PrintStackTrace(llvm::raw_ostream&) (/home/pareto/llvm/build/bin/clang-3.8+0x1757018)
    #1 0x000055793a201ae6 llvm::sys::RunSignalHandlers() (/home/pareto/llvm/build/bin/clang-3.8+0x1754ae6)
    #2 0x000055793a201cf0 SignalHandler(int) (/home/pareto/llvm/build/bin/clang-3.8+0x1754cf0)
    #3 0x00007f86f2f2b890 __restore_rt (/lib/x86_64-linux-gnu/libpthread.so.0+0x12890)
    #4 0x0000557939d7bb20 llvm::BasicBlock::getFirstNonPHI() (/home/pareto/llvm/build/bin/clang-3.8+0x12ceb20)
    #5 0x0000557939d7bcd9 llvm::BasicBlock::getFirstInsertionPt() (/home/pareto/llvm/build/bin/clang-3.8+0x12cecd9)
    #6 0x00007f86f1dc8ec8 (anonymous namespace)::AFLCoverage::runOnModule(llvm::Module&) /home/pareto/workspace/AFL/llvm_mode/afl-llvm-pass.so.cc:121:36
    #7 0x0000557939e79e44 llvm::legacy::PassManagerImpl::run(llvm::Module&) (/home/pareto/llvm/build/bin/clang-3.8+0x13cce44)
    #8 0x000055793a33a2cf clang::EmitBackendOutput(clang::DiagnosticsEngine&, clang::CodeGenOptions const&, clang::TargetOptions const&, clang::LangOptions const&, llvm::StringRef, llvm::Module*, clang::BackendAction, llvm::raw_pwrite_stream*) (/home/pareto/llvm/build/bin/clang-3.8+0x188d2cf)
    #9 0x000055793a8c3e31 clang::BackendConsumer::HandleTranslationUnit(clang::ASTContext&) (/home/pareto/llvm/build/bin/clang-3.8+0x1e16e31)
    #10 0x000055793ac402ca clang::ParseAST(clang::Sema&, bool, bool) (/home/pareto/llvm/build/bin/clang-3.8+0x21932ca)
    #11 0x000055793a6379f6 clang::FrontendAction::Execute() (/home/pareto/llvm/build/bin/clang-3.8+0x1b8a9f6)
    #12 0x000055793a60a75c clang::CompilerInstance::ExecuteAction(clang::FrontendAction&) (/home/pareto/llvm/build/bin/clang-3.8+0x1b5d75c)
    #13 0x000055793a6cb30c clang::ExecuteCompilerInvocation(clang::CompilerInstance*) (/home/pareto/llvm/build/bin/clang-3.8+0x1c1e30c)
    #14 0x00005579391588e8 cc1_main(llvm::ArrayRef<char const*>, char const*, void*) (/home/pareto/llvm/build/bin/clang-3.8+0x6ab8e8)
    #15 0x000055793910e93d main (/home/pareto/llvm/build/bin/clang-3.8+0x66193d)
    #16 0x00007f86f1fedb97 __libc_start_main /build/glibc-OTsEL5/glibc-2.27/csu/../csu/libc-start.c:344:0
    #17 0x00005579391568aa _start (/home/pareto/llvm/build/bin/clang-3.8+0x6a98aa)
    Stack dump:
    0.	Program arguments: /home/pareto/llvm/build/bin/clang-3.8 -cc1 -triple x86_64-unknown-linux-gnu -emit-obj -disable-free -disable-llvm-verifier -main-file-name testCXXCompiler.cxx -mrelocation-model static -mthread-model posix -fmath-errno -masm-verbose -mconstructor-aliases -munwind-tables -fuse-init-array -target-cpu x86-64 -momit-leaf-frame-pointer -dwarf-column-info -debug-info-kind=limited -dwarf-version=4 -debugger-tuning=gdb -coverage-file /home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp/CMakeFiles/cmTC_36df1.dir/testCXXCompiler.cxx.o -resource-dir /home/pareto/llvm/build/bin/../lib/clang/3.8.0 -D __AFL_HAVE_MANUAL_CONTROL=1 -D __AFL_COMPILER=1 -D FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1 -D __AFL_LOOP(_A)=({ static volatile char *_B __attribute__((used));  _B = (char*)"##SIG_AFL_PERSISTENT##"; __attribute__((visibility("default"))) int _L(unsigned int) __asm__("__afl_persistent_loop"); _L(_A); }) -D __AFL_INIT()=do { static volatile char *_A __attribute__((used));  _A = (char*)"##SIG_AFL_DEFER_FORKSRV##"; __attribute__((visibility("default"))) void _I(void) __asm__("__afl_manual_init"); _I(); } while (0) -internal-isystem /usr/lib/gcc/x86_64-linux-gnu/7.5.0/../../../../include/c++/7.5.0 -internal-isystem /usr/lib/gcc/x86_64-linux-gnu/7.5.0/../../../../include/x86_64-linux-gnu/c++/7.5.0 -internal-isystem /usr/lib/gcc/x86_64-linux-gnu/7.5.0/../../../../include/x86_64-linux-gnu/c++/7.5.0 -internal-isystem /usr/lib/gcc/x86_64-linux-gnu/7.5.0/../../../../include/c++/7.5.0/backward -internal-isystem /usr/local/include -internal-isystem /home/pareto/llvm/build/bin/../lib/clang/3.8.0/include -internal-externc-isystem /usr/include/x86_64-linux-gnu -internal-externc-isystem /include -internal-externc-isystem /usr/include -O3 -fdeprecated-macro -fdebug-compilation-dir /home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp -ferror-limit 19 -fmessage-length 0 -funroll-loops -fobjc-runtime=gcc -fcxx-exceptions -fexceptions -fdiagnostics-show-option -vectorize-loops -vectorize-slp -load /usr/local/lib/afl/afl-llvm-pass.so -o CMakeFiles/cmTC_36df1.dir/testCXXCompiler.cxx.o -x c++ /home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp/testCXXCompiler.cxx 
    1.	<eof> parser at end of file
    2.	Per-module optimization passes
    3.	Running pass 'Unnamed pass: implement Pass::getPassName()' on module '/home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp/testCXXCompiler.cxx'.
    clang-3.8: error: unable to execute command: Segmentation fault (core dumped)
    clang-3.8: error: clang frontend command failed due to signal (use -v to see invocation)
    clang version 3.8.0 (tags/RELEASE_380/final)
    Target: x86_64-unknown-linux-gnu
    Thread model: posix
    InstalledDir: /home/pareto/llvm/build/bin
    clang-3.8: note: diagnostic msg: PLEASE submit a bug report to http://llvm.org/bugs/ and include the crash backtrace, preprocessed source, and associated run script.
    clang-3.8: note: diagnostic msg: 
    ********************
    
    PLEASE ATTACH THE FOLLOWING FILES TO THE BUG REPORT:
    Preprocessed source(s) and associated run script(s) are located at:
    clang-3.8: note: diagnostic msg: /tmp/testCXXCompiler-c0067f.cpp
    clang-3.8: note: diagnostic msg: /tmp/testCXXCompiler-c0067f.sh
    clang-3.8: note: diagnostic msg: 
    
    ********************
    CMakeFiles/cmTC_36df1.dir/build.make:65: recipe for target 'CMakeFiles/cmTC_36df1.dir/testCXXCompiler.cxx.o' failed
    make[1]: *** [CMakeFiles/cmTC_36df1.dir/testCXXCompiler.cxx.o] Error 254
    make[1]: Leaving directory '/home/pareto/yaml-cpp/build/CMakeFiles/CMakeTmp'
    Makefile:126: recipe for target 'cmTC_36df1/fast' failed
    make: *** [cmTC_36df1/fast] Error 2
    

  

  CMake will not be able to correctly generate this project.
Call Stack (most recent call first):
  CMakeLists.txt:3 (project)


-- Configuring incomplete, errors occurred!
See also "/home/pareto/yaml-cpp/build/CMakeFiles/CMakeOutput.log".
See also "/home/pareto/yaml-cpp/build/CMakeFiles/CMakeError.log".

```

