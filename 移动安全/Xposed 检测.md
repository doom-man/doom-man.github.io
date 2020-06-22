
[TOC]
# [XposedChecker](https://github.com/w568w/XposedChecker)


## 载入Xposed工具类(java层)

```
        try {
            ClassLoader.getSystemClassLoader()
                                .loadClass("de.robv.android.xposed.XposedHelpers");

            return true;
        }
                catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
```



## 寻找特征动态链接库

```
    try {
        HashSet<String> localObject = new HashSet<>();
        // 读取maps文件信息
        BufferedReader localBufferedReader =
    new BufferedReader(new FileReader("/proc/" + Process.myPid() + "/maps"));
        while (true) {
            String str = localBufferedReader.readLine();
            if (str == null) {
                break;
            }
            localObject.add(str.substring(str.lastIndexOf(" ") + 1));
        }
        //应用程序的链接库不可能是空，除非是高于7.0。。。
        if (localObject.isEmpty() && Build.VERSION.SDK_INT <= Build.VERSION_CODES.M) {
            return true;
        }
        localBufferedReader.close();
        for (String aLocalObject : localObject) {
            if (aLocalObject.contains(paramString)) {
                return true;
            }
        }
    }
catch (Throwable ignored) {
    }
    return false;
```

## 代码堆栈寻找调起者

```
private int check3() {
        try {
            throw new Exception();
        }
                catch (Exception e) {
            StackTraceElement[] arrayOfStackTraceElement = e.getStackTrace();
            for (StackTraceElement s : arrayOfStackTraceElement) {
                if ("de.robv.android.xposed.XposedBridge".equals(s.getClassName())) {
                    return 1;
                }
            }
            return 0;
        }
    }
```



## 检测Xposed安装情况
```
try {
            List<PackageInfo> list = getPackageManager().getInstalledPackages(0);
            for (PackageInfo info : list) {
                if ("de.robv.android.xposed.installer".equals(info.packageName)) {
                    return 1;
                }
                if ("io.va.exposed".equals(info.packageName)) {
                    return 1;
                }
            }
        }
                catch (Throwable ignored) {

        }
```

## 判定系统方法调用钩子
```
        try {
            Method method = Throwable.class.getDeclaredMethod("getStackTrace");
            return Modifier.isNative(method.getModifiers()) ? 1 : 0;
        }
                catch (NoSuchMethodException e) {
            e.printStackTrace();
        }
```

## 检测虚拟Xposed环境
```
    return System.getProperty("vxp") != null ? 1 : 0;
```

## 寻找Xposed运行库文件
```
CommandResult commandResult = Shell.run("ls /system/lib");
	return commandResult.isSuccessful() ? 						   commandResult.getStdout().contains("xposed") ? 1 : 0 : 0;
```

## 内核查找Xposed链接库
```
        FILE * maps;
        char path[80];
        char * content;
        strcpy (path,"/proc/");
        strcat (path,pid);
        strcat (path,"/maps");
        if((maps=fopen(path,"r"))==NULL){
                return 0;
        }else{
                int len=filelength(maps);
                content=(char *)malloc(len);
                fread(content,len,1,maps);
                content[len-1]='\0';
                return strstr(content,"XposedBridge")!=NULL;
        }
```

## 环境变量特征字判断
```
	return System.getenv("CLASSPATH").contains("XposedBridge") ? 1 : 0;
```