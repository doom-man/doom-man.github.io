

# 创建一个继承AccessibilityService的类

```
    import android.accessibilityservice.AccessibilityService;
    import android.view.accessibility.AccessibilityEvent;

    public class MyAccessibilityService extends AccessibilityService {
```

# 清单声明和权限

要被视为无障碍服务，您必须在清单的 `application` 元素中添加一个 `service` 元素（而非 `activity` 元素）。此外，在 `service` 元素中，您还必须添加一个无障碍服务 Intent 过滤器。为了与 Android 4.1 及更高版本兼容，该清单还必须保护该服务，具体做法是添加 `BIND_ACCESSIBILITY_SERVICE` 权限来确保只有系统可以绑定到该服务

```
      <application>
        <service android:name=".MyAccessibilityService"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"
            android:label="@string/accessibility_service_label">
          <intent-filter>
            <action android:name="android.accessibilityservice.AccessibilityService" />
          </intent-filter>
        </service>
      </application>
    
```



# 无障碍服务配置

无障碍服务还必须提供一项配置，此配置可指定该服务能够处理的无障碍事件类型以及有关该服务的其他信息。无障碍服务的配置包含在 `AccessibilityServiceInfo` 类中。您的服务可以在运行时使用此类的实例和 `setServiceInfo()` 来构建和设置配置。不过，使用此方法时，并非所有的配置选项都可用。

从 Android 4.0 开始，您可以在清单中添加一个引用了配置文件的 `<meta-data>` 元素。通过该元素，您能够为无障碍服务设置所有选项，如下例所示：

```
    <service android:name=".MyAccessibilityService">
      ...
      <meta-data
        android:name="android.accessibilityservice"
        android:resource="@xml/accessibility_service_config" />
    </service>
    
```

该元数据元素引用了您在应用的资源目录中创建的 XML 文件 (`<project_dir>/res/xml/accessibility_service_config.xml`)。以下代码展示了该服务配置文件的示例内容：

```xml
    <accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
        android:description="@string/accessibility_service_description"
        android:packageNames="com.example.android.apis"//接受服务事件的包名
        android:accessibilityEventTypes="typeAllMask"
        android:accessibilityFlags="flagDefault" //
        android:accessibilityFeedbackType="feedbackSpoken" //表示语音反馈。
        android:notificationTimeout="100" //两个相同类型的服务送给该服务的最小间隔时间
        android:canRetrieveWindowContent="true" //是否能检索活动的窗口内容
        android:settingsActivity="com.example.android.accessibility.ServiceSettingsActivity"
    />
```