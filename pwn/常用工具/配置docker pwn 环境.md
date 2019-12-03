[TOC]
# 卸载旧版本
```
sudo apt-get remove docker docker-engine docker.io containerd runc
```
# 使用Docker 仓库进行安装
## 设置仓库
更新apt包索引
```
sudo apt-get update
```

安装 apt 依赖包，用于通过HTTPS来获取仓库:
```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
```
添加docker官方的GPG密钥：
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -


```
9DC8 5822 9FC7 DD38 854A E2D8 8D81 803C 0EBF CD88 通过搜索指纹的后8个字符，验证您现在是否拥有带有指纹的密钥。
```
sudo apt-key fingerprint 0EBFCD88
   
pub   rsa4096 2017-02-22 [SCEA]
      9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88
uid           [ unknown] Docker Release (CE deb) <docker@docker.com>
sub   rsa4096 2017-02-22 [S]
```
使用以下指令设置稳定版仓库
```
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) \
  stable"
  

```

## 安装 Docker Engine-Community
更新apt索引
```
sudo apt-get update
```
安装最新版本的 Docker Engine-Community 和 containerd ，或者转到下一步安装特定版本：
```
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
要安装特定版本的 Docker Engine-Community，请在仓库中列出可用版本，然后选择一种安装。列出您的仓库中可用的版本：
```
apt-cache madison docker-ce
```
官方源下载太慢了,换成中科大源
```
sudo add-apt-repository "deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs) stable" 
```
修改/etc/apt/souces.list文件删除官方源仅保留中科大源。

重新下载速度飞起。
```
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
# docker 指令
```
run 创建新容器并运行一个命令

-d  后台运行容器并打印id
-h  指定容器名称
--name 给容器分配昵称
-v 绑定挂载指定卷
-p 开放一个容器端口给主机
--cap-add 增加linux功能

exec 在容器中执行命令
-d 后台运行
-i 没有附加也保持stdin 打开
-t 分配一个伪终端


```
# 下载镜像
(pwddocker)[https://github.com/skysider/pwndocker]
pwndocker 下配置启动脚本
```
dra@ubuntu:~/docker_pwn/pwndocker$ ls
Dockerfile  LICENSE.md  linux_server  linux_server64  pip.conf  pwn  README.md  sources.list  start.sh

#cat start.sh

sudo docker run -d --rm -h pwn --name pwn -v ~/ctf:/ctf/work -p 23946:23946 --cap-add=SYS_PTRACE skysider/pwndocker

```
要修改成自己的路径 -v 指定挂载目录 -p 映射docker端口到主机端口

```
sudo docker run -d \
        --rm -h pwn \
        --name pwn \
        -v $(pwd):/ctf/work \
        -v ~/ctf:/ctf/pwn \
        -p 23946:23946 \
        --cap-add=SYS_PTRACE \
        skysider/pwndocker

```
进入伪终端
```
sudo docker exec -it pwn /bin/sh
```

[pwndocker](https://github.com/skysider/pwndocker)

[reference](https://www.anquanke.com/post/id/187922#h3-6)
