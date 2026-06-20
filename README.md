# 📱 抖音工作台

**一个本地运行的抖音内容分析工具。** 粘贴链接 → 自动下载视频、转写文案、AI 总结、封面分析。全部走云端大模型，本地零负担。

## 🚀 快速开始

### 1. 安装 Python

确保电脑上有 **Python 3.9+**：

```bash
python3 --version
```

没有的话去 [python.org](https://www.python.org/downloads/) 下载安装。

### 2. 安装 ffmpeg（处理视频/音频）

**macOS：**
```bash
brew install ffmpeg
```

**Windows：**
1. 去 https://ffmpeg.org/download.html 下载
2. 解压后把 `bin/` 目录加到系统环境变量 `PATH` 中
3. 打开 cmd 输入 `ffmpeg -version` 确认安装成功

### 3. 下载项目

```bash
git clone https://github.com/zmajiabilly/douyin-workbench.git
cd douyin-workbench
```

（或直接下载 ZIP 解压）

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置 API Key

编辑 `config.yaml`，填上你的 SiliconFlow API Key：

```yaml
llm:
  siliconflow_api_key: "sk-你的key"    # AI 总结 + 封面分析
asr:
  siliconflow_api_key: "sk-你的key"    # 语音转写（同一个 Key）
```

**免费获取 API Key：** https://cloud.siliconflow.cn → 注册 → 创建 API Key（新用户有免费额度）

### 6. 启动

```bash
python app.py
```

浏览器自动打开 `http://127.0.0.1:8650`

## 🎯 使用

1. 粘贴抖音分享链接（如 `https://v.douyin.com/xxxxx/`）
2. 点击「开始处理」
3. 等待处理完成（通常 1-3 分钟）
4. 四个 Tab 查看结果：**视频播放 / 完整文案 / AI 总结 / 封面分析**
5. 历史记录在下方列表，点击可回顾

## ⚙️ 配置

打开 `config.yaml` 或点网页右上角「配置」：

| 配置项 | 说明 |
|--------|------|
| `llm.provider` | 大模型：siliconflow / openai |
| `llm.siliconflow_api_key` | SiliconFlow API Key |
| `asr.siliconflow_api_key` | ASR 语音识别的 API Key |

## 🗂 文件结构

```
douyin-workbench/
├── app.py              # 启动入口
├── config.yaml         # 配置文件（填 API Key）
├── requirements.txt    # Python 依赖
├── pipeline/
│   ├── db.py           # 数据管理
│   ├── douyin.py       # 视频解析+下载
│   ├── asr.py          # 语音转写
│   └── llm.py          # AI 总结 + 封面视觉分析
├── templates/
│   ├── index.html      # 主界面
│   └── config.html     # 配置页
└── data/
    └── downloads/      # 下载的素材
```

## 📝 说明

- 所有数据存本地，不上传任何服务器
- 视频、音频、截图都保存在 `data/downloads/` 下
- 桌面版功能：单条链接处理、下载、转写、AI 总结、封面视觉分析
- 完整版（批量监控、竞品对比、行业模板）→ 课程内提供