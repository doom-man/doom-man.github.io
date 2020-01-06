# 环境搭建
## 下载编译源码
```
apt-get install lua5.2 lua5.2-doc
```
end
### 函数
```
luaL_loadbuffer
载入并编译内存中的一段lua代码，然后作为一个代码块(称为chunk)压入栈中，其中最后一个参数作为代码 块的名称用于调试。

类似的函数 
loadL_loadfile(载入文件),luaL_loadstring(载入字符串)，luaL_loadbuff(载入缓冲区) 这些函数是同一函数的不同封装。

lua_pcall 从从栈顶取得函数并执行，出错，则返回一个非0值并把错误信息压入栈顶。

```
实例代码
```
extern "C" {
#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"
}
 
#include <iostream>
#include <string>
using namespace std;
int main()
{

//Lua示例代码
char *szLua_code =
"r = string.gsub(c_Str, c_Mode, c_Tag) --宿主给的变量 "
"u = string.upper(r)";
//Lua的字符串模式
char *szMode = "(%w+)%s*=%s*(%w+)";
//要处理的字符串
char *szStr = "key1 = value1 key2 = value2";
//目标字符串模式
char *szTag = "<%1>%2</%1>";
lua_State *L = luaL_newstate();
luaL_openlibs(L);
//把一个数据送给Lua
lua_pushstring(L, szMode);
lua_setglobal(L, "c_Mode");
lua_pushstring(L, szTag);
lua_setglobal(L, "c_Tag");
lua_pushstring(L, szStr);
lua_setglobal(L, "c_Str");
//执行
bool err = luaL_loadbuffer(L, szLua_code, strlen(szLua_code),
"demo") || lua_pcall(L, 0, 0, 0);
if(err)
{
//如果错误，显示
cerr << lua_tostring(L, -1);
//弹出栈顶的这个错误信息
lua_pop(L, 1);
}
else
{
//Lua执行后取得全局变量的值
lua_getglobal(L, "r");
cout << "r = " << lua_tostring(L,-1) << endl;
lua_pop(L, 1);
lua_getglobal(L, "u");
cout << "u = " << lua_tostring(L,-1) << endl;    
lua_pop(L, 1);
}
lua_close(L);
return 0;
}
```
## lua、luac、luaJIT三种文件的关系
在学习lua手游过程中，本人遇到的lua文件大部分是这3种。其中lua是明文代码，直接用记事本就能打开，luac是lua编译后的字节码，文件头为0x1B 0x4C 0x75 0x61 0x51，lua虚拟机能够直接解析lua和luac脚本文件，而luaJIT是另一个lua的实现版本（不是原作者写的），JIT是指Just-In-Time（即时解析运行），luaJIT相比lua和luac更加高效，文件头是0x1B 0x4C 0x4A。
luac:
```
1B 4C 75 61   .LuaQ
```
luajit:
```
1B 4C 4A .LJ
```



> reference 
> https://bbs.pediy.com/thread-216969.htm