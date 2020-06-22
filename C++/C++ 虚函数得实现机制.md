C++中的虚函数的作用主要是实现了多态的机制。

### 虚函数表

对C++ 了解的人都应该知道虚函数（Virtual Function）是通过一张虚函数表（Virtual Table）来实现的。简称为V-Table。 在这个表中，主是要一个类的虚函数的地址表，这张表解决了继承、覆盖的问题，保证其容真实反应实际的函数。这样，在有虚函数的类的实例中这个表被分配在了 这个实例的内存中，所以，当我们用父类的指针来操作一个子类的时候，这张虚函数表就显得由为重要了，它就像一个地图一样，指明了实际所应该调用的函数。

这里我们着重看一下这张虚函数表。在C++的标准规格说明书中说到，编译器必需要保证虚函数表的指针存在于对象实例中最前面的位置（这是为了保证正确取到虚函数的偏移量）。 这意味着我们通过对象实例的地址得到这张虚函数表，然后就可以遍历其中函数指针，并调用相应的函数。

```
#include <iostream>
using namespace std;

class Base {

public:

	virtual void f() { cout << "Base::f" << endl; }

	virtual void g() { cout << "Base::g" << endl; }

	virtual void h() { cout << "Base::h" << endl; }

};

class Derive:Base{
public:
	virtual void f1() { cout << "Base::f1" << endl; }

	virtual void g1() { cout << "Base::g1" << endl; }

	virtual void h1() { cout << "Base::h1" << endl; }
};

int main(void) {
	typedef void(*Fun)(void);
	Fun pFun = NULL;
	Base b;

	cout << "父类虚函数表地址：" << (int*)(&b) << endl;

	cout << "父类虚函数表 — 第一个函数地址：" << (int*)*(int*)(&b) << endl;
	
	Derive d;

	cout << "父类虚函数表地址：" << (int*)(&d) << endl;

	cout << "父类虚函数表 — 第一个函数地址：" << (int*)*(int*)(&d) << endl;

	Derive d2;

	cout << "父类虚函数表地址：" << (int*)(&d2) << endl;

	cout << "父类虚函数表 — 第一个函数地址：" << (int*)*(int*)(&d2) << endl;
	
	((Fun)*((int*)*(int*)(&b) + 0))(); // Base::f()

	((Fun)*((int*)*(int*)(&b) + 1))(); // Base::g()

	((Fun)*((int*)*(int*)(&b) + 2))(); // Base::h()

	//((Fun)*((int*)*(int*)(&b) + 3))(); // Base::f()

	//((Fun)*((int*)*(int*)(&b) + 4))(); // Base::g()

	//((Fun)*((int*)*(int*)(&b) + 5))(); // Base::h()

	return 0;
 }
```

运行结果：

```
父类虚函数表地址：004FFC9C
父类虚函数表 — 第一个函数地址：00FC9B34
父类虚函数表地址：004FFC90
父类虚函数表 — 第一个函数地址：00FC9C4C
父类虚函数表地址：004FFC84
父类虚函数表 — 第一个函数地址：00FC9C4C
Base::f
Base::g
Base::h
```

### 一般继承（有虚函数覆盖）

![o_vtable3](J:\gitproject\doom-man.github.io\res\pic\o_vtable3.JPG)



> https://blog.csdn.net/neiloid/article/details/6934135