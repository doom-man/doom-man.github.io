[TOC]
# 示例代码
```
#include <stdio.h>


int main(void){
    char buf[20] = "mcl";
    printf("%s\n",buf);
    write(1,"mcl",4);
    return 0;
}
```

printf 处打断点，开始运行。
# _IO_list_all

_flags 标志位有如下字段
```
#define _IO_MAGIC         0xFBAD0000 /* Magic number */
#define _IO_MAGIC_MASK    0xFFFF0000
#define _IO_USER_BUF          0x0001 /* Don't deallocate buffer on close. */
#define _IO_UNBUFFERED        0x0002
#define _IO_NO_READS          0x0004 /* Reading not allowed.  */
#define _IO_NO_WRITES         0x0008 /* Writing not allowed.  */
#define _IO_EOF_SEEN          0x0010
#define _IO_ERR_SEEN          0x0020
#define _IO_DELETE_DONT_CLOSE 0x0040 /* Don't call close(_fileno) on close.  */
#define _IO_LINKED            0x0080 /* In the list of all open files.  */
#define _IO_IN_BACKUP         0x0100
#define _IO_LINE_BUF          0x0200
#define _IO_TIED_PUT_GET      0x0400 /* Put and get pointer move in unison.  */
#define _IO_CURRENTLY_PUTTING 0x0800
#define _IO_IS_APPENDING      0x1000
#define _IO_IS_FILEBUF        0x2000
                           /* 0x4000  No longer used, reserved for compat.  */
#define _IO_USER_LOCK         0x8000
```
查看 _IO_list_all 

```
gdb-peda$ p *_IO_list_all
$2 = {
  file = {
    _flags = 0xfbad2086, 
    _IO_read_ptr = 0x0, 
    _IO_read_end = 0x0, 
    _IO_read_base = 0x0, 
    _IO_write_base = 0x0, 
    _IO_write_ptr = 0x0, 
    _IO_write_end = 0x0, 
    _IO_buf_base = 0x0, 
    _IO_buf_end = 0x0, 
    _IO_save_base = 0x0, 
    _IO_backup_base = 0x0, 
    _IO_save_end = 0x0, 
    _markers = 0x0, 
    _chain = 0x7ffff7dd2620 <_IO_2_1_stdout_>, 
    _fileno = 0x2, 
    _flags2 = 0x0, 
    _old_offset = 0xffffffffffffffff, 
    _cur_column = 0x0, 
    _vtable_offset = 0x0, 
    _shortbuf = "", 
    _lock = 0x7ffff7dd3770 <_IO_stdfile_2_lock>, 
    _offset = 0xffffffffffffffff, 
    _codecvt = 0x0, 
    _wide_data = 0x7ffff7dd1660 <_IO_wide_data_2>, 
    _freeres_list = 0x0, 
    _freeres_buf = 0x0, 
    __pad5 = 0x0, 
    _mode = 0x0, 
    _unused2 = '\000' <repeats 19 times>
  }, 
  vtable = 0x7ffff7dd06e0 <_IO_file_jumps>
}

```
各个_IO_FILE 通过 _chain 连接。我们访问到下一个_IO_FIlE
```
gdb-peda$ p *(struct _IO_FILE *)0x7ffff7dd2620
$4 = {
  _flags = 0xfbad2084, 
  _IO_read_ptr = 0x0, 
  _IO_read_end = 0x0, 
  _IO_read_base = 0x0, 
  _IO_write_base = 0x0, 
  _IO_write_ptr = 0x0, 
  _IO_write_end = 0x0, 
  _IO_buf_base = 0x0, 
  _IO_buf_end = 0x0, 
  _IO_save_base = 0x0, 
  _IO_backup_base = 0x0, 
  _IO_save_end = 0x0, 
  _markers = 0x0, 
  _chain = 0x7ffff7dd18e0 <_IO_2_1_stdin_>, 
  _fileno = 0x1, 
  _flags2 = 0x0, 
  _old_offset = 0xffffffffffffffff, 
  _cur_column = 0x0, 
  _vtable_offset = 0x0, 
  _shortbuf = "", 
  _lock = 0x7ffff7dd3780 <_IO_stdfile_1_lock>, 
  _offset = 0xffffffffffffffff, 
  _codecvt = 0x0, 
  _wide_data = 0x7ffff7dd17a0 <_IO_wide_data_1>, 
  _freeres_list = 0x0, 
  _freeres_buf = 0x0, 
  __pad5 = 0x0, 
  _mode = 0x0, 
  _unused2 = '\000' <repeats 19 times>
}

```
由于此时没有执行标准输出操作，所以ptr 都指向NULL，n执行下一步，此时IO_file 指向堆分配的缓冲区
```
gdb-peda$ p *(struct _IO_FILE *)0x7ffff7dd2620
$5 = {
  _flags = 0xfbad2a84, 
  _IO_read_ptr = 0x602010 "mcl\n", 
  _IO_read_end = 0x602010 "mcl\n", 
  _IO_read_base = 0x602010 "mcl\n", 
  _IO_write_base = 0x602010 "mcl\n", 
  _IO_write_ptr = 0x602010 "mcl\n", 
  _IO_write_end = 0x602010 "mcl\n", 
  _IO_buf_base = 0x602010 "mcl\n", 
  _IO_buf_end = 0x602410 "", 
  _IO_save_base = 0x0, 
  _IO_backup_base = 0x0, 
  _IO_save_end = 0x0, 
  _markers = 0x0, 
  _chain = 0x7ffff7dd18e0 <_IO_2_1_stdin_>, 

```