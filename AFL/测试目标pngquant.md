发现AFL-fuzz 不能直接去测试类似于菜单功能的程序,所以在开源项目中找到pngquant ,一种png损失压缩的工具.
# pngquant 源码分析
## main函数分析
```
int main(int argc , char * argv[])
```
1. 传入命令行选项解析，保存返回值。
2. 根据选项执行相应操作。
3. 文件解析 。

## 文件解析
```
pngquant_error pngquant_main_internal(struct pngquant_options *options, liq_attr *liq)
```
1. 使用 #pragma omp parallel for 并行运行,

   ```c
   #pragma omp parallel for schedule(static, 1) reduction(+:skipped_count) reduction(+:error_count) reduction(+:file_count) shared(latest_error)
   ```
reduction() 保证并行运行结果正确性。
2. 调用pngquant_file_internal
```
static pngquant_error pngquant_file_internal(const char *filename, const char *outname, struct pngquant_options *options, liq_attr *liq)
```
1. 读取图片
2. 图片量化（pngquant核心部分liq_image_quantize）
3. 写图片





fuzz 测试过程中遇见了两个问题

1. pngquat 压缩文件时，可能存在检查，当传入压缩过文件以后，pngquant直接返回该文件。
2. afl-fuzz 过程中输入的文件没有发生变异（依据是查看out/queue 文件下的文件仅有给定文件，且last new path 长时间未更新）





# REFERENCE

> https://blog.csdn.net/gengshenghong/article/details/7000685