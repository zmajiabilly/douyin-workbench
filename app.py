"""抖音工作台 — Flask 入口"""
import datetime
import io
import os
import threading
import time
from pathlib import Path

import yaml
from flask import Flask, jsonify, request, send_from_directory, render_template

from douyin_pipeline import parser, downloader, asr, llm
from db import add_item, update_item, get_item, get_items, get_item_by_video_id, get_all_items, delete_item

app = Flask(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"
DATA_DIR = Path(__file__).parent / "data" / "downloads"


def _load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Pages ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/config")
def config_page():
    return render_template("config.html")


# ── Config API ─────────────────────────────────────────

@app.route("/api/config", methods=["GET"])
def get_config():
    cfg = _load_config()
    # 脱敏：返回时隐藏完整 key，只显示前后 4 位
    for section in ("llm", "asr"):
        for key in list(cfg.get(section, {})):
            val = cfg[section].get(key, "")
            if "key" in key.lower() and val:
                cfg[section][key] = val[:4] + "****" + val[-4:]
    return jsonify(cfg)


@app.route("/api/config", methods=["POST"])
def save_config():
    data = request.get_json(force=True)
    existing = _load_config()

    def _merge(section):
        for key, val in data.get(section, {}).items():
            # 如果传过来的是脱敏值，保留原值
            if "key" in key.lower() and isinstance(val, str) and "****" in val:
                continue
            existing.setdefault(section, {})[key] = val

    _merge("llm")
    _merge("asr")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(existing, f, allow_unicode=True, sort_keys=False)
    return jsonify({"ok": True})


# ── Process ────────────────────────────────────────────

@app.route("/api/process", methods=["POST"])
def process():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    asr_enabled = data.get("asr", True)
    summary_enabled = data.get("summary", True)

    if not url:
        return jsonify({"error": "请输入抖音链接"}), 400

    config = _load_config()

    # 先解析链接，获取 video_id
    try:
        info = parser.parse_url(url)
    except Exception as e:
        return jsonify({"error": f"链接解析失败: {str(e)}"}), 400

    video_id = info.get("video_id", str(time.time()))
    add_item(video_id=video_id, url=url,
             title=info.get("title", ""),
             author=info.get("author", ""),
             like_count=info.get("like_count", 0))

    def _run(info):
        video_id = info["video_id"]
        try:
            update_item(video_id, status="parsing")
            update_item(video_id, status="downloading")
            files = downloader.download_video(info, data_dir=DATA_DIR)
            update_item(video_id,
                        video_path=files["video_path"],
                        audio_path=files["audio_path"],
                        screenshot_path=files["screenshot_path"],
                        status="downloaded")

            if asr_enabled and files.get("audio_path"):
                update_item(video_id, status="transcribing")
                transcript = asr.transcribe(files["audio_path"], config)
                update_item(video_id, transcript=transcript, status="transcribed")

            if summary_enabled:
                update_item(video_id, status="summarizing")
                row = get_item_by_video_id(video_id)
                text_to_summarize = (row or {}).get("transcript", "")
                if text_to_summarize and not text_to_summarize.startswith("("):
                    summary_text = llm.summarize(text_to_summarize, config)
                    update_item(video_id, summary=summary_text)
                if files.get("screenshot_path"):
                    cover_analysis = llm.analyze_cover(files["screenshot_path"], config)
                    existing_tags = ""
                    row2 = get_item_by_video_id(video_id)
                    if row2:
                        existing_tags = row2.get("tags", "") or ""
                    tags = existing_tags + (" | " + cover_analysis[:100] if existing_tags else cover_analysis[:100])
                    update_item(video_id, tags=tags)

            update_item(video_id, status="done")
        except Exception as e:
            try:
                update_item(video_id, status=f"error: {str(e)[:200]}")
            except Exception:
                pass

    threading.Thread(target=_run, args=(info,), daemon=True).start()
    return jsonify({"video_id": video_id}), 202


# ── History ────────────────────────────────────────────

@app.route("/api/history")
def history():
    items = get_items(limit=200)
    return jsonify(items)


@app.route("/api/item/<int:item_id>")
def item_detail(item_id):
    item = get_item(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@app.route("/api/item/<int:item_id>", methods=["DELETE"])
def item_delete(item_id):
    item = get_item(item_id)
    if item:
        for path_key in ("video_path", "audio_path", "screenshot_path"):
            p = item.get(path_key)
            if p and Path(p).exists():
                try:
                    Path(p).unlink()
                except OSError:
                    pass
    delete_item(item_id)
    return jsonify({"ok": True})


# ── Export ─────────────────────────────────────────────

@app.route("/api/export")
def export_excel():
    from openpyxl import Workbook

    items = get_all_items()

    wb = Workbook()
    ws = wb.active
    ws.title = "抖音素材"
    headers = ["标题", "原始链接", "作者", "点赞量", "视频创建时间", "下载时间",
               "标签", "内容总结", "AI总结"]
    ws.append(headers)

    for item in items:
        ws.append([
            item.get("title", ""),
            item.get("url", ""),
            item.get("author", ""),
            item.get("like_count", 0),
            _fmt_time(item.get("created_at")),
            _fmt_time(item.get("updated_at")),
            item.get("tags", ""),
            item.get("transcript", ""),
            item.get("summary", ""),
        ])

    import io
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue(), 200, {
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition": "attachment; filename=douyin_export.xlsx",
    }


def _get_all_items():
    conn = get_db()
    rows = conn.execute("SELECT * FROM items ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _fmt_time(ts):
    if not ts:
        return ""
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


# ── Static files ───────────────────────────────────────

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(str(DATA_DIR), filename)


# ── Startup ────────────────────────────────────────────

if __name__ == "__main__":
    # 确保下载目录存在
    for sub in ("videos", "audio", "screenshots"):
        (DATA_DIR / sub).mkdir(parents=True, exist_ok=True)

    print("🚀 抖音工作台启动: http://127.0.0.1:8650")
    app.run(host="127.0.0.1", port=8650, debug=False)
