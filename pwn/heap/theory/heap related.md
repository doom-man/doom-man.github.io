[TOC]
# fast bin

# unsorted bin

# small bin

# large bin
## x32

组 | 数量 | 公差
---|---|---
1 | 32 | 64B
2 | 16 | 512B
3 | 8 | 4096B
4 | 4 | 32768B
5 | 2 | 262144B
6 | 1 | 不限制

第一个 large bin 的起始 chunk 大小为 512 字节，位于第一组，所以该 bin 可以存储的 chunk 的大小范围为 [512,512+64)。

large bins 中的每一个 bin 都包含一定范围内的 chunk，其中的 chunk 按 fd 指针的顺序从大到小排列。相同大小的 chunk 同样按照最近使用顺序排列。

# tcache