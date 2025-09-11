import os
import json
import shutil
import time
import pytz
import asyncio
from datetime import datetime
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
load_dotenv(os.path.join(BASE_DIR, "serrc.env"))


try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_USERNAME = os.getenv("CHAT_USERNAME", "@CHAT_ISSUE")
    YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID", "380051255"))
except Exception as e:
    raise RuntimeError(f"Ошибка при получении переменных окружения: {e}")



PHOTOS_DIR = os.path.join(BASE_DIR, "photos")       
USERS_FILE = os.path.join(BASE_DIR, "users.json")  
VOTES_FILE = os.path.join(BASE_DIR, "votes.json") 


client = TelegramClient("bot_session", API_ID, API_HASH)



if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}





last_info_time = {}

def load_users():
    try:
        with open(os.path.join(BASE_DIR, "users.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_users(users):
    with open(os.path.join(BASE_DIR, "users.json"), "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def get_user(user_id):
    users = load_users()
    for user in users:
        if str(user.get('id')) == str(user_id):
            return user
    return None

async def update_first_name(user_id, new_name):
    users = load_users()
    for user in users:
        if str(user.get('id')) == str(user_id):
            user['first_name'] = new_name
            save_users(users)
            return
    users.append({
        "id": user_id,
        "first_name": new_name,
        "username": None,
        "hidden": False,
        "blocked": False
    })
    save_users(users)

async def change_name_by_id(user_id, new_name):
    await update_first_name(user_id, new_name)

async def hide_siteinfo(user_id):
    users = load_users()
    for user in users:
        if str(user.get('id')) == str(user_id):
            user['id'] = "скрыто пользователем"
            user['username'] = "скрыто пользователем"
            user['hidden'] = True
            save_users(users)
            return
    users.append({
        "id": "скрыто пользователем",
        "username": "скрыто пользователем",
        "first_name": "",
        "hidden": True,
        "blocked": False
    })
    save_users(users)

async def show_siteinfo(user_id, sender=None):
    users = load_users()
    real_id = sender.id if sender else user_id
    username = sender.username if sender else ""
    for user in users:
        if str(user.get('id')) == str(user_id) or user.get('id') == "скрыто пользователем":
            user['id'] = real_id
            user['username'] = username
            user['hidden'] = False
            if sender:
                user['first_name'] = sender.first_name
            save_users(users)
            return
    users.append({
        "id": real_id,
        "username": username,
        "first_name": sender.first_name if sender else "",
        "hidden": False,
        "blocked": False
    })
    save_users(users)

async def set_block_status(user_id, blocked=True):
    users = load_users()
    for user in users:
        if str(user.get('id')) == str(user_id):
            user['blocked'] = blocked
            save_users(users)
            return
    users.append({
        "id": user_id,
        "first_name": "",
        "username": "",
        "hidden": False,
        "blocked": blocked
    })
    save_users(users)

async def get_first_name(user_id):
    user = get_user(user_id)
    if user:
        return user.get('first_name')
    return None

async def is_blocked(user_id):
    user = get_user(user_id)
    return user.get('blocked', False) if user else False

VOTES_FILE = os.path.join(BASE_DIR, "votes.json")


def load_votes():
    try:
        with open(VOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_votes(votes):
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)


NOMINATION_NAMES = [
    "«ᴨиᴋʍи чᴀᴛᴀ»",
    "«ᴧюбиʍчиᴋ чᴀᴛᴀ»",
    "«ᴋᴩинж чᴀᴛᴀ»",
    "«бᴧудницᴀ чᴀᴛᴀ»",
    "«бᴀбниᴋ чᴀᴛᴀ»",
    "«нᴀᴄᴛоящий джᴇнᴛᴇᴧьʍᴇн чᴀᴛᴀ»",
    "«ʙᴄᴇзнᴀйᴋᴀ чᴀᴛᴀ»",
    "«хуᴇᴄоᴄ чᴀᴛᴀ»",
    "«ныᴛиᴋ чᴀᴛᴀ»",
    "«϶ᴦоиᴄᴛ чᴀᴛᴀ»",
]

NOMINATIONS = [
    f"уᴋᴀжиᴛᴇ ɪᴅ до ᴛᴩᴇх чᴇᴧоʙᴇᴋ нᴀ ᴄᴧᴇдующую ноʍинᴀцию:\n{name}"
    for name in NOMINATION_NAMES
]

user_states = {}

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.name\s+(.+)'))
async def change_name(event):
    user_id = event.sender_id
    if await is_blocked(user_id):
        await event.reply("❌ Тебе запрещено менять имя.")
        return
    new_name = event.pattern_match.group(1).strip()
    if len(new_name) > 25:
        await event.reply("❌ Имя не может быть длиннее 25 символов")
        return
    await update_first_name(user_id, new_name)
    await event.reply(f'✅ Твоё имя успешно изменено на "{new_name}"')

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.-name'))
async def reset_name(event):
    user_id = event.sender_id
    if await is_blocked(user_id):
        await event.reply("❌ Тебе запрещено менять имя.")
        return
    new_name = event.sender.first_name
    await update_first_name(user_id, new_name)
    await event.reply(f'✅ Твоё имя сброшено на дефолтное: "{new_name}"')

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.myname'))
async def myname(event):
    user_id = event.sender_id
    name = await get_first_name(user_id)
    if not name:
        name = event.sender.first_name
    await event.reply(f'ℹ️ Твоё текущее имя на сайте: {name}')

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.namechange\s+(\d+)\s+(.+)'))
async def namechange_handler(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        await event.reply("❌ У тебя нет прав на эту команду.")
        return
    target_id = event.pattern_match.group(1)
    new_name = event.pattern_match.group(2).strip()
    if new_name == "-name":
        for participant in await client.get_participants(CHAT_USERNAME):
            if str(participant.id) == str(target_id):
                new_name = participant.first_name
                break
    await change_name_by_id(target_id, new_name)
    await event.reply(f'✅ Имя пользователя с ID {target_id} изменено на "{new_name}"')

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.-siteinfo\s*(\d*)'))
async def hide_info(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        await event.reply("❌ У тебя нет прав на эту команду.")
        return
    target_id = event.pattern_match.group(1) or event.sender_id
    await hide_siteinfo(target_id)
    await event.reply(f"🔒 Информация пользователя с ID {target_id} скрыта на сайте.")

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.\+siteinfo\s*(\d*)'))
async def show_info(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        await event.reply("❌ У тебя нет прав на эту команду.")
        return
    target_id = event.pattern_match.group(1) or event.sender_id
    await show_siteinfo(target_id, sender=event.sender)
    await event.reply(f"✅ Информация пользователя с ID {target_id} теперь отображается на сайте.")

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.-user\s+(\d+)'))
async def block_user(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        await event.reply("❌ У тебя нет прав на эту команду.")
        return
    target_id = event.pattern_match.group(1)
    await set_block_status(target_id, blocked=True)
    await event.reply(f"⛔ Пользователь с ID {target_id} теперь не может менять имя и показывать ID на сайте.")

async def update_users_info():
    users = load_users()
    participants = await client.get_participants(CHAT_USERNAME)

    for participant in participants:
        user_id = str(participant.id)
        username = participant.username
        first_name = participant.first_name or ""
        photo_url = f"https://razlag4.github.io/Issue-photos/{user_id}.jpg"

        found = False
        for user in users:
            if str(user.get("id")) == user_id:
                user["username"] = username
                user["first_name"] = first_name
                user["photo"] = photo_url
                found = True
                break
        if not found:
            users.append({
                "id": user_id,
                "username": username,
                "first_name": first_name,
                "photo": photo_url,
                "hidden": False,
                "blocked": False
            })
    save_users(users)

async def periodic_photo_update():
    while True:
        try:
            await update_users_info()  
            print("✅ Информация о пользователях и аватарках обновлена")
        except Exception as e:
            print("Ошибка при обновлении информации:", e)
        await asyncio.sleep(3600)  # 1 час


@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.\+user\s+(\d+)'))
async def unblock_user(event):
    if event.sender_id != YOUR_TELEGRAM_ID:
        await event.reply("❌ У тебя нет прав на эту команду.")
        return
    target_id = event.pattern_match.group(1)
    await set_block_status(target_id, blocked=False)
    await event.reply(f"✅ Пользователь с ID {target_id} снова может менять имя и показывать ID на сайте.")

@client.on(events.NewMessage(chats=CHAT_USERNAME, pattern=r'\.info'))
async def info_command(event):
    user_id = event.sender_id
    now = time.time()
    if user_id in last_info_time and now - last_info_time[user_id] < 15:
        await event.reply("⏳ Подожди 15 секунд перед повторным использованием команды.")
        return
    last_info_time[user_id] = now
    info_text = (
        ".name имя — поменять своё имя на сайте\n"
        ".-name — вернуть имя на то, что стоит в тг\n"
        ".myname — узнать своё текущее имя на сайте\n"
        ".-siteinfo — скрыть свой ID и username на сайте\n"
        ".+siteinfo — снова показать свой ID и username на сайте\n\n"
        "Для администратора:\n"
        ".namechange id новое_имя — изменить имя пользователя с указанным ID. Если вместо имени написать -name, вернётся имя из тг\n"
        ".-siteinfo id — скрыть ID и username указанного пользователя\n"
        ".+siteinfo id — показать ID и username указанного пользователя\n"
        ".-user id — запретить пользователю менять имя и показывать ID на сайте\n"
        ".info — посмотреть все команды в боте\n"
        ".+user id — разрешить пользователю менять имя и показывать ID на сайте"
    )
    await event.reply(info_text)

@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    user_id = str(event.sender_id)
    votes = load_votes()

    if user_id in votes:
        await event.respond("Ты уже участвовал в голосовании.")
        return

    user_states[user_id] = {"step": 0, "answers": []}

    await event.respond(
        "━━━━━━━━━━━━━━━━━━\n"
        "      ✨ ноʙоᴦодняя ноʍинᴀция ✨\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "оᴛᴋᴩыᴛо ᴦоᴧоᴄоʙᴀниᴇ нᴀ ᴇжᴇᴦодную ноʍинᴀцию!\n\n"
        "дᴧя учᴀᴄᴛия уᴋᴀжиᴛᴇ оᴛ 1 до 3 чᴇᴧоʙᴇᴋ нᴀ ʙыбᴩᴀнную ᴋᴀᴛᴇᴦоᴩию.\n\n"
        "➤ дᴧя удобᴄᴛʙᴀ иᴄᴨоᴧьзуйᴛᴇ ᴄᴨиᴄоᴋ ɪᴅ:\n"
        "https://t.me/+DGoXpsnNmHM4MDUy\n"
        "(ᴄᴨиᴄоᴋ ᴨоᴨоᴧняᴇᴛᴄя до 31.12.25)\n\n"
        "➤ ᴧибо нᴀᴨиɯиᴛᴇ ᴋоʍᴀнду:\n"
        "«.ид» (ʙ оᴛʙᴇᴛ нᴀ ᴄообщᴇниᴇ ᴨоᴧьзоʙᴀᴛᴇᴧя, зᴀ ᴋоᴛоᴩоᴦо ᴦоᴧоᴄуᴇᴛᴇ)\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ᴨо ʙᴄᴇʍ ᴛᴇхничᴇᴄᴋиʍ ʙоᴨᴩоᴄᴀʍ обᴩᴀщᴀᴛьᴄя ᴋ ᴀдʍиниᴄᴛᴩᴀᴛоᴩу.\n"
        "━━━━━━━━━━━━━━━━━━"
    )

   
    await event.respond(NOMINATIONS[0])


@client.on(events.NewMessage)
async def voting_handler(event):
    if not event.is_private:
        return

    text = event.message.message.strip()

    
    if not text or text.startswith("/") or text == "Отправить голоса":
        return

    entries = text.split()
    valid_entries = []

    users = load_users()
    
   
    for entry in entries:
        
        if entry.startswith("@"):
            entry = entry[1:]
        
        found = False
        for u in users:
            if str(u.get("id")) == entry or (u.get("username") and u.get("username") == entry):
                found = True
                break
        if found:
            valid_entries.append(entry)
        else:
            await event.respond(f"❌ Пользователь с ID '{entry}' не найден в базе.")
            return

    user_id = str(event.sender_id)
    state = user_states.get(user_id)
    if not state:
        return

    
    state["answers"].append({
        "nomination": NOMINATION_NAMES[state["step"]],
        "votes": valid_entries
    })

    state["step"] += 1

    if state["step"] < len(NOMINATIONS):
        nom_text = NOMINATIONS[state["step"]]
        await event.respond(nom_text)
    else:
        buttons = [Button.text("Отправить голоса", single_use=True)]
        await event.respond(
            "✅ Все номинации заполнены. Отправить?\nPS.Если кнопка не появилась, напиши - Отправить голоса",
            buttons=buttons
        )


@client.on(events.NewMessage(pattern=r'^Отправить голоса$'))
async def submit_handler(event):
    if not event.is_private:
        return
    user_id = str(event.sender_id)
    if user_id not in user_states:
        await event.respond("Нету активного голосования. Нажми /start чтобы начать.")
        return
    state = user_states.pop(user_id)
    votes = load_votes()
    
    moscow_tz = pytz.timezone("Europe/Moscow")
    timestamp = datetime.now(moscow_tz).strftime('%Y-%m-%d %H:%M:%S') + " (по МСК)"
    votes[user_id] = {"answers": state["answers"], "time": timestamp}
    save_votes(votes)

    
    site_name = await get_first_name(event.sender_id)
    if not site_name:
        sender = await event.get_sender()
        site_name = sender.first_name if sender else ""
    
    text = f"📊 Новый голос от {event.sender_id} ({site_name})\n\n"
    for answer in state["answers"]:
        nomination = answer["nomination"]
        votes_list = ", ".join(answer["votes"])
        text += f"{nomination}: {votes_list}\n"
    text += f"\nВремя: {timestamp}"

    
    await client.send_message(YOUR_TELEGRAM_ID, text)
    
    await event.respond("✅ Спасибо, твой голос учтён!")


async def send_stats():
    while True:
        votes = load_votes()
        stats = "ㅤㅤㅤㅤㅤㅤㅤㅤ\n\n"
        for i, nom in enumerate(NOMINATIONS):
            counter = {}
            for v in votes.values():
                ans = v.get("answers", [])
                if i < len(ans):
                    name = ans[i]
                    counter[name] = counter.get(name, 0) + 1
            stats += f"\n{nom}:\n"
            for name, count in sorted(counter.items(), key=lambda x: -x[1]):
                stats += f"  {name}: {count}\n"
        try:
            await client.send_message(YOUR_TELEGRAM_ID, stats)
        except Exception as e:
            print("Ошибка отправки статистики:", e)
        await asyncio.sleep(43200)  # 12 часов


ALLOWED_STATS_IDS = [380051255, 2123680656]

@client.on(events.NewMessage(pattern=r'/stats'))
async def stats_command(event):
    if event.sender_id not in ALLOWED_STATS_IDS:
        await event.reply("❌ У вас нет прав на просмотр статистики.")
        return

    votes = load_votes()
    if not votes:
        await event.reply("📊 Статистика голосования пока пуста.")
        return

    stats = "📢 Статистика голосования (по пользователям):\n\n"
    for user_id, data in votes.items():
        site_name = await get_first_name(int(user_id))
        if not site_name:
            site_name = "Неизвестно"
        stats += f"ID {user_id} ({site_name}):\n"
        answers = data.get("answers", [])
        for i, answer in enumerate(answers):
            stats += f"  {NOMINATIONS[i]} {answer}\n"
        stats += f"Время голосования: {data.get('time', 'неизвестно')}\n\n"

    await event.reply(stats)


async def start_bot():
    await client.start(bot_token=BOT_TOKEN)
    client.loop.create_task(periodic_photo_update())  
    # client.loop.create_task(send_stats())
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
