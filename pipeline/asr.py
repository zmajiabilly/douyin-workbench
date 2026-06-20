"""语音识别 — ASR 转写口播文案"""
import requests, time

def transcribe(audio_path, config):
    """转写音频为文字，返回完整文案"""
    provider = config.get("asr", {}).get("provider", "siliconflow")
    
    if provider == "siliconflow":
        return _siliconflow_asr(audio_path, config)
    elif provider == "local_whisper":
        return _whisper_asr(audio_path, config)
    else:
        raise ValueError(f"不支持的 ASR 提供商: {provider}")

def _siliconflow_asr(audio_path, config):
    api_key = config.get("asr", {}).get("siliconflow_api_key", "")
    if not api_key:
        # 尝试从 llm 配置借
        api_key = config.get("llm", {}).get("siliconflow_api_key", "")
    if not api_key:
        return "(未配置 API Key，请在 config.yaml 中填写 siliconflow_api_key)"
    
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with open(audio_path, "rb") as f:
        files = {"file": (audio_path, f, "audio/mpeg")}
        data = {"model": "FunAudioLLM/SenseVoiceSmall", "response_format": "text"}
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    
    if resp.status_code != 200:
        return f"(ASR 失败: HTTP {resp.status_code})"
    return resp.text.strip()

def _whisper_asr(audio_path, config):
    try:
        import whisper
    except ImportError:
        return "(需要先安装 openai-whisper: pip install openai-whisper)"
    
    model_name = config.get("asr", {}).get("model", "base")
    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path))
    return result["text"].strip()
