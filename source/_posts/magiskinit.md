---
title: magiskinit
date: 2024-03-26 19:33:20
tags: magisk,android
---

#  magiskinit 原理探究

测试设备：pixel 7 pro

magisk 版本： 27000



从流程上看

1. 安装magisk apk，使用magisk修补init_boot.img
2. 将修补后的init_boot.img 刷入手机
3. 重启手机， 完成root

想要理解为什么，我认为有两个目标：

1. 理解init_boot.img 在android 发挥的作用 
2. 被修改后的镜像，做了哪些特殊行为



## magisk debug环境搭建

能对magisk init插入一些日志，验证分析。

1. 官网安装debug版本的magisk 。
2. clone magisk 的源码，参考[文档](https://topjohnwu.github.io/Magisk/build.html)，搭建好编译环境
3. 编译apk ，将编译的apk 重命名为zip 通过magisk刷入到手机，安装成功。
4. 重启设备，查看magiskinit日志。

```bash
dmesg | grep magiskinit
```

```
[    0.433073] magiskinit: Device config:
[    0.433085] magiskinit: skip_initramfs=[0]
[    0.433092] magiskinit: force_normal_boot=[1]
[    0.433098] magiskinit: rootwait=[0]
[    0.433104] magiskinit: slot=[_a]
[    0.433111] magiskinit: dt_dir=[/proc/device-tree/firmware/android]
[    0.433117] magiskinit: fstab_suffix=[]
[    0.433122] magiskinit: hardware=[cheetah]
```



## 理解init_boot.img 的作用

[''android对bootloader行为的说明"](https://source.android.com/docs/core/architecture/bootloader )说到 ，bootloader 加载init_boot.img, boot.img 。

1. 将内核加载内存，并且在内存中执行
2. 加载ramdisks和bootconfig 到内存创建initramfs

其中ramdisk 就在init_boot.img ，ramdisk中有init 进程 ，内核启动后，会执行initramfs  根目录的/init，进行第一阶段，完成目录挂载、系统环境的搭建后，切换根目录到/system , 执行/system/bin/init 开始第二阶段，初始化用户态环境 ，继续启动系统。init的这个过程就是2SI。

这里理解init_boot.img 提供initramfs 环境 、init程序。



## 修补init_boot.img

分析源码，修补镜像功能所在代码com/topjohnwu/magisk/core/tasks/MagiskInstaller.kt > MagiskInstallImpl。

核心功能**patchBoot**：

```kotlin
        val cmds = arrayOf(
            "cd $installDir",
            "KEEPFORCEENCRYPT=${Config.keepEnc} " +
            "KEEPVERITY=${Config.keepVerity} " +
            "PATCHVBMETAFLAG=${Info.patchBootVbmeta} " +
            "RECOVERYMODE=${Config.recovery} " +
            "LEGACYSAR=${Info.legacySAR} " +
            "sh boot_patch.sh $srcBoot")
        val isSuccess = cmds.sh().isSuccess
```

准备一些环境变量，用boot_patch.sh 去patch init_boot.img，

```bash
./magiskboot cpio ramdisk.cpio \
"add 0750 $INIT magiskinit" \  # magiskinit 作为init
"mkdir 0750 overlay.d" \ # 创建overlay.d目录
"mkdir 0750 overlay.d/sbin" \ # 创建overlay.d/sbin目录
"$SKIP32 add 0644 overlay.d/sbin/magisk32.xz magisk32.xz" \ # magisk32.xz 放到 overlay.d/sbin/magisk32.xz
"$SKIP64 add 0644 overlay.d/sbin/magisk64.xz magisk64.xz" \ # 同上，但64位
"add 0644 overlay.d/sbin/stub.xz stub.xz" \ #同上,但stub.xz
"patch" \ # 执行patch
"$SKIP_BACKUP backup ramdisk.cpio.orig" \ # 放入备份ramdisk.cpio
"mkdir 000 .backup" \ # 创建.backup目录
"add 000 .backup/.magisk config" \ # 放入config到.backup
|| abort "! Unable to patch ramdisk"
```

将patch后的ramdisk 和原始文件对比，前者多了.overlay.d/sbin/magisk*.xz 和.overlay.d/sbin/stub.xz ; 并且init 文件不同；此时init 为magiskinit进程。

```
#解压命令 
cpio -i -d < ramdisk.cpio
```



## magiskinit 代码分析

已经搭建好了magisk debug环境，直接看看日志，magisk做了什么。

```
[    0.433073] magiskinit: Device config:
[    0.433085] magiskinit: skip_initramfs=[0]
[    0.433092] magiskinit: force_normal_boot=[1]
[    0.433098] magiskinit: rootwait=[0]
[    0.433104] magiskinit: slot=[_a]
[    0.433111] magiskinit: dt_dir=[/proc/device-tree/firmware/android]
[    0.433117] magiskinit: fstab_suffix=[]
[    0.433122] magiskinit: hardware=[cheetah]
[    0.433128] magiskinit: hardware.platform=[gs201]
[    0.433132] magiskinit: emulator=[0]
[    0.433140] magiskinit: FirstStageInit
[    0.433145] magiskinit: Setup data tmp
[    0.434591] magiskinit: unxz /.backup/init.xz -> /.backup/init   ?? hah  不知到啥时候还存了个init.xz
[    0.614553] magiskinit: Patch @ 0000F39F [/system/bin/init] -> [/data/magiskinit]
[    0.614831] magiskinit: Unmount [/sys]
[    0.614916] magiskinit: Unmount [/proc] 
[    1.523679] magiskinit: SecondStageInit
[    1.523791] magiskinit: Setup Magisk tmp at /debug_ramdisk
[    1.527170] magiskinit: Setup persist: [sda1] (8, 1)
[    1.530972] magiskinit: preinit: .magisk/mirror/preinit/magisk
[    1.534912] magiskinit: Patching init.rc in /system/etc/init/hw
[    1.535883] magiskinit: Inject magisk rc
[    1.535951] magiskinit: Patching init.zygote64.rc in /system/etc/init/hw
[    1.536340] magiskinit: Inject zygote restart
[    1.536385] magiskinit: Patching init.zygote64_32.rc in /system/etc/init/hw
[    1.536617] magiskinit: Inject zygote restart
[    1.536649] magiskinit: Patching init.zygote32.rc in /system/etc/init/hw
[    1.536867] magiskinit: Inject zygote restart
[    1.552893] magiskinit: Hijack [/sys/fs/selinux/load]
[    1.552912] magiskinit: Hijack [/sys/fs/selinux/enforce]
[    1.553672] magiskinit: Mount [.magisk/rootdir/system/etc/init/hw/init.zygote32.rc] -> [/system/etc/init/hw/init.zygote32.rc]
[    1.553707] magiskinit: Mount [.magisk/rootdir/system/etc/init/hw/init.zygote64_32.rc] -> [/system/etc/init/hw/init.zygote64_32.rc]
[    1.553721] magiskinit: Mount [.magisk/rootdir/system/etc/init/hw/init.zygote64.rc] -> [/system/etc/init/hw/init.zygote64.rc]
[    1.553741] magiskinit: Mount [.magisk/rootdir/system/etc/init/hw/init.rc] -> [/system/etc/init/hw/init.rc]
[    1.554586] magiskinit: Unmount [/data]
[    1.637197] magiskinit: Load policy from: .magisk/selinux/load
```

结合代码分析：

```C++
class FirstStageInit : public BaseInit {
private:
    void prepare();
public:
    FirstStageInit(char *argv[], BootConfig *config) : BaseInit(argv, config) {
        LOGD("%s\n", __FUNCTION__);
    };
    void start() override {
        prepare();
        exec_init();
    }
};
void FirstStageInit::prepare() {
    prepare_data();//复制init到/data/magiskinit
    restore_ramdisk_init(); //还原/init
    auto init = mmap_data("/init", true);
    // Redirect original init to magiskinit
    for (size_t off : init.patch(INIT_PATH, REDIR_PATH)) { /// 修改system/bin/init为 /data/magiskinit
        LOGD("Patch @ %08zX [" INIT_PATH "] -> [" REDIR_PATH "]\n", off);
    }
}
void BaseInit::exec_init() {
    // Unmount in reverse order
    for (auto &p : reversed) {
        if (xumount2(p.data(), MNT_DETACH) == 0)
            LOGD("Unmount [%s]\n", p.data());
    }
    execv("/init", argv);
    exit(1);
}
```

prepare将当前/init 复制到/data/magiskinit ，还原/init为原init ，用注释的话说，重定位/system/bin/init 为/data/magiskinit ，内部实现使用rust，我猜测修改/init程序中 /system/bin/init 字符串为/data/magiskinit。

第二阶段代码执行如下：

```C++
class SecondStageInit : public MagiskInit {
private:
    bool prepare();
public:
    SecondStageInit(char *argv[]) : MagiskInit(argv) {
        LOGD("%s\n", __FUNCTION__);
    };

    void start() override {
        bool is_rootfs = prepare();
        if (is_rootfs)
            patch_rw_root();
        else
            patch_ro_root();
        exec_init();
    }
};

bool SecondStageInit::prepare() {
    umount2("/init", MNT_DETACH);
    unlink("/data/init");

    // Make sure init dmesg logs won't get messed up
    argv[0] = (char *) INIT_PATH;

    // Some weird devices like meizu, uses 2SI but still have legacy rootfs
    struct statfs sfs{};
    statfs("/", &sfs);
    if (sfs.f_type == RAMFS_MAGIC || sfs.f_type == TMPFS_MAGIC) {
        // We are still on rootfs, so make sure we will execute the init of the 2nd stage
        unlink("/init");
        xsymlink(INIT_PATH, "/init");
        return true;
    }
    return false;
}

void MagiskInit::patch_rw_root() {
    mount_list.emplace_back("/data");
    parse_config_file();

    // Create hardlink mirror of /sbin to /root
    mkdir("/root", 0777);
    clone_attr("/sbin", "/root");
    link_path("/sbin", "/root");

    // Handle overlays
    load_overlay_rc("/overlay.d");
    mv_path("/overlay.d", "/");
    rm_rf("/data/overlay.d");
    rm_rf("/.backup");

    // Patch init.rc
    patch_rc_scripts("/", "/sbin", true);

    bool treble;
    {
        auto init = mmap_data("/init");
        treble = init.contains(SPLIT_PLAT_CIL);
    }

    xmkdir(PRE_TMPSRC, 0);
    xmount("tmpfs", PRE_TMPSRC, "tmpfs", 0, "mode=755");
    xmkdir(PRE_TMPDIR, 0);
    setup_tmp(PRE_TMPDIR);
    chdir(PRE_TMPDIR);

    // Extract magisk
    extract_files(true);

    if ((!treble && access("/sepolicy", F_OK) == 0) || !hijack_sepolicy()) {
        patch_sepolicy("/sepolicy", "/sepolicy");
    }

    chdir("/");

    // Dump magiskinit as magisk
    cp_afc(REDIR_PATH, "/sbin/magisk");
}
```

创建/debug_ramdisk 存放文件magisk 相关文件并且patch init.rc  , patch sepolicy  ， 执行/system/bin/init 。



完整的控制流，/magiskinit -> /init 一阶段 -> /data/magiskinit 二阶段 -> /system/bin/init 二阶段。
