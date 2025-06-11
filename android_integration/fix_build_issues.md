# Android 构建问题修复指南

## 🔧 已修复的问题

### 1. AAPT2 版本问题
- **问题**: 使用了 alpha 版本的 Android Gradle Plugin (7.1.0-alpha11)
- **修复**: 升级到稳定版本 8.1.4

### 2. Gradle 版本兼容性
- **问题**: Gradle 版本过旧 (7.2)
- **修复**: 升级到 Gradle 8.0

### 3. 资源链接问题
- **问题**: 布局文件中的自定义样式引用导致 AAPT2 崩溃
- **修复**: 移除自定义样式引用，使用内联样式

## 🚀 构建步骤

### 1. 清理项目
```bash
cd android_integration
./gradlew clean
```

### 2. 重新构建
```bash
./gradlew build
```

### 3. 如果仍有问题，尝试以下步骤：

#### 步骤 A: 清理 Gradle 缓存
```bash
./gradlew clean
rm -rf .gradle
rm -rf app/build
```

#### 步骤 B: 重新下载依赖
```bash
./gradlew --refresh-dependencies
```

#### 步骤 C: 使用基础布局
如果改进版布局仍有问题，在 `AndroidManifest.xml` 中切换到基础版：
```xml
<activity android:name=".MainActivity" ... />
```

## 🔍 常见问题解决

### 问题 1: "AAPT2 process unexpectedly exit"
**解决方案**:
1. 检查资源文件是否有语法错误
2. 确保所有引用的资源都存在
3. 使用 `./gradlew clean` 清理项目

### 问题 2: "Gradle sync failed"
**解决方案**:
1. 检查网络连接
2. 更新 Android Studio
3. 删除 `.gradle` 文件夹重新同步

### 问题 3: "Resource linking failed"
**解决方案**:
1. 检查 `colors.xml` 中的颜色定义
2. 确保所有字符串资源都存在
3. 验证图标文件格式正确

## 📱 推荐的构建配置

### 使用基础版本（最稳定）
1. 主活动: `MainActivity`
2. 布局: `activity_main.xml`
3. 无自定义样式依赖

### 使用改进版本（功能丰富）
1. 主活动: `MainActivityImproved`
2. 布局: `activity_main_improved.xml`
3. Material Design 组件

## 🛠️ 调试技巧

### 1. 查看详细错误信息
```bash
./gradlew build --info
```

### 2. 检查资源编译
```bash
./gradlew :app:processDebugResources --info
```

### 3. 验证 APK 内容
```bash
./gradlew assembleDebug
unzip -l app/build/outputs/apk/debug/app-debug.apk
```

## 📞 如果问题仍然存在

1. **检查 Android Studio 版本**: 建议使用最新稳定版
2. **检查 JDK 版本**: 确保使用 JDK 8 或更高版本
3. **检查系统资源**: 确保有足够的内存和磁盘空间
4. **重启 Android Studio**: 有时简单重启可以解决问题

## ✅ 验证修复

构建成功后，您应该看到：
```
BUILD SUCCESSFUL in Xs
```

然后可以：
1. 在 Android Studio 中运行应用
2. 或使用命令行安装: `./gradlew installDebug`
