"""抖音内容分析管线 — 可独立调用的 Python 包

用法:
    from douyin_pipeline import parser, downloader, asr, llm

    info = parser.parse_url("https://v.douyin.com/xxx/")
    files = downloader.download_video(info)
    transcript = asr.transcribe(files["audio_path"], config)
    summary = llm.summarize(transcript, config)
"""

from . import parser, downloader, asr, llm

__all__ = ["parser", "downloader", "asr", "llm"]
