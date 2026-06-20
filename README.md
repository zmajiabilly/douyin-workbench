# 抖音工作台

粘贴抖音链接 → 自动下载视频、转写文案、AI 总结、封面分析。全部走云端大模型，本地零负担。

## 在 Windows 上部署

### 第 1 步：装 Python

1. 打开浏览器，访问 https://www.python.org/downloads/
2. 点击黄色的 **Download Python 3.12.x** 按钮下载安装包
3. 运行下载的安装程序
4. **重要：** 安装时勾选底部的 **"Add Python to PATH"**（把 Python 加到系统路径）
5. 点 "Install Now" 完成安装

验证是否安装成功：按 `Win + R`，输入 `cmd` 回车，在黑色窗口里输入：

```cmd
python --version
```

能看到 Python 版本号就说明装好了。

### 第 2 步：装 ffmpeg（处理视频/音频）

1. 打开浏览器，访问 https://www.gyan.dev/ffmpeg/builds/
2. 找到 **ffmpeg-release-full.7z** 并下载
3. 解压到 `C:\ffmpeg`（解压后里面应该有一个 `bin` 文件夹）
4. 把 `C:\ffmpeg\bin` 加到系统 PATH：
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 在"系统变量"里找到 `Path` → 双击 → 新建 → 粘贴 `C:\ffmpeg\bin`
   - 点确定保存

验证：重新打开 cmd，输入 `ffmpeg -version`，能看到版本信息就说明装好了。

### 第 3 步：下载本项目

- **有 Git：** 打开 cmd，输入：

```cmd
git clone https://github.com/zmajiabilly/douyin-workbench.git
cd douyin-workbench
```

- **没有 Git：** 去 https://github.com/zmajiabilly/douyin-workbench 点绿色的 "Code" → "Download ZIP" → 解压，然后在 cmd 里 `cd` 到解压后的文件夹。

### 第 4 步：装依赖

在 cmd 里（确保当前在项目目录下）输入：

```cmd
pip install -r requirements.txt
```

等它跑完，没有红字报错就行。

### 第 5 步：配置 API Key

1. 复制配置文件模板：
```cmd
copy config.example.yaml config.yaml
```

2. 用记事本打开 `config.yaml`，找到 `siliconflow_api_key: ""` 填入你的真实 Key。

**或者：** 启动后打开网页右上角「⚙ 配置」，在页面上填写 API Key。

**免费获取 API Key：** 打开 https://cloud.siliconflow.cn → 注册账号 → 进入控制台 → 创建 API Key（新用户有免费额度，够用很久）

### 第 6 步：启动

在 cmd 里输入：

```cmd
python app.py
```

浏览器会自动打开 http://127.0.0.1:8650，看到页面就成功了！

---

## 在 Mac 上部署

### 第 1 步：装 ffmpeg

打开"终端"（Terminal），先装 Homebrew（如果没装的话）：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

然后用 Homebrew 装 ffmpeg：

```bash
brew install ffmpeg
```

### 第 2 步：下载本项目

```bash
git clone https://github.com/zmajiabilly/douyin-workbench.git
cd douyin-workbench
```

（或直接下载 ZIP 解压，然后在终端里 `cd` 到项目目录）

### 第 3 步：装依赖

```bash
pip3 install -r requirements.txt
```

### 第 4 步：配置 API Key

```bash
cp config.example.yaml config.yaml
open config.yaml
```

找到 `siliconflow_api_key: ""`，填入你的真实 Key。或者启动后打开网页配置页填写。

**免费获取 API Key：** 打开 https://cloud.siliconflow.cn → 注册 → 创建 API Key

### 第 5 步：启动

```bash
python3 app.py
```

浏览器自动打开 http://127.0.0.1:8650

---

## 使用说明

1. 粘贴抖音分享链接（如 `https://v.douyin.com/xxxxx/`）
2. 点「开始处理」
3. 等待处理完成（通常 1-3 分钟）
4. 四个 Tab 查看结果：**视频播放 / 完整文案 / AI 总结 / 封面分析**
5. 历史记录在下方列表，点击可回顾

## 文件结构

```
douyin-workbench/
├── app.py                  # 启动入口
├── db.py                   # 数据管理（SQLite）
├── config.yaml             # 配置文件（填 API Key）
├── requirements.txt        # Python 依赖
├── douyin_pipeline/        # 核心管线包（可独立调用）
│   ├── __init__.py
│   ├── parser.py           # 抖音页面解析
│   ├── downloader.py       # 视频/音频/封面下载
│   ├── asr.py              # 语音转写（SiliconFlow SenseVoice）
│   └── llm.py              # AI 总结 + 封面视觉分析
├── templates/
│   ├── index.html          # 主界面
│   └── config.html         # 配置页
└── data/
    └── downloads/          # 下载的素材
```

## 说明

- 所有数据存本地，不上传任何服务器
- 视频、音频、截图保存在 `data/downloads/` 下
- 支持 SiliconFlow 和 OpenAI 两种大模型
- 默认用 SiliconFlow（免费额度多），可在网页右上角「配置」中切换
