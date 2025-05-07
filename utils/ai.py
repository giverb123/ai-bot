import os
import requests

def get_ai_response(memory, prompt):
    # Try to extract a username from memory
    user_name = "user"
    for m in memory:
        if m.get("role") == "user" and "name" in m:
            user_name = m["name"]
            break

    system_prompt = {
        "role": "system",
        "content": f"You are a helpful, friendly Discord bot. The user you are speaking to is named {user_name}. If they ask who they are or what their username is, you should be able to answer based on that."
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [system_prompt] + memory + [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
    return response.json()["choices"][0]["message"]["content"]
