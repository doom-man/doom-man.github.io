添加代码

```
  char buf[2000]={};
  for(int i = 0 ; i <cc_par_cnt; i++ ){
        strncat(buf,cc_params[i],strlen(cc_params));
        buf[strlen(buf)] = ' ';

  }
  FATAL("%s",buf);
  
```



```
[-] PROGRAM ABORT : gcc -O3 -funro -Wall -D_FOR -g -Wno-p -DAFL_ -DDOC_ -DBIN_ test-i -o test-i -ldl -B . -g -O3 -funro -D__AF -DFUZZ 
```