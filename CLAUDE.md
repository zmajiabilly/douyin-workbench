# 抖音工作台 — 项目说明

## 项目定位
用户本地运行的 Web 工具（Windows优先）。粘贴抖音链接 → 自动下载视频/文案/音频/封面 → AI结构化总结 + 封面视觉分析。
**纯本地，不上传任何数据。**

## 技术栈
- 后端：Python Flask + SQLite
- 前端：原生 HTML/CSS/JS（零构建工具）
- 依赖：flask, requests, pyyaml, openpyxl

## 文件结构
```
douyin-workbench/
├── app.py                  # Flask 入口
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖清单
├── README.md               # 部署说明（Windows优先）
│
├── douyin_pipeline/        # 核心处理模块
│   ├── __init__.py
│   ├── parser.py           # 抖音页面解析（直接爬 iesdouyin.com）
│   ├── downloader.py       # 视频/音频/封面下载
│   ├── asr.py              # 语音转写（SiliconFlow）
│   └── llm.py              # AI总结+封面视觉分析
│
├── templates/
│   ├── index.html          # 主界面（两个Tab）
│   └── config.html         # 配置页
│
└── data/downloads/
    ├── videos/
    ├── audio/
    └── screenshots/
```

---

## 页面设计

### 顶部栏
左边「📱 抖音工作台」标题，右边「⚙ 配置」按钮。

### 主页面：两个 Tab 切换

**Tab 1「处理新链接」：**
```
┌─────────────────────────────────────────────┬──────────┐
│  粘贴抖音链接 https://v.douyin.com/xxx      │ 开始处理  │
└─────────────────────────────────────────────┴──────────┘
☑ 转写文案  ☑ AI 总结

[加载中：◌ 解析链接中… / 下载视频中… / 转写文案中…]

┌── 结果卡片 ────────────────────────────────┐
│  标题文字                                    │
│  👤 作者名 · ❤ 1234                        │
│                                             │
│  [视频] [完整文案] [AI总结] [封面分析]       │
│  ┌─────────────────────────────────────┐   │
│  │  视频播放器 / 全文 / 总结 / 分析     │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Tab 2「📋 下载记录」（表格）：**

列头：
```
标题 | 原始链接 | 作者 | 点赞量 | 创建时间 | 下载时间 | 标签 | 内容总结 | AI总结 | 操作
```

- 标题可点击 → 弹窗查看完整详情
- 原始链接可点击 → 跳转抖音
- 内容总结：ASR 前 100 字 +「全文」按钮弹窗
- AI总结：前 100 字 +「全文」按钮弹窗
- 操作列：[▶ 播放视频] [删除]
- 搜索框按标题/作者筛选
- 底部「📥 导出 Excel」按钮，导出完整字段
- 表格可排序（按创建时间/下载时间）

---

### 配置页

**区块 1：🤖 API Key（二选一，radio 互斥）**

```
○ 使用自己的 API Key
   提供商 [SiliconFlow ▼]
   API Key [••••••••••••••••••••••••]

● 扫码购买（用我们的 Key）
   ┌──────────┐
   │ 二维码图  │   微信/支付宝收款码
   └──────────┘
   扫描支付后，将收到的激活码粘贴到下方：
   [激活码输入框]  [验证]
   状态：✅ 已激活 · 剩余 100 次
```

**区块 2：📂 下载保存位置**
```
保存路径：[ C:\Users\xxx\Videos\抖音素材  ]  [浏览...]
默认：data/downloads/
子目录：videos/  audio/  screenshots/
```

底部 [💾 保存配置]

---

## 抖音页面解析 — 直接爬取 iesdouyin.com

`douyin_pipeline/parser.py` 直接请求抖音解析页面获取数据，无需额外依赖：

### 示例

```python
from douyin_pipeline import parser
info = parser.parse_url("https://v.douyin.com/xxx/")
# 返回: { video_id, title, author, like_count, video_url, cover_url, duration }
```

### 文案提取（SiliconFlow API）

```python
from douyin_pipeline import asr
text = asr.transcribe("audio.mp3", {"llm": {"siliconflow_api_key": "sk-xxx"}})
```

### 安装方式
```bash
pip install -r requirements.txt
```

该工具自己解析 iesdouyin.com 页面获取无水印视频地址，无需第三方付费 API 即可获取视频地址。AI 文案总结和 ASR 走 SiliconFlow（需要 API Key）。

---

## API 路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 主页面 |
| GET | /config | 配置页 |
| GET | /api/config | 读配置 |
| POST | /api/config | 存配置 |
| POST | /api/process | 处理链接（异步） |
| GET | /api/history | 记录列表 |
| GET | /api/item/{id} | 单条详情 |
| DELETE | /api/item/{id} | 删除+清文件 |
| GET | /api/export | 导出 Excel |
| GET | /download/{path} | 本地素材文件 |

---

## 核心流程

```
parser.parse_url(链接)         ← 直接爬 iesdouyin.com
    ↓
downloader.download_video()
downloader.download_cover()
downloader.extract_audio()
    ↓
asr.transcribe(音频)          ← 调用 SiliconFlow SenseVoice
    ↓
llm.summarize(文案)           ← 调用 SiliconFlow / OpenAI
llm.analyze_cover(封面)       ← 调用视觉模型
    ↓
SQLite 存库 → 刷新页面
```

---

## 数据库字段（对标飞书每日叙述表，去掉 ob 链接）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| video_id | TEXT UNIQUE | 抖音视频ID |
| url | TEXT | 原始链接 |
| title | TEXT | 标题 |
| author | TEXT | 作者 |
| like_count | INTEGER | 点赞量 |
| create_time | INTEGER | 视频创建时间 |
| video_path | TEXT | 本地视频路径 |
| audio_path | TEXT | 本地音频路径 |
| screenshot_path | TEXT | 本地封面路径 |
| transcript | TEXT | ASR全文（=飞书"视频内容"） |
| summary | TEXT | AI总结（=飞书"内容AI总结"） |
| tags | TEXT | 标签逗号分隔（=飞书"内容标签"） |
| status | TEXT | parsed/downloaded/transcribed/done |
| downloaded_at | INTEGER | 下载时间（=飞书"提取时间"） |

---

## 导出 Excel

`/api/export` → .xlsx，包含所有字段，transcript 和 summary 导出完整内容。

---

## 设计风格
- 深色：背景 #0f0f13，卡片 #1a1a23，边框 #2a2a35
- 强调：橙色 #ea580c
- 圆角 6-10px

## 约束
- pathlib 跨平台
- ffmpeg 找不到给提示
- 无前端框架，原生 JS fetch
- 异步处理不卡页面
- openpyxl 导出 Excel
- **页面解析直接爬 iesdouyin.com，无需任何外部依赖**