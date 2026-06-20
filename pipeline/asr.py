"""语音识别 — ASR 转写口播文案（仅 SiliconFlow 云端）"""
import requests

def transcribe(audio_path, config):
    """转写音频为文字，返回完整文案"""
    # 从 asr 配置取 Key，没有则从 llm 配置借
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
    
    return resp.text.strip()