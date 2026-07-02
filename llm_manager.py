# -*- coding: utf-8 -*-
"""
LLM Manager Module per LTX & Wan2GP Prompt Agent Studio.
Gestisce le comunicazioni con Ollama, LM Studio e il modello locale interno.
Supporta input multimodale (immagini codificate in Base64).
"""

import os
import io
import json
import base64
import requests
from PIL import Image

def encode_image_base64(image_path: str, max_size=(1024, 1024)) -> str:
    """Carica un'immagine, la ridimensiona se necessario per ottimizzare l'invio all'LLM e la converte in Base64 JPEG."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Errore nella codifica dell'immagine {image_path}: {e}")
        return ""


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def check_connection(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate(self, model: str, system_prompt: str, user_prompt: str, image_paths: list = None, temperature: float = 0.7) -> str:
        url = f"{self.base_url}/api/chat"
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        user_msg = {"role": "user", "content": user_prompt}
        if image_paths:
            b64_images = [encode_image_base64(p) for p in image_paths if p]
            b64_images = [b for b in b64_images if b]
            if b64_images:
                user_msg["images"] = b64_images
                
        messages.append(user_msg)
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "").strip()


class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234"):
        self.base_url = base_url.rstrip("/")

    def check_connection(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/v1/models", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        try:
            resp = requests.get(f"{self.base_url}/v1/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return []

    def generate(self, model: str, system_prompt: str, user_prompt: str, image_paths: list = None, temperature: float = 0.7) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if image_paths:
            content_list = [{"type": "text", "text": user_prompt}]
            for p in image_paths:
                b64 = encode_image_base64(p)
                if b64:
                    content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
            messages.append({"role": "user", "content": content_list})
        else:
            messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


class LocalModelDownloader:
    """Gestisce il download di modelli GGUF compatti da Hugging Face per l'esecuzione in locale."""
    RECOMMENDED_MODELS = {
        "Qwen 2.5 0.5B (Veloce/Leggero - 350MB)": {
            "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
            "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf"
        },
        "Llama 3.2 1B (Bilanciato - 700MB)": {
            "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
            "filename": "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
        }
    }

    def __init__(self, models_dir="models"):
        self.models_dir = os.path.abspath(models_dir)
        os.makedirs(self.models_dir, exist_ok=True)

    def get_downloaded_models(self) -> list:
        if not os.path.exists(self.models_dir):
            return []
        return [f for f in os.listdir(self.models_dir) if f.endswith(".gguf")]

    def download_model(self, model_key: str, progress_callback=None) -> str:
        if model_key not in self.RECOMMENDED_MODELS:
            raise ValueError("Modello non trovato tra i raccomandati.")
        
        info = self.RECOMMENDED_MODELS[model_key]
        dest_path = os.path.join(self.models_dir, info["filename"])
        if os.path.exists(dest_path):
            if progress_callback:
                progress_callback(100.0, "Già scaricato")
            return dest_path

        resp = requests.get(info["url"], stream=True, timeout=30)
        resp.raise_for_status()
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0

        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0 and progress_callback:
                        pct = (downloaded / total_size) * 100.0
                        mb_d = downloaded / (1024*1024)
                        mb_t = total_size / (1024*1024)
                        progress_callback(pct, f"Download: {mb_d:.1f} MB / {mb_t:.1f} MB")
        
        if progress_callback:
            progress_callback(100.0, "Completato!")
        return dest_path
