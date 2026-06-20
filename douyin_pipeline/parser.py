"""抖音页面解析 — 从分享链接提取视频信息

直接请求抖音解析页面，不需要 API Key，不需要第三方包。
"""
import json
import re

import requests

# 模拟手机端访问
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 "
                  "Version/17.0 Mobile/15E148 Safari/604.1"
}


def parse_url(share_url):
    """解析抖音分享链接，返回视频信息字典

    Args:
        share_url: 抖音分享链接 (https://v.douyin.com/xxx/)

    Returns:
        dict: video_id, title, author, like_count,
              video_url, cover_url, duration, url

    Raises:
        ValueError: 解析失败时抛出
    """
    # Step 1: 短链接重定向，拿到真实 video_id
    resp = requests.get(share_url.strip(), headers=HEADERS, timeout=15, allow_redirects=True)
    resp.raise_for_status()
    actual_url = resp.url.split("?")[0].rstrip("/")
    video_id = actual_url.split("/")[-1]
    if not video_id or len(video_id) < 10:
        raise ValueError(f"无法从重定向链接提取 video_id: {resp.url}")

    # Step 2: 请求解析页面，提取 _ROUTER_DATA
    info_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    page_resp = requests.get(info_url, headers=HEADERS, timeout=15)
    page_resp.raise_for_status()

    pattern = re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", flags=re.DOTALL)
    m = pattern.search(page_resp.text)
    if not m:
        raise ValueError("页面中未找到 _ROUTER_DATA，抖音可能改版了")

    raw_json = m.group(1).strip()
    router_data = json.loads(raw_json)
    loader = router_data.get("loaderData", {})

    # Step 3: 定位视频数据（支持 video 和 note 两种页面类型）
    page_data = loader.get("video_(id)/page") or loader.get("note_(id)/page") or {}
    item_list = page_data.get("videoInfoRes", {}).get("item_list", [])
    if not item_list:
        raise ValueError("解析页面中无视频数据")

    data = item_list[0]

    # Step 4: 提取关键字段
    desc = data.get("desc", "").strip() or f"douyin_{video_id}"

    # 无水印视频链接
    play_addr = data.get("video", {}).get("play_addr", {})
    url_list = play_addr.get("url_list", [])
    video_url = url_list[0].replace("playwm", "play") if url_list else ""

    # 封面
    cover = data.get("video", {}).get("cover", {})
    cover_url = (cover.get("url_list") or [None])[0] or ""

    # 作者
    author = (data.get("author") or {}).get("nickname", "")

    # 统计
    stats = data.get("statistics") or {}
    like_count = stats.get("digg_count", 0)

    # 时长（毫秒）
    duration = (data.get("video") or {}).get("duration", 0)

    return {
        "video_id": video_id,
        "url": share_url,
        "title": desc,
        "author": author,
        "like_count": like_count,
        "video_url": video_url,
        "cover_url": cover_url,
        "duration": duration,
    }
