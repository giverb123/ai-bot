
import os
import requests

def get_ai_response(memory, prompt):
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": memory + [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
    return response.json()["choices"][0]["message"]["content"]
