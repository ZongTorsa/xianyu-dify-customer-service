# 闲鱼智能客服

基于 Playwright 监听闲鱼未读消息，将客户问题发送给 Dify 工作流生成回复，并自动回填到闲鱼聊天窗口。

## 技术栈

- **Python 3.11+**：应用逻辑、配置加载与本地任务运行。
- **Playwright for Python**：启动 Chrome、读取未读聊天内容、发送自动回复。
- **FastAPI + Uvicorn**：提供本地 `/chat` 服务，隔离 Dify API 调用。
- **Dify Workflow API**：根据客户消息，rag检索知识库，生成客服回复。
- **Requests + python-dotenv**：HTTP 通信和本地环境变量管理。

## 项目结构

```text
.
├── xianyu_customer_service/
│   ├── api.py          # FastAPI 本地接口
│   ├── bot.py          # 闲鱼页面监听与自动回复
│   ├── dify.py         # Dify 请求与回复解析
│   └── settings.py     # 环境变量与路径配置
├── run_api.py          # 启动本地 Dify API
├── run_bot.py          # 启动闲鱼客服机器人
├── .env.example        # 配置模板
├── requirements.txt
└── tests/              # 不依赖浏览器的单元测试
```

`test_playwright.py`、`dify_client.py` 和 `dify_fastapi/main.py` 保留为兼容入口，已有启动习惯不会失效。

## 环境准备

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

复制配置模板并填写 Dify 信息：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`：

```dotenv
DIFY_URL=https://your-dify-host/v1/workflows/run
DIFY_API_KEY=app-xxxxxxxx
```

如需安装 Playwright 浏览器组件，可执行：

```powershell
playwright install
```

本工具优先使用已安装的 Google Chrome。

## 运行

先在第一个终端启动本地 Dify API：

```powershell
python run_api.py
```

再在第二个终端启动闲鱼监听：

```powershell
python run_bot.py
```

首次运行会打开独立的 Chrome 资料目录 `playwright-profile/`。请自行完成闲鱼登录；该目录保存 Cookie 与会话，不得上传或分享。

## 测试

```powershell
python -m unittest discover -s tests
```

## GitHub 安全说明

`.gitignore` 已忽略 `.env`、浏览器资料目录、Python 缓存、虚拟环境及 IDE 文件。发布前请确认仓库中仅包含 `.env.example`，绝不包含真实 API Key、Cookie 或聊天记录。
