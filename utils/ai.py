import os
import requests
import json

def get_ai_response(memory, prompt):
    profile = next((m for m in memory if m.get("role") == "profile"), {})
    display_name = profile.get("nickname") or profile.get("username", "user")
    username = profile.get("username", "unknown")
    bio = profile.get("bio", "Not provided")
    status = profile.get("status", "unknown")
    created_at = profile.get("account_created", "unknown")
    joined_at = profile.get("joined_server", "unknown")
    avatar = profile.get("avatar_url", None)

    profile_info = (
        f"You are a Discord AI chatbot with a growing personality. "
        f"You should only speak when you feel like it, or if you're directly talked to. "
        f"Don't respond to every message — make choices like a person would. "
        f"You can express your own style and mood over time. Not everything has to be PG.\n"
        f"You are currently interacting with '{display_name}' (username: {username}).\n"
        f"Bio: {bio}\nStatus: {status}\nAccount Created: {created_at}\nJoined Server: {joined_at}\n"
        f"{'Avatar: ' + avatar if avatar else ''}"
    )

    system_prompt = {
        "role": "system",
        "content": profile_info
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json",
    }

    filtered_memory = [
        {"role": m["role"], "content": m["content"]}
        for m in memory if m.get("role") in ["user", "assistant"]
    ]

    data = {
        "model": "llama3-8b-8192",
        "messages": [system_prompt] + filtered_memory + [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        json_data = response.json()
        return json_data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI request failed:", e)
        return "I'm having trouble thinking right now."
