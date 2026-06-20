# 📱 抖音工作台

**一个本地运行的抖音内容分析工具。** 粘贴链接 → 自动下载视频、转写文案、AI 总结、封面分析。

## 🚀 快速开始

### 1. 安装 Python

确保电脑上有 **Python 3.9+**：

```bash
python3 --version
```

没有的话去 [python.org](https://www.python.org/downloads/) 下载安装。

### 2. 安装 ffmpeg（视频/音频处理）

**macOS：**
```bash
brew install ffmpeg
```

**Windows：**
1. 去 https://ffmpeg.org/download.html 下载
2. 解压后把 `bin/` 目录加到系统环境变量 `PATH` 中
3. 打开 cmd 输入 `ffmpeg -version` 确认安装成功

### 3. 下载本项目

```bash
git clone https://github.com/你的用户名/douyin-workbench.git
cd douyin-workbench
```

（或者直接下载 ZIP 解压）

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置大模型（二选一）

#### 方式 A：Ollama（本地运行，免费，推荐）

1. 安装 [Ollama](https://ollama.com/)
2. 拉取模型：
```bash
ollama pull qwen2.5:7b        # 文本分析
ollama pull qwen2.5-vl:7b     # 封面分析（可选，需要 ~5G）
```
3. 打开浏览器访问 `http://localhost:11434` 确认 Ollama 在运行
4. 本项目的配置默认就是 Ollama，无需修改

#### 方式 B：SiliconFlow（云端 API）

1. 去 [SiliconFlow](https://cloud.siliconflow.cn) 注册，获取 API Key
2. 打开浏览器访问本项目 → 点右上角「配置」→ 选择 SiliconFlow → 填 API Key

### 6. 启动

```bash
python app.py
```

浏览器自动打开 `http://127.0.0.1:8650`

## 🎯 使用

1. 粘贴抖音分享链接（如 `https://v.douyin.com/xxxxx/`）
2. 点击「开始处理」
3. 等待处理完成（通常 1-3 分钟）
4. 查看：视频播放 / 完整文案 / AI 总结 / 封面分析
5. 历史记录在下方列表，点击可回顾

## ⚙️ 配置说明

打开 `config.yaml` 或点网页右上角「配置」：

| 配置项 | 说明 |
|--------|------|
| `llm.provider` | 大模型：ollama / siliconflow / openai |
| `llm.text_model` | 文本模型名 |
| `llm.vision_model` | 视觉模型名（封面分析） |
| `asr.provider` | 语音识别：siliconflow / local_whisper |
| `asr.siliconflow_api_key` | ASR 的 API Key |

**推荐配置（免费）：**
- LLM: Ollama + qwen2.5:7b（本地运行，0 费用）
- ASR: SiliconFlow（有免费额度）

## 🗂 文件结构

```
douyin-workbench/
├── app.py              # 启动入口
├── config.yaml         # 配置文件
├── requirements.txt    # Python 依赖
├── pipeline/
│   ├── db.py           # 数据管理
│   ├── douyin.py       # 视频解析+下载
│   ├── asr.py          # 语音转写
│   └── llm.py          # AI 总结
├── templates/
│   ├── index.html      # 主界面
│   └── config.html     # 配置页
└── data/
    └── downloads/      # 下载素材
        ├── videos/
        ├── audio/
        └── screenshots/
```

## 📝 说明

- 所有数据存本地，不上传任何服务器
- 视频、音频、截图都保存在 `data/downloads/` 下
- 免费版可做的功能都在这里面
- 完整版（不限账号+批量监控+行业模板）→ 课程内提供