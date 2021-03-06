[TOC]

# 虚拟化技术简介

## 介绍

在这篇文章，我希望展示虚拟化技术的基础知识。最近我搜寻了一个新的研究主题然后我想起我并不了解虚拟化技术，也不了解在我打开我从VMware Workstation打开ubuntu虚拟机时发生了什么。

首先，我们将介绍为什么要使用它，有关主题的历史，不同类型的虚拟化和管理程序 ，一些用于高效虚拟化的技术，还有一些关于内存虚拟化的技术。

## 为什么要使用

假设一个公司提供多种服务，每种服务需要使用运行在不同的操作系统，如果我们使用虚拟化技术只需要一个物理机并且安装各种操作系统，这样我们节约了金钱和物理空间。

## 不同类型的Hypervisors

我们区分两种不同类型的Hypervisor ， 如图：

![hypervisor_types](J:\gitproject\doom-man.github.io\res\pic\hypervisor_types.png)

第一种类型，hypervisor 直接安装在硬件，在其之上就是一些操作系统。这种被称为裸机(bare metal) 。例如微软的Hyper-V 就是这种类型。

第二种类型很明显的不同，第一，他安装在操作系统之上，并且除了hypervisor 还有其他进程在运行在同一层。第二点不是完全正确，以VMware为例，当运行一个VM实例时可以看到一个进程叫VMX，是VMware的一个进程，它在后台与VMM driver 协作。所以VMware 仅出现在用户进程，

### 不同类型的虚拟化

共有三种虚拟化类型： 完全虚拟化、半虚拟化和硬件辅组虚拟化(HAV)。

* 完全虚拟化 - 不改变客户机操作系统的技术，使用二进制转换(binary translation)的技术实现
* 半虚拟化 - 这种技术，操作系统内核会被修改，这种修改不会提升操作系统运行速度但会导致不再能运行任意的操作系统，因为安装的操作系统必须要有半虚拟化驱动，例如"Xen 1.0"
* HAV - 这种类型代表一个新方法，使用半虚拟化技术，你必须改变客户机系统内核，HAV 你需要有特殊的硬件，比如额外的ISA指令。这种技术在现在很常见，比如"Microsoft Hyper-V"

## 内存虚拟化

**GVA** - guest virtual address
**GPA** - guest physical address
**MVA** - machine virtual address
**MPA** - machine physical address

VM A 分配了虚拟页5和6 ， 管理程序把他们匹配到 7 和 8 物理页，在另一个虚拟机想要分配页数时，管理程序怎么指导哪一个分配给哪个虚拟机。

我们想要找到一种方法可以匹配客户机的虚拟页和宿主机的物理页并且不需要重写其他虚拟机的页数，基本上想管理一个真正的电脑并且每个虚拟机就像一个进程。

一种软件辅助的解决方案是影子页表( **Shadow Page Table**),它的目的是完成从GBA到MPA的映射，所以对于每个虚拟机，管理程序会创建一个他的影子页表。

![shadow_page_tables](J:\gitproject\doom-man.github.io\res\pic\shadow_page_tables.gif)

客户机可以通过写内存来改变映射关系，而不需要任何的敏感操作，所以管理程序不知道改变并且影子页表不会同步就失去了作用(大概就是客户机没有将页表隔离出来吧，客户机可以直接修改映射关系。)

一个解决方法在全虚拟化环境下管理程序将客户机页表映射为只读，因此导致的页错误会让管理程序去处理和更新影子页表。

在半虚拟化环境，客户机可以在其完成该表页表后让管理程序知道，

> https://yuvaly0.github.io/2020/06/19/introduction-to-virtualization.html