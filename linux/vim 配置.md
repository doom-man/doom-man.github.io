
在vundle插件管理的方式，直接在~/.vimrc中的Plugin段落中加入`Plugin "scrooloose/nerdtree
"然后重启Vim并输入PluginInstall`，即可完成安装

.vimrc 配置文件
```
set expandtab
set autoindent
map <F3> :NERDTreeToggle<CR>
let g:NERDTreeWinSize = 25

set nocompatible              " 这是必需的
filetype off                  " 这是必需的
" 在此设置运行时路径
set rtp+=~/.vim/bundle/Vundle.vim
" vundle初始化
call vundle#begin()
" 或者传递一个 Vundle 安装插件的路径
"call vundle#begin('~/some/path/here')

" 让 Vundle 管理 Vundle, 必须
Plugin 'VundleVim/Vundle.vim'

" 下面是不同支持幅度的例子
" 保持 Plugin 命令 在 vundle#begin 和 end 之间
" plugin 在 GitHub 仓库
" Plugin 'tpope/vim-fugitive'
" 来自http://vim-scripts.org/vim/scripts.html的插件
" Plugin 'L9'
" 未托管在GitHub上的Git插件
" Plugin 'git://git.wincent.com/command-t.git'
" 本地机器上的git软件库（即编写自己的插件时）
" Plugin 'file:///home/gmarik/path/to/plugin'
" sparkup vim脚本在名为vim的该软件库子目录下。
" 传递路径，合理设置运行时路径。
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
" 安装 L9 并避免名称冲突
" different version somewhere else.
" Plugin 'ascenator/L9', {'name': 'newL9'}
Plugin 'scrooloose/nerdtree'

"每个插件都应该在这一行之前
call vundle#end()            " 这是必需的
filetype plugin indent on    " 这是必需的
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for 
```

切换工作台和目录
```
ctrl + w + h    光标 focus 左侧树形目录
ctrl + w + l    光标 focus 右侧文件显示窗口
ctrl + w + w    光标自动在左右侧窗口切换
ctrl + w + r    移动当前窗口的布局位置

o       在已有窗口中打开文件、目录或书签，并跳到该窗口
go      在已有窗口 中打开文件、目录或书签，但不跳到该窗口
t       在新 Tab 中打开选中文件/书签，并跳到新 Tab
T       在新 Tab 中打开选中文件/书签，但不跳到新 Tab
i       split 一个新窗口打开选中文件，并跳到该窗口
gi      split 一个新窗口打开选中文件，但不跳到该窗口
s       vsplit 一个新窗口打开选中文件，并跳到该窗口
gs      vsplit 一个新 窗口打开选中文件，但不跳到该窗口
!       执行当前文件
O       递归打开选中 结点下的所有目录
m    文件操作：复制、删除、移动等
```

切换标签页
```
:tabnew [++opt选项] ［＋cmd］ 文件      建立对指定文件新的tab
:tabc   关闭当前的 tab
:tabo   关闭所有其他的 tab
:tabs   查看所有打开的 tab
:tabp   前一个 tab
:tabn   后一个 tab

标准模式下：
gT      前一个 tab
gt      后一个 tab
```

