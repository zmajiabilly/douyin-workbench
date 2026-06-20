"""抖音页面解析 + 视频/音频下载"""
import re, json, time, requests, subprocess, shutil
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 "
                  "Version/17.0 Mobile/15E148 Safari/604.1"
}

DATA_DIR = Path(__file__).parent.parent / "data" / "downloads"

def parse_url(share_url):
    """解析抖音分享链接，返回视频信息"""
    r = requests.get(share_url, headers=HEADERS, allow_redirects=True, timeout=15)
    video_id = r.url.split("?")[0].strip("/").split("/")[-1]
    
    page_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    resp = requests.get(page_url, headers=HEADERS, timeout=15)
    
    match = re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)\s*</script>", flags=re.DOTALL).search(resp.text)
    if not match:
        raise ValueError("无法解析页面数据，可能是链接过期或抖音改版")
    
    data = json.loads(match.group(1))
    for key, val in data.get("loaderData", {}).items():
        if isinstance(val, dict) and "videoInfoRes" in val:
            info = val["videoInfoRes"]["item_list"][0]
            st = info.get("statistics", {})
            au = info.get("author", {})
            vi = info.get("video", {})
            video_url = (vi.get("play_addr", {}) or {}).get("url_list", [None])[0] or ""
            video_url = video_url.replace("playwm", "play")
            
            return {
                "video_id": video_id,
                "url": share_url,
                "title": info.get("desc", ""),
                "author": au.get("nickname", ""),
                "like_count": st.get("digg_count", 0),
                "video_url": video_url,
                "cover_url": (vi.get("cover", {}) or {}).get("url_list", [None])[0] or "",
                "duration": info.get("duration", 0)
            }
    raise ValueError("无法提取视频信息")


def download_video(video_info):
    """下载视频 + 截图封面"""
    video_id = video_info["video_id"]
    title_clean = _safe_name(video_info["title"])
    
    video_dir = DATA_DIR / "videos"
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
    screenshot_dir = DATA_DIR / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / f"{title_clean}_{video_id[:8]}.jpg"
    if video_info.get("cover_url") and not screenshot_path.exists():
        r = requests.get(video_info["cover_url"], headers=HEADERS, timeout=30)
        with open(screenshot_path, "wb") as f:
            f.write(r.content)
    
    # 提取音频
    audio_dir = DATA_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_path = audio_dir / f"{title_clean}_{video_id[:8]}.mp3"
    if not audio_path.exists() and shutil.which("ffmpeg"):
        subprocess.run([
            "ffmpeg", "-i", str(video_path), "-vn",
            "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1",
            "-b:a", "32k", "-y", str(audio_path)
        ], capture_output=True, timeout=300)
    
    return {
        "video_path": str(video_path),
        "audio_path": str(audio_path) if audio_path.exists() else "",
        "screenshot_path": str(screenshot_path) if screenshot_path.exists() else ""
    }

def _safe_name(text, max_len=40):
    text = re.sub(r"#\S+\s*", "", text).strip()
    text = re.sub(r'[\\/:*?"<>|\n\r#：！，（）]', "_", text)[:max_len]
    text = re.sub(r"\s+", "_", text).strip("_")
    return text or "untitled"