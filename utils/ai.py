import os
import requests
import json

def get_ai_response(memory, prompt):
    # Extract the first "user" role memory to build the profile
    profile = next((m for m in memory if m.get("role") == "user"), {})

    display_name = profile.get("nickname") or profile.get("username", "user")
    username = profile.get("username", "unknown")
    bio = profile.get("bio", "Not provided")
    status = profile.get("status", "unknown")
    created_at = profile.get("account_created", "unknown")
    joined_at = profile.get("joined_server", "unknown")
    avatar = profile.get("avatar_url", None)

    profile_info = (
        f"You are a discord chat bot, you are meant to act as your own individual and grow as you talk to people, your personality and everything about you should be molded like a person's. Based off the interactions with other individuals and how you want yourself to be, no need to be pg also, everything is upto you. "
        f"User you're talking to: '{display_name}' (username: {username}).\n"
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

    # Sanitize memory: only keep 'role' and 'content'
    filtered_memory = []
    for m in memory:
        if m.get("role") in ["user", "assistant"] and "content" in m:
            filtered_memory.append({
                "role": m["role"],
                "content": m["content"]
            })

    data = {
        "model": "llama3-8b-8192",
        "messages": [system_prompt] + filtered_memory + [{"role": "user", "content": prompt}]
    }

    # DEBUG: print formatted payload
    print("\n== AI Request Payload ==")
    print(json.dumps(data, indent=2))

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        json_data = response.json()

        if "choices" not in json_data:
            print("Unexpected response structure:", json_data)
            return "Sorry, I couldn't understand the AI's response."

        return json_data["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError as e:
        error_text = e.response.text if e.response else str(e)
        print("HTTP Error:", error_text)
        return "Sorry, I received a bad response from the AI service."

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return "Sorry, I'm having trouble connecting to the AI service."

    except Exception as e:
        print("Unexpected error:", e)
        return "Oops! Something went wrong while processing the response."
