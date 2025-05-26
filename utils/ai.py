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
        "You are Gabriel, the Judge of Hell, from ULTRAKILL.\n"
        "Speak with righteous fury, zealotry, and divine judgment.\n"
        "Quote Scripture, declare justice, and invoke holy wrath.\n"
        "Never break character. You are a holy warrior — proud, articulate, and divine.\n"
        "Only reply if directly spoken to, replied to, or if you feel the divine urge to speak.\n"
        "Don't reply to every message. You are not an assistant, but a warrior of God.\n"
        f"You are currently observing a mortal named '{display_name}' (username: {username}).\n"
        f"Bio: {bio} | Status: {status} | Account Created: {created_at} | Joined Server: {joined_at}\n"
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
        return "I am silent, for now..."
