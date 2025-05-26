import os
import requests
from io import BytesIO
from pydub import AudioSegment

def tts_vocloner(text, voice_id):
    try:
        response = requests.post(
            "https://vocloner.com/api/tts",
            headers={"Content-Type": "application/json"},
            json={"voiceid": voice_id, "text": text}
        )
        response.raise_for_status()
        audio_url = response.json().get("audio_url")
        if not audio_url:
            print("No audio URL returned from Vocloner.")
            return None

        # Download the audio
        audio_data = requests.get(audio_url).content
        return audio_data

    except Exception as e:
        print("Vocloner TTS failed:", e)
        return None

def generate_tts(text, model="vocloner"):
    if model == "vocloner":
        voice_id = os.getenv("VOCLONER_VOICE_ID")
        return tts_vocloner(text, voice_id)
    else:
        raise ValueError("Invalid or unsupported TTS model.")
