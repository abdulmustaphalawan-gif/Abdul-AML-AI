import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def get_user(memory, user_id):
    user_id = str(user_id)

    if user_id not in memory:
        memory[user_id] = {
            "name": "",
            "history": [],
            "facts": {},
            "preferences": {}
        }

    return memory[user_id]


def add_history(memory, user_id, message):
    user = get_user(memory, user_id)

    user["history"].append(message)

    if len(user["history"]) > 20:
        user["history"] = user["history"][-20:]

    save_memory(memory)


def remember_fact(memory, user_id, key, value):
    user = get_user(memory, user_id)
    user["facts"][key] = value
    save_memory(memory)


def get_fact(memory, user_id, key):
    user = get_user(memory, user_id)
    return user["facts"].get(key)


def set_preference(memory, user_id, key, value):
    user = get_user(memory, user_id)
    user["preferences"][key] = value
    save_memory(memory)


def get_preference(memory, user_id, key):
    user = get_user(memory, user_id)
    return user["preferences"].get(key)


def clear_user(memory, user_id):
    user_id = str(user_id)
    if user_id in memory:
        del memory[user_id]
        save_memory(memory)
