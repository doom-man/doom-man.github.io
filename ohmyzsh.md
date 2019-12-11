我丢,用了那么久的linux 居然居然没有用过ohmyzsh, 插件使用简单.
# 下载安装
首先要安装zsh
```
sudo apt-get install zsh
```
安装oh my zsh
```
sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
```
中途会让你选择是否替代默认bash ,替代就好. 安装完成

# 插件安装
```
plugins=(git)
olugins=(wd)

```
直接添加在 ~/.zshrc  里面再
```
source ~/.zshrc
```
就ok
界面简洁
![image.png](https://upload-images.jianshu.io/upload_images/15133848-80e527ec222a2c5b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

# 主题
 [主题](https://github.com/ohmyzsh/ohmyzsh/wiki/Themes)

# 卸载
要是用久了不喜欢了,该命令切换shell.
```
chsh -s /bin/zsh
```
卸载ohmyzsh
```
uninstall_oh_my_zsh
```