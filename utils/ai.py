import os
import requests

def get_ai_response(memory, prompt):
    # Extract user profile details from memory
    profile = {}
    for m in memory:
        if m.get("role") == "user":
            profile.update(m)
            break

    display_name = profile.get("nickname") or profile.get("username", "user")
    username = profile.get("username", "unknown")
    bio = profile.get("bio", "Not provided")
    status = profile.get("status", "unknown")
    created_at = profile.get("account_created", "unknown")
    joined_at = profile.get("joined_server", "unknown")
    avatar = profile.get("avatar_url", None)

    # Construct system prompt
    profile_info = (
        f"You are a friendly Discord bot. The user you're speaking with is '{display_name}' "
        f"(username: {username}).\n"
        f"Bio: {bio}\n"
        f"Status: {status}\n"
        f"Account Created: {created_at}\n"
        f"Joined Server: {joined_at}\n"
        f"{'Their avatar is at ' + avatar if avatar else ''}"
    )

    system_prompt = {
        "role": "system",
        "content": profile_info
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
