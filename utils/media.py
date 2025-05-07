
import os
import requests

def get_gif(query):
    url = f"https://api.tenor.com/v1/search?q={query}&key={os.getenv('TENOR_API_KEY')}&limit=1"
    response = requests.get(url).json()
    return response["results"][0]["media"][0]["gif"]["url"]
