import json


def search_user(user_id):

    with open("data/users.json", "r") as f:
        users = json.load(f)

    for user in users:
        if user["user_id"] == user_id:
            return user

    return None