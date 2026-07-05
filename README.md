# 契合（Web版）

房屋租赁合同小助手，包含"合同生成"（对话式）和"合同审查"（上传式）两个功能。
直接对接真实 Dify API，不做 Mock。

## 目录结构

```
qihe-project/
├── web-app/     # 纯 HTML + CSS + JS 前端
└── backend/     # Python + FastAPI 后端
```

## 启动后端

```bash
cd backend
python3 -m venv .venv          # 可选：使用虚拟环境
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

后端启动后访问 http://127.0.0.1:8000 应能看到 `{"status": "ok", ...}`。

## 启动前端

另开一个终端窗口：

```bash
cd web-app
python3 -m http.server 5500
```

然后在浏览器打开 http://127.0.0.1:5500 即可使用。

> 前端默认请求 `http://127.0.0.1:8000` 作为后端地址，如需修改请编辑 `web-app/js/api.js` 中的 `API_BASE`。

## 功能说明

- **合同生成**（`web-app/pages/generate.html`）：文字输入与 AI 对话，AI 自动收集 11 项必要信息后生成完整合同，支持下载 `.docx`。
- **合同审查**（`web-app/pages/review.html`）：上传合同文件（图片/Word/PDF），AI 审查风险条款，给出 RED/YELLOW/GREEN 三级风险等级和逐条修改建议。

## 注意事项

- 本项目不使用数据库、不做用户登录、不做历史记录持久化，所有状态都在内存中。
- 仅支持文字输入，不做语音输入。
- 内容由 AI 生成，仅供参考。
