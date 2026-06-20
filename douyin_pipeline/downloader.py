"""视频/音频/封面下载 — 下载抖音素材到本地

参考: ~/scripts/douyin-pipeline.py 的 download_audio + pipeline/douyin.py 的 download_video
"""
import re
import subprocess
import shutil
from pathlib import Path

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 "
                  "Version/17.0 Mobile/15E148 Safari/604.1"
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "downloads"


def download_video(video_info, data_dir=None):
    """下载视频 + 封面截图 + 提取音频

    Args:
        video_info: parser.parse_url() 返回的字典
        data_dir: 下载目录，默认 data/downloads/

    Returns:
        dict: video_path, audio_path, screenshot_path
    """
    base_dir = Path(data_dir) if data_dir else DATA_DIR
    video_id = video_info["video_id"]
    title_clean = _safe_name(video_info["title"])

    video_dir = base_dir / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    video_path = video_dir / f"{title_clean}_{video_id[:8]}.mp4"

    # 下载视频
    if not video_path.exists():
        r = requests.get(video_info["video_url"], headers=HEADERS, timeout=120, stream=True)
        r.raise_for_status()
        with open(video_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)

    # 下载封面
    screenshot_dir = base_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / f"{title_clean}_{video_id[:8]}.jpg"
    if video_info.get("cover_url") and not screenshot_path.exists():
        r = requests.get(video_info["cover_url"], headers=HEADERS, timeout=30)
        with open(screenshot_path, "wb") as f:
            f.write(r.content)

    # 提取音频
    audio_dir = base_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_path = audio_dir / f"{title_clean}_{video_id[:8]}.mp3"
    if not audio_path.exists():
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            subprocess.run([
                ffmpeg, "-i", str(video_path), "-vn",
                "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1",
                "-b:a", "32k", "-y", str(audio_path)
            ], capture_output=True, timeout=300)

    return {
        "video_path": str(video_path),
        "audio_path": str(audio_path) if audio_path.exists() else "",
        "screenshot_path": str(screenshot_path) if screenshot_path.exists() else "",
    }


def _safe_name(text, max_len=40):
    """清理文件名中的特殊字符"""
    text = re.sub(r"#\S+\s*", "", text).strip()
    text = re.sub(r'[\\/:*?"<>|\n\r#：！，（）]', "_", text)[:max_len]
    text = re.sub(r"\s+", "_", text).strip("_")
    return text or "untitled"
