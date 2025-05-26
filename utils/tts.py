import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN")
VOC_GABRIEL_URL = "https://vocloner.com/tts.php?voiceid=dab61d33633c4758b859a1b89a8f35cd"

HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}"
}

# Hugging Face models
BARK_MODEL = "suno/bark"
TORTOISE_MODEL = "neonbjb/tortoise-tts"

def tts_bark(text):
    url = f"https://api-inference.huggingface.co/models/{BARK_MODEL}"
    payload = {"inputs": text}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print("Bark TTS error:", response.status_code, response.text)
        return None

def tts_tortoise(text):
    url = f"https://api-inference.huggingface.co/models/{TORTOISE_MODEL}"
    payload = {"inputs": text}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print("Tortoise TTS error:", response.status_code, response.text)
        return None

def tts_gabriel(text):
    try:
        response = requests.post(
            VOC_GABRIEL_URL,
            data={"text": text},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.ok and response.headers.get("Content-Type", "").startswith("audio"):
            return response.content
        else:
            print("Gabriel TTS error:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Gabriel TTS exception:", e)
        return None

def generate_tts(text, model="bark"):
    if model == "bark":
        return tts_bark(text)
    elif model == "tortoise":
        return tts_tortoise(text)
    elif model == "gabriel":
        return tts_gabriel(text)
    else:
        raise ValueError("Invalid TTS model specified. Choose 'bark', 'tortoise', or 'gabriel'.")
