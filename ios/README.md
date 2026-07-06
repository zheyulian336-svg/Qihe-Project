# 契合 (Qihe) - iOS App

基于 WKWebView 壳封装的 iOS 原生 App，加载本地 HTML/CSS/JS 前端，
通过局域网 HTTP 请求连接 Mac 上的 Python 后端。

## 目录结构

```
ios/
├── QiheApp/
│   ├── QiheApp.swift              # @main App 入口
│   ├── ContentView.swift          # 根视图（全屏 WebView）
│   ├── WebViewWrapper.swift       # WKWebView 壳 + JS 桥接
│   ├── Info.plist                 # App 配置（ATS 允许 HTTP 等）
│   ├── Assets.xcassets/           # App 图标 + 强调色
│   └── www/                       # → 软链接到 ../web-app/
├── QiheApp.xcodeproj/             # Xcode 项目（由脚本生成）
│   └── project.pbxproj
├── generate_xcode_project.py      # 项目生成脚本
└── README.md                      # 本文件
```

---

## 第一步：准备工作

### 1. 安装 Xcode
从 Mac App Store 免费下载（约 12 GB，建议提前装好）。

### 2. 获取 Mac 局域网 IP
在 Mac 终端运行：

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

你会看到类似 `inet 192.168.1.100` 或 `inet 192.168.31.42` 的输出，
记下这个 IP 地址。

### 3. 修改 App 中的后端地址
打开 `ios/QiheApp/WebViewWrapper.swift`，修改第 7-8 行：

```swift
private let backendHost = "192.168.1.100"   // 改成你 Mac 的 IP
private let backendPort = "8000"
```

### 4. 启动后端（监听局域网）
```bash
cd backend
source .venv/bin/activate         # 如果有虚拟环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. iPhone 开启开发者模式
- iPhone 上：`设置 → 隐私与安全性 → 开发者模式` → 打开 → **重启手机**
- 如果没看到这个选项，先用数据线连一次 Mac，它会自动出现

---

## 第二步：在 Xcode 中登录 Apple ID

1. 打开 Xcode
2. 菜单栏 → `Xcode` → `Settings...`（或 `⌘,`）
3. 点击 `Accounts` 标签页
4. 左下角 `+` → `Apple ID` → 输入你的 Apple ID 和密码
5. 登录成功后，右侧会显示 `Personal Team`

---

## 第三步：打开项目并配置签名

1. 在终端运行（或 Finder 中双击 `QiheApp.xcodeproj`）：

```bash
open ios/QiheApp.xcodeproj
```

2. Xcode 打开后，左侧文件列表中点击最顶部的蓝色 **QiheApp** 项目图标
3. 中间区域选择 **Signing & Capabilities** 标签
4. 勾选 ✅ `Automatically manage signing`
5. **Team** 下拉菜单 → 选择你的 `Personal Team`
6. **Bundle Identifier** 改成唯一的，建议：`com.你的名字.qihe`
   （例如 `com.zhangsan.qihe`）

> 如果一切正常，这里不会报红色错误。如果出现红色错误提示，
> 检查 Apple ID 是否已登录，或 Bundle Identifier 是否已被占用（换一个即可）。

---

## 第四步：连接手机、运行 App

1. 用 **USB 数据线** 将 iPhone 连接到 Mac
2. iPhone 弹出「**信任此电脑？**」→ 点 **信任**，输入手机解锁密码
3. 在 Xcode 顶部工具栏，点击设备选择下拉菜单（显示 iPhone 名字或模拟器名）
4. 选择你的 **iPhone**（例如"张三的 iPhone"）
5. 点击 ▶️ 运行按钮（或按 `⌘ + R`）
6. Xcode 开始编译 → 编译完成后自动安装到 iPhone
7. **第一次运行会失败** —— iPhone 上弹出「不受信任的开发者」，这是正常的
8. 去 iPhone：`设置 → 通用 → VPN 与设备管理` → 找到你的 Apple ID → 点击 **信任**
9. 回到桌面，点击「契合」图标 → App 启动！

> 之后每次运行（`⌘ + R`）不再需要重新信任。

---

## 第五步：确保网络通畅

- iPhone 和 Mac 必须连接 **同一个 Wi-Fi**（或同一局域网）
- Mac 的防火墙可能阻止外部访问端口 8000，如果 iPhone 连不上后端：
  - `系统设置 → 网络 → 防火墙` → 关闭或添加例外
- 可以用 iPhone 的 Safari 先访问 `http://<Mac的IP>:8000` 测试，
  如果能看到 `{"status":"ok",...}` 说明网络通

---

## 关于 7 天重签（免费 Apple ID）

| 账号类型 | App 有效期 | 续签方式 |
|---------|-----------|---------|
| 免费 Apple ID | **7 天** | 连 Mac → 打开 Xcode → `⌘ + R` 重新安装 |
| Apple Developer ($99/年) | 1 年 | 同上，但一年一次 |

> 7 天后 App 图标变灰无法打开，数据（对话记录）会丢失。
> 重装后即可继续使用。

---

## 常见问题

**Q: Xcode 说 "Failed to code sign" 或 "No provisioning profile"**
A: 检查 Signing & Capabilities 里的 Team 是否选中了你的 Personal Team。

**Q: App 白屏或无法加载页面**
A: 检查 `www/` 软链接是否正常：`ls -la ios/QiheApp/www` 应指向 `../../web-app`。

**Q: iPhone 上能打开但无法连接后端**
A: 1) 确认后端已用 `--host 0.0.0.0` 启动；2) 确认 iPhone 和 Mac 在同一 Wi-Fi；
3) 确认 `WebViewWrapper.swift` 中的 IP 地址正确。

**Q: 文件上传点了没反应**
A: iOS 14+ 的 WKWebView 原生支持 `<input type="file">`，会自动弹出系统文件选择器。
如果没有弹出，检查 iPhone 是否授予了 App 访问文件的权限。

**Q: 想改回纯 Web 开发模式**
A: 不影响。`web-app/` 目录完全没有被修改（只是 api.js 加了一行兼容代码），
照常用 `python3 -m http.server 5500` 启动前端即可。
