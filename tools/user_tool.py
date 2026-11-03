import json

from agent.paths import DATA_DIR


def search_user(user_id):
    with open(DATA_DIR / "users.json", encoding="utf-8") as f:
        users = json.load(f)

    for user in users:
        if user["user_id"] == user_id:
            return user

    return None
