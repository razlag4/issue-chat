import json
import os

USERS_FILE = os.path.join("public", "users.json")
REAL_USERS_FILE = os.path.join("public", "real_users.json")

with open(USERS_FILE, 'r', encoding='utf-8') as f:
    users = json.load(f)

filtered_users = [u for u in users if not u.get('deleted') and not u.get('is_bot')]

with open(REAL_USERS_FILE, 'w', encoding='utf-8') as f:
    json.dump(filtered_users, f, ensure_ascii=False, indent=4)

print(f"Всего участников: {len(users)}")
print(f"Живых людей: {len(filtered_users)}")
