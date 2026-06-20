"""抖音页面解析 — 从分享链接提取视频信息

使用 douyin-mcp-server 库，视频解析无需 API Key，文案提取需要 SiliconFlow Key。
"""
from douyin_mcp_server import parse_douyin_video_info, extract_douyin_text


def parse_url(share_url):
    """解析抖音分享链接，返回视频信息字典

    Args:
        share_url: 抖音分享链接 (https://v.douyin.com/xxx/)

    Returns:
        dict: video_id, url, title, author, like_count,
              video_url, cover_url, duration

    Raises:
        ValueError: 解析失败时抛出
    """
    result = parse_douyin_video_info(share_url)
    if not result:
        raise ValueError("无法解析视频信息，可能是链接过期或抖音改版")
    return result
