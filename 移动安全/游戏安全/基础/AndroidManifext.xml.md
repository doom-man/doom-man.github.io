## AndroidManifext.xml
AndroidManifest官方解释是应用清单.

<manifest>元素
首先，所有的xml都必须包含<manifest>元素。这是文件的根节点。它必须要包含<application>元素，并且指明xmlns:android和package属性。

<manifest>元素中的属性
xmlns:android
这个属性定义了Android命名空间。必须设置成"http://schemas.android.com/apk/res/android"。不要手动修改。

package
这是一个完整的Java语言风格包名。包名由英文字母（大小写均可）、数字和下划线组成。每个独立的名字必须以字母开头。

构建APK的时候，构建系统使用这个属性来做两件事：

1、生成R.java类时用这个名字作为命名空间（用于访问APP的资源）
比如：package被设置成com.sample.teapot，那么生成的R类就是：com.sample.teapot.R
2、用来生成在manifest文件中定义的类的完整类名。比如package被设置成com.sample.teapot，并且activity元素被声明成<activity android:name=".MainActivity">，完整的类名就是com.sample.teapot.MainActivity。
包名也代表着唯一的application ID，用来发布应用。但是，要注意的一点是：在APK构建过程的最后一步，package名会被build.gradle文件中的applicationId属性取代。如果这两个属性值一样，那么万事大吉，如果不一样，那就要小心了。

android:versionCode
内部的版本号。用来表明哪个版本更新。这个数字不会显示给用户。显示给用户的是versionName。这个数字必须是整数。不能用16进制，也就是说不接受"0x1"这种参数

android:versionName
显示给用户看的版本号。

<manifest>元素中的元素
<uses-feature>元素
Google Play利用这个元素的值从不符合应用需要的设备上将应用过滤。

这东西的作用是将APP所依赖的硬件或者软件条件告诉别人。它说明了APP的哪些功能可以随设备的变化而变化。

使用的时候要注意，必须在单独的<uses-feature>元素中指定每个功能，如果要多个功能，需要多个<uses-feture>元素。比如要求设备同时具有蓝牙和相机功能：
```
<uses-feature android:name="android.hardware.bluetooth" />
<uses-feature android:name="android.hardware.camera" />
```


<uses-feature>的属性
android:name
该属性以字符串形式指定了APP要用的硬件或软件功能。

android:required
这项属性如果值为true表示需要这项功能否则应用无法工作，如果为false表示应用在必要时会使用该功能，但是如果没有此功能应用也能工作。

android:glEsVersion
指明应用需要的Opengl ES版本。高16位表示主版本号，低16位表示次版本号。例如，如果是要3.2的版本，就是0x00030002。如果定义多个glEsVersion，应用会自动启用最高的设置。

<application>元素
此元素描述了应用的配置。这是一个必备的元素，它包含了很多子元素来描述应用的组件，它的属性影响到所有的子组件。许多属性（例如icon、label、permission、process、taskAffinity和allowTaskReparenting）都可以设置成默认值。

<application>的属性
android:allowBackup
表示是否允许APP加入到备份还原的结构中。如果设置成false，那么应用就不会备份还原。默认值为true。

android:fullBackupContent
这个属性指向了一个xml文件，该文件中包含了在进行自动备份时的完全备份规则。这些规则定义了哪些文件需要备份。此属性是一个可选属性。默认情况下，自动备份包含了大部分app文件。

android:supportsRtl
声明你的APP是否支持RTL（Right To Left）布局。如果设置成true，并且targetSdkVersion被设置成17或更高。很多RTL API会被集火，这样你的应用就可以显示RTL布局了。如果设置成false或者targetSdkVersion被设置成16或更低。哪些RTL API就不起作用了。

该属性的默认的值是false。

android:icon
APP的图标，以及每个组件的默认图标。可以在组价中自定义图标。这个属性必须设置成一个引用，指向一个可绘制的资源，这个资源必须包含图片。系统不设置默认图标。例如mipmap/ic_launcher引用的就是下面的资源




实例分析
```
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          package="com.sample.teapot"
          android:versionCode="1"
          android:versionName="1.0.0.1" >


  <uses-feature android:glEsVersion="0x00020000"></uses-feature>

  <application
      android:allowBackup="false"
      android:fullBackupContent="false"
      android:supportsRtl="true"
      android:icon="@mipmap/ic_launcher"
      android:label="@string/app_name"
      android:theme="@style/AppTheme"
      android:name="com.sample.teapot.TeapotApplication"
      >

    <!-- Our activity is the built-in NativeActivity framework class.
         This will take care of integrating with our NDK code. -->
    <activity android:name="com.sample.teapot.TeapotNativeActivity"
              android:label="@string/app_name"
              android:configChanges="orientation|keyboardHidden">
      <!-- Tell NativeActivity the name of our .so -->
      <meta-data android:name="android.app.lib_name"
                 android:value="TeapotNativeActivity" />
      <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
      </intent-filter>
    </activity>
  </application>
</manifest>
```

> reference
> https://www.jianshu.com/p/3b5b89d4e154