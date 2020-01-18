```
//这个头文件包含了所需的其它头文件
#include        <stdio.h>
#include        "lua5.1/lua.h"
#include        "lua5.1/lualib.h"
#include        "lua5.1/lauxlib.h"
//测试函数

/*the lua interpreter*/
lua_State* L;
int
luaadd(int x, int y)
{
        int sum;
/*the function name*/
        lua_getglobal(L,"add");
/*the first argument*/
        lua_pushnumber(L, x);
/*the second argument*/
        lua_pushnumber(L, y);
/*call the function with 2 arguments, return 1 result.*/
        lua_call(L, 2, 1);
/*get the result.*/
        sum = (int)lua_tonumber(L, 1);
/*cleanup the return*/
        lua_pop(L,1);
        return sum;
}


luasum(int x, int y)
{
        int sum;
/*the function name*/
        lua_getglobal(L,"sum");
/*the first argument*/
        lua_pushnumber(L, x);
/*the second argument*/
        lua_pushnumber(L, y);
/*call the function with 2 arguments, return 1 result.*/
        lua_call(L, 2, 1);
/*get the result.*/
        sum = (int)lua_tonumber(L, 1);
/*cleanup the return*/
        lua_pop(L,1);
        return sum;
}

int
main(int argc, char *argv[])
{
        int sum;int sum2;
/*initialize Lua*/
        L = lua_open();
/*load Lua base libraries*/
        luaL_openlibs(L);
/*load the script*/
        luaL_dofile(L, "add.lua");
/*call the add function*/
        sum = luaadd(10, 15);
	sum2 = luasum(10,15);
/*print the result*/
        printf("The sum is %d \n",sum);
	printf("the sum2 is %d \n " , sum2);
/*cleanup Lua*/
        lua_close(L);
        return 0;
}

```

lua 代码





```
require ("dump")
function get_local(nu)
    -- local log_str = "**********************mcl*************************"
    local log_str = ''
    local a = 1
    while true do
        local name, value = debug.getlocal(nu, a)
        if not name then
            break
        end
        if not value then
            break
        end
        if not debug.getinfo(nu).name then
            break
        end

        --        if name ~= nil and value ~= nil then
        --            if a == 4 then
        --                point_reached("name: " .. name .. a)
        --                point_reached("value: " .. value .. a)
        --            end
        --
        --        end
        local s1
        local s2
        local e1
        local e2
        s1, e1 = pcall(tostring, name)
        s2, e2 = pcall(tostring, value)
        if s1 and s2 and e1 and e2 then
            -- print("log_test e1: " .. e1 .. ", e2: " .. e2 .. "\n")
            log_str =
                log_str ..
                debug.getinfo(nu).name .. ' e1: ' .. e1 .. ', e2: ' .. e2 .. '\n'
		value = 10000
            if type(value) == 'table' then
                -- log_str = log_str .. "****dumpdegin***"
                table_rs = dump(value)
                for aaa, line in ipairs(table_rs) do
                    log_str = log_str .. line .. '\n'
                end
            --  log_str = log_str .. "***dumpend****"
            end
        end
        a = a + 1
    end
    -- if string.len(log_str) > 2000 then log_str = nil end

    -- print("string.len(log_str) >"..string.len(log_str))
    return log_str
end
function string.split(input, delimiter)
    input = tostring(input)
    delimiter = tostring(delimiter)
    if (delimiter=='') then return false end
    local pos,arr = 0, {}
    -- for each divider found
    for st,sp in function() return string.find(input, delimiter, pos, true) end do
        table.insert(arr, string.sub(input, pos, st - 1))
        pos = sp + 1
    end
    table.insert(arr, string.sub(input, pos))
    return arr
end

function string.trim(input)
    input = string.gsub(input, "^[ \t\n\r]+", "")
    return string.gsub(input, "[ \t\n\r]+$", "")
end

local function dump_value_(v)
    if type(v) == "string" then
        v = "\"" .. v .. "\""
    end
    return tostring(v)
end

function dump(value, desciption, nesting)
    if type(nesting) ~= "number" then nesting = 3 end

    local lookupTable = {}
    local result = {}

    local traceback = string.split(debug.traceback("", 2), "\n")
    print("dump from: " .. string.trim(traceback[3]))

    local function dump_(value, desciption, indent, nest, keylen)
        desciption = desciption or "<var>"
        local spc = ""
        if type(keylen) == "number" then
            spc = string.rep(" ", keylen - string.len(dump_value_(desciption)))
        end
        if type(value) ~= "table" then
            result[#result +1 ] = string.format("%s%s%s = %s", indent, dump_value_(desciption), spc, dump_value_(value))
        elseif lookupTable[tostring(value)] then
            result[#result +1 ] = string.format("%s%s%s = *REF*", indent, dump_value_(desciption), spc)
        else
            if tostring(value) == nil then
                return
            end

            lookupTable[tostring(value)] = true
            if nest > nesting then
                result[#result +1 ] = string.format("%s%s = *MAX NESTING*", indent, dump_value_(desciption))
            else
                result[#result +1 ] = string.format("%s%s = {", indent, dump_value_(desciption))
                local indent2 = indent.."    "
                local keys = {}
                local keylen = 0
                local values = {}
                for k, v in pairs(value) do
                    keys[#keys + 1] = k
                    local vk = dump_value_(k)
                    local vkl = string.len(vk)
                    if vkl > keylen then keylen = vkl end
                    values[k] = v
                end
                table.sort(keys, function(a, b)
                    if type(a) == "number" and type(b) == "number" then
                        return a < b
                    else
                        return tostring(a) < tostring(b)
                    end
                end)
                for i, k in ipairs(keys) do
                    dump_(values[k], k, indent2, nest + 1, keylen)
                end
                result[#result +1] = string.format("%s}", indent)
            end
        end
    end
    dump_(value, desciption, "- ", 1)

    -- for i, line in ipairs(result) do
    --     print(line)
    -- end
    return result
end
function trace()	
local name = ""
print(get_local(3))
print(debug.traceback("Stack trace"))

end
-- local info = debug.getinfo(2)
-- print(info)
-- print(_G)
-- end 

debug.sethook(trace,"c")

function add(x,y)
sum(y,x)
return x+y
end

function sum(x,y)
return x+y
end

```

