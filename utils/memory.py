from tinydb import TinyDB, Query

db = TinyDB("memory/user_data.json")

def get_user_memory(user_id):
    result = db.get(Query().user_id == user_id)
    return result["memory"] if result else []

def update_user_memory(user_id, message):
    result = db.get(Query().user_id == user_id)
    if result:
        result["memory"].append(message)
        db.update({"memory": result["memory"]}, Query().user_id == user_id)
    else:
        db.insert({"user_id": user_id, "memory": [message]})

def update_user_profile(user_id, profile_data):
    result = db.get(Query().user_id == user_id)
    memory_entry = {"role": "profile", **profile_data}

    if result:
        # Remove old profile if exists
        new_memory = [m for m in result["memory"] if m.get("role") != "profile"]
        new_memory.insert(0, memory_entry)
        db.update({"memory": new_memory}, Query().user_id == user_id)
    else:
        db.insert({"user_id": user_id, "memory": [memory_entry]})
