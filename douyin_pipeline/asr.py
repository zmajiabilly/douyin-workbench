"""语音识别 — ASR 转写口播文案（SiliconFlow SenseVoice 云端）"""
import requests


def transcribe(audio_path, config):
    """转写音频为文字，返回完整文案

    Args:
        audio_path: 音频文件路径
        config: 配置字典（需包含 asr.siliconflow_api_key 或 llm.siliconflow_api_key）

    Returns:
        str: 转写文本，失败时返回以 ( 开头的错误信息
    """
    api_key = (config.get("asr", {}).get("siliconflow_api_key") or
               config.get("llm", {}).get("siliconflow_api_key") or
               "")

    if not api_key:
        return "(未配置 API Key，请在 config.yaml 中填写 siliconflow_api_key)"

    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    with open(audio_path, "rb") as f:
        files = {"file": (audio_path, f, "audio/mpeg")}
        data = {"model": "FunAudioLLM/SenseVoiceSmall", "response_format": "text"}
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)

    if resp.status_code == 401:
        return "(API Key 无效，请检查 config.yaml 中的 siliconflow_api_key)"
    if resp.status_code != 200:
        return f"(ASR 失败: HTTP {resp.status_code})"

    result = resp.text.strip()
    # SiliconFlow 有时返回 JSON {"text":"..."} 而非纯文本
    if result.startswith('{"text":'):
        import json as _json
        try:
            result = _json.loads(result).get("text", result)
        except Exception:
            pass
    return result
