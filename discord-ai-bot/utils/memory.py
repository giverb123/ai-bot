
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
