"""大模型 — 文案总结 + 视觉分析"""
import requests, json

def summarize(transcript, config):
    """用大模型总结口播文案"""
    if not transcript or transcript.startswith("("):
        return transcript
    
    llm = config.get("llm", {})
    provider = llm.get("provider", "ollama")
    
    prompt = (
        "你是一个内容分析专家。请对以下抖音口播文案进行结构化总结，要求：\n"
        "1. 用 ## 分二级章节（核心观点、具体方法、案例、数据等）\n"
        "2. 包含至少一个对比表格\n"
        "3. 提炼 3-5 个标签\n"
        "4. 保持客观，不评价好坏\n\n"
        f"文案：\n{transcript[:8000]}"
    )
    
    if provider == "ollama":
        return _ollama_chat(llm.get("ollama_url", "http://localhost:11434"),
                           llm.get("text_model", "qwen2.5:7b"), prompt)
    elif provider == "siliconflow":
        return _siliconflow_chat(
            llm.get("siliconflow_api_key", ""),
            llm.get("siliconflow_text_model", "Qwen/Qwen3-8B"),
            prompt
        )
    elif provider == "openai":
        return _openai_chat(
            llm.get("openai_api_key", ""),
            llm.get("openai_text_model", "gpt-4o-mini"),
            prompt
        )
    return "(未配置 LLM)"

def analyze_cover(image_path, config):
    """用视觉模型分析封面/截图"""
    llm = config.get("llm", {})
    provider = llm.get("provider", "ollama")
    
    prompt = "请分析这张图片的内容：画面里有什么、文字写了什么、整体风格如何。"
    
    if provider == "ollama":
        return _ollama_vision(llm.get("ollama_url", "http://localhost:11434"),
                             llm.get("vision_model", "qwen2.5-vl:7b"), image_path, prompt)
    elif provider == "siliconflow":
        return _siliconflow_vision(
            llm.get("siliconflow_api_key", ""),
            llm.get("siliconflow_vision_model", "Qwen/Qwen2.5-VL-7B-Instruct"),
            image_path, prompt
        )
    return "(视觉分析需要配置 vision_model)"

def _ollama_chat(url, model, prompt):
    try:
        resp = requests.post(f"{url}/api/chat", json={
            "model": model, "messages": [{"role": "user", "content": prompt}],
            "stream": False, "options": {"temperature": 0.3}
        }, timeout=60)
        if resp.status_code == 200:
            return resp.json()["message"]["content"]
    except Exception as e:
        return f"(Ollama 调用失败: {e})"
    return "(Ollama 无响应)"

def _ollama_vision(url, model, image_path, prompt):
    import base64
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        resp = requests.post(f"{url}/api/chat", json={
            "model": model,
            "messages": [{
                "role": "user",
                "content": prompt,
                "images": [img_b64]
            }],
            "stream": False, "options": {"temperature": 0.3}
        }, timeout=60)
        if resp.status_code == 200:
            return resp.json()["message"]["content"]
    except Exception as e:
        return f"(视觉分析失败: {e})"
    return "(Ollama 视觉无响应)"

def _siliconflow_chat(api_key, model, prompt):
    if not api_key:
        return "(未配置 API Key)"
    resp = requests.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}],
              "temperature": 0.3, "max_tokens": 2048},
        timeout=120
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"(API 错误: {resp.status_code})"

def _siliconflow_vision(api_key, model, image_path, prompt):
    if not api_key:
        return "(未配置 API Key)"
    import base64
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    resp = requests.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }],
            "temperature": 0.3, "max_tokens": 2048
        },
        timeout=120
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"(视觉 API 错误: {resp.status_code})"

def _openai_chat(api_key, model, prompt):
    if not api_key:
        return "(未配置 API Key)"
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}],
              "temperature": 0.3},
        timeout=120
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"(API 错误: {resp.status_code})"