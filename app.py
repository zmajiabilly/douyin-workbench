"""抖音工作台 — Flask 后端"""
import os, sys, yaml, time, json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

# 确保模块路径正确
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import db, douyin, asr as asr_mod, llm as llm_mod

app = Flask(__name__)

# ── 加载配置 ──
CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)

# ── 页面路由 ──
@app.route("/")
def index():
    return render_template("index.html")

# ── 配置页面 ──
@app.route("/config")
def config_page():
    return render_template("config.html", config=load_config())

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

@app.route("/api/config", methods=["POST"])
def update_config():
    cfg = load_config()
    data = request.get_json()
    # 更新 llm
    if "llm" in data:
        cfg.setdefault("llm", {}).update(data["llm"])
    if "asr" in data:
        cfg.setdefault("asr", {}).update(data["asr"])
    if "proxy" in data:
        cfg.setdefault("proxy", {}).update(data["proxy"])
    save_config(cfg)
    return jsonify({"status": "ok", "config": cfg})

# ── 处理单条链接 ──
@app.route("/api/process", methods=["POST"])
def process():
    data = request.get_json()
    url = data.get("url", "").strip()
    do_asr = data.get("asr", True)       # 是否做语音转写
    do_summary = data.get("summary", True)  # 是否做 AI 总结
    
    if not url:
        return jsonify({"error": "请输入抖音链接"}), 400
    if "douyin.com" not in url and "iesdouyin.com" not in url:
        return jsonify({"error": "请输入有效的抖音链接"}), 400
    
    config = load_config()
    
    try:
        # 1. 解析页面
        info = douyin.parse_url(url)
        
        # 2. 写入数据库
        item = db.add_item(
            info["video_id"], url,
            title=info["title"],
            author=info["author"],
            like_count=info.get("like_count", 0)
        )
        
        # 3. 下载视频 + 音频 + 封面
        files = douyin.download_video(info)
        db.update_item(info["video_id"], **files, status="downloaded")
        
        result = {
            "status": "ok",
            "item": {**info, **files}
        }
        
        # 4. ASR 转写
        if do_asr and files.get("audio_path"):
            transcript = asr_mod.transcribe(files["audio_path"], config)
            db.update_item(info["video_id"], transcript=transcript, status="transcribed")
            result["transcript"] = transcript
        else:
            transcript = ""
            result["transcript"] = ""
        
        # 5. LLM 总结
        if do_summary and transcript and not transcript.startswith("("):
            summary = llm_mod.summarize(transcript, config)
            db.update_item(info["video_id"], summary=summary, status="done")
            result["summary"] = summary
        
        # 6. 视觉分析封面
        if do_summary and files.get("screenshot_path"):
            vision = llm_mod.analyze_cover(files["screenshot_path"], config)
            result["vision"] = vision
        
        result["status"] = "done"
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"处理失败: {str(e)}"}), 500

# ── 历史列表 ──
@app.route("/api/history")
def history():
    items = db.get_items(limit=100)
    return jsonify({"items": items})

@app.route("/api/item/<int:item_id>")
def item_detail(item_id):
    item = db.get_item(item_id)
    if not item:
        return jsonify({"error": "不存在"}), 404
    return jsonify({"item": item})

@app.route("/api/item/<int:item_id>", methods=["DELETE"])
def item_delete(item_id):
    item = db.get_item(item_id)
    if item:
        # 清理文件
        for key in ("video_path", "audio_path", "screenshot_path"):
            p = item.get(key)
            if p and Path(p).exists():
                Path(p).unlink(missing_ok=True)
        db.delete_item(item_id)
    return jsonify({"status": "ok"})

# ── 静态文件下载 ──
@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(str(Path(__file__).parent / "data" / "downloads"), filename)

# ── 启动 ──
if __name__ == "__main__":
    import webbrowser
    print("=" * 45)
    print("  抖音工作台已启动")
    print(f"  打开浏览器访问：http://127.0.0.1:8650")
    print("  Ctrl+C 停止服务")
    print("=" * 45)
    webbrowser.open("http://127.0.0.1:8650")
    app.run(host="127.0.0.1", port=8650, debug=False)