import SwiftUI
import WebKit

// MARK: - 后端地址配置（改成你 Mac 的局域网 IP）
// 在 Mac 终端输入 ifconfig | grep "inet " 查看你的局域网 IP 地址
// 例如：192.168.1.100、192.168.31.42 等
private let backendHost = "192.168.31.155"
private let backendPort = "8000"
private let backendURL  = "http://\(backendHost):\(backendPort)"

// MARK: - WKWebView 壳
struct WebViewWrapper: UIViewRepresentable {

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        // ---- 配置 ----
        let config = WKWebViewConfiguration()
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")

        // 注入后端地址，在页面加载前设置 window.__QIHE_API_BASE__
        let injectJS = """
        window.__QIHE_API_BASE__ = '\(backendURL)';
        """
        let userScript = WKUserScript(
            source: injectJS,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: true
        )
        config.userContentController.addUserScript(userScript)

        // 注册 saveFile 消息处理器（前端下载文件用）
        config.userContentController.add(context.coordinator, name: "saveFile")

        // ---- 创建 WebView ----
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.allowsBackForwardNavigationGestures = true
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.92, green: 0.94, blue: 0.98, alpha: 1.0)

        // ---- 加载本地 HTML ----
        if let wwwURL = Bundle.main.url(
            forResource: "www/index",
            withExtension: "html",
            subdirectory: nil
        ) {
            let readAccessURL = wwwURL.deletingLastPathComponent()
            webView.loadFileURL(wwwURL, allowingReadAccessTo: readAccessURL)
        }

        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    // MARK: - Coordinator（导航代理 + 消息处理）
    class Coordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {

        // ---- WKScriptMessageHandler：处理前端发来的 saveFile 消息 ----
        func userContentController(
            _ userContentController: WKUserContentController,
            didReceive message: WKScriptMessage
        ) {
            guard message.name == "saveFile",
                  let body = message.body as? [String: Any],
                  let filename = body["filename"] as? String,
                  let base64 = body["base64"] as? String,
                  let fileData = Data(base64Encoded: base64) else {
                print("[Qihe] saveFile 消息格式错误")
                return
            }

            // 保存到临时目录
            let tempDir = FileManager.default.temporaryDirectory
            let fileURL = tempDir.appendingPathComponent(filename)
            do {
                try fileData.write(to: fileURL)
                print("[Qihe] 文件已保存: \(fileURL.path)")
            } catch {
                print("[Qihe] 文件保存失败: \(error.localizedDescription)")
                return
            }

            // 在主线程弹出系统分享面板
            DispatchQueue.main.async {
                self.presentShareSheet(fileURL: fileURL)
            }
        }

        private func presentShareSheet(fileURL: URL) {
            guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                  let rootVC = windowScene.windows.first?.rootViewController else {
                print("[Qihe] 无法获取 root view controller")
                return
            }

            let activityVC = UIActivityViewController(
                activityItems: [fileURL],
                applicationActivities: nil
            )

            // iPad 需要设置 popover 锚点
            if let popover = activityVC.popoverPresentationController {
                popover.sourceView = rootVC.view
                popover.sourceRect = CGRect(
                    x: rootVC.view.bounds.midX,
                    y: rootVC.view.bounds.midY,
                    width: 0,
                    height: 0
                )
                popover.permittedArrowDirections = []
            }

            rootVC.present(activityVC, animated: true)
        }

        // ---- WKNavigationDelegate ----
        func webView(
            _ webView: WKWebView,
            didFail navigation: WKNavigation!,
            withError error: Error
        ) {
            print("[Qihe] 页面导航失败: \(error.localizedDescription)")
        }

        func webView(
            _ webView: WKWebView,
            didFailProvisionalNavigation navigation: WKNavigation!,
            withError error: Error
        ) {
            print("[Qihe] 页面加载失败: \(error.localizedDescription)")
        }

        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationAction: WKNavigationAction,
            decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
        ) -> Void {
            // 允许所有导航（包括文件上传等）
            decisionHandler(.allow)
        }
    }
}
