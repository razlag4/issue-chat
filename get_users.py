from telethon import TelegramClient
import json, os, asyncio
import os
from telethon.errors import FloodWaitError
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
CHAT_USERNAME = os.environ["CHAT_USERNAME"]

client = TelegramClient('session_name', API_ID, API_HASH)
os.makedirs('photos', exist_ok=True)

async def main():
    await client.start()
    users_list = []
    print("Начинаем выгрузку участников...")

    try:
        async for user in client.iter_participants(CHAT_USERNAME, aggressive=False):
            photo_path = None
            if user.photo:
                photo_path = f'photos/{user.id}.jpg'
                await client.download_profile_photo(user, file=photo_path)
            users_list.append({
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.bot,
                "deleted": getattr(user, 'deleted', False),
                "photo": photo_path
            })
            print(f"Собран: {user.id} ({user.first_name})")
            await asyncio.sleep(0.1)

    except FloodWaitError as e:
        print(f"FloodWait {e.seconds}s — ждём...")
        await asyncio.sleep(e.seconds + 1)


    with open(os.path.join("public", "users.json"), 'w', encoding='utf-8') as f:
        json.dump(users_list, f, ensure_ascii=False, indent=4)

    print(f"Готово! Всего участников: {len(users_list)}")

with client:
    client.loop.run_until_complete(main())
