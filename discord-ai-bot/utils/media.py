import os
import requests
import re
import random
from tinydb import TinyDB, Query

# Load or create the local GIF storage DB
gif_db = TinyDB("memory/gifs.json")

# ---------------------
# ✅ TENOR API SEARCH
# ---------------------
def search_tenor(query):
    try:
        url = f"https://api.tenor.com/v1/search?q={query}&key={os.getenv('TENOR_API_KEY')}&limit=1"
        response = requests.get(url).json()
        return response["results"][0]["media"][0]["gif"]["url"]
    except Exception:
        return None

# ---------------------
# ✅ GIPHY API SEARCH
# ---------------------
def search_giphy(query):
    try:
        api_key = os.getenv("GIPHY_API_KEY")  # Optional: Add this to .env if using Giphy
        if not api_key:
            return None
        url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=1&rating=pg"
        response = requests.get(url).json()
        return response["data"][0]["images"]["original"]["url"]
    except Exception:
        return None

# ---------------------
# ✅ Combined Search (Tenor > Giphy fallback)
# ---------------------
def get_gif(query):
    gif_url = search_tenor(query)
    if not gif_url:
        gif_url = search_giphy(query)
    return gif_url

# ---------------------
# ✅ Save a GIF for a specific user
# ---------------------
def save_gif_for_user(user_id, url):
    gif_db.insert({"user_id": user_id, "url": url})

# ---------------------
# ✅ Get all saved GIFs for a user
# ---------------------
def get_saved_gifs(user_id):
    return [entry["url"] for entry in gif_db.search(Query().user_id == user_id)]

# ---------------------
# ✅ Get random saved GIF for a user
# ---------------------
def get_random_user_gif(user_id):
    gifs = get_saved_gifs(user_id)
    return random.choice(gifs) if gifs else None

# ---------------------
# ✅ Extract .gif or Tenor URLs from message text
# ---------------------
def extract_gif_url(text):
    gif_regex = r'(https?://[^\s]+\.gif)'
    tenor_regex = r'(https?://tenor\.com/view/[^\s]+)'
    matches = re.findall(gif_regex, text) + re.findall(tenor_regex, text)
    return matches[0] if matches else None
