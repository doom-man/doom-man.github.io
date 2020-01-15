远程服务器安装git 

```
sudo apt-get install git
```

本地创建远程仓库(远程必须有对应仓库)
```
git remote add origin ssh://xxx@192.168.1.32/~/workspace/code_celloct/gittest

```
本地clone

```
 git clone root@47.108.202.176:~/My_Kernel-4.10.1
```





...... 写到这里写不下去, 都是重复的之前的git命令, 只是创建远程仓库的时候需要自己去远程服务器创建 . 
写一个shell 脚本来跑需要环境 
下载expect 脚本.用来实现shell的交互

```
sudo apt-get install expect
```
shell 脚本
```
pass_word="*******"
ip="47.75.56.196"
user_name="root"
expect <<EOF
        spawn scp -r root@47.75.56.196:~/a.out ./
        expect {
                "password: " { send "$pass_word\n"}
        }
        expect eof
EOF
ls
```

