import os
import json
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUR_TELEGRAM_ID = int(os.getenv("YOUR_TELEGRAM_ID"))

ADMINS = [YOUR_TELEGRAM_ID, 2123680656]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENTS_FILE = os.path.join(BASE_DIR, "ivents.json")
if not os.path.exists(EVENTS_FILE):
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

client = TelegramClient("iventsbot_new_session", API_ID, API_HASH)

def load_events():
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_events(events):
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

@client.on(events.NewMessage(pattern=r"^[/\.]start"))
async def start_handler(event):
    await event.respond(
        "Привет! Я бот для управления ивентами.\n\n"
        "Команды:\n"
        "/add Название | ссылка | дни:часы:минут — добавить ивент\n"
        "/list — список ивентов\n"
        "/delete номер — удалить ивент"
    )

@client.on(events.NewMessage(pattern=r"^[/\.]add"))
async def add_handler(event):
    if event.sender_id not in ADMINS:
        await event.respond("❌ У тебя нет прав для добавления ивентов.")
        return
    try:
        parts = event.raw_text.split(" ", 1)
        if len(parts) < 2:
            await event.respond("Используй: `/add Название | ссылка | дни:часы:минут`")
            return
        data = parts[1].split("|")
        if len(data) < 3:
            await event.respond("Нужно указать: Название | ссылка | дни:часы:минут")
            return
        name = data[0].strip()
        link = data[1].strip()
        days, hours, minutes = map(int, data[2].strip().split(":"))
        end_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
        end_time_str = end_time.isoformat()
        events_list = load_events()
        events_list.append({"name": name, "link": link, "end_time": end_time_str})
        save_events(events_list)
        await event.respond(
            f"✅ Ивент добавлен:\n\n<b>{name}</b>\n🔗 {link}\n⏳ До окончания через {days}д {hours}ч {minutes}м",
            parse_mode="html"
        )
    except Exception as e:
        await event.respond(f"Ошибка: {e}")

@client.on(events.NewMessage(pattern=r"^[/\.]list"))
async def list_handler(event):
    events_list = load_events()
    if not events_list:
        await event.respond("📭 Список ивентов пуст.")
        return
    text = "📌 Текущие ивенты:\n\n"
    for i, ev in enumerate(events_list, 1):
        end_dt = datetime.fromisoformat(ev['end_time'])
        diff = end_dt - datetime.now()
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        text += f"{i}. <b>{ev['name']}</b>\n🔗 {ev['link']}\n⏳ До окончания: {days}д {hours}ч {minutes}м\n\n"
    await event.respond(text, parse_mode="html")

@client.on(events.NewMessage(pattern=r"^[/\.]delete"))
async def delete_handler(event):
    if event.sender_id not in ADMINS:
        await event.respond("❌ У тебя нет прав для удаления ивентов.")
        return
    parts = event.raw_text.split(" ", 1)
    if len(parts) < 2 or not parts[1].isdigit():
        await event.respond("Используй: `/delete номер`")
        return
    idx = int(parts[1]) - 1
    events_list = load_events()
    if idx < 0 or idx >= len(events_list):
        await event.respond("❌ Нет ивента с таким номером.")
        return
    removed = events_list.pop(idx)
    save_events(events_list)
    await event.respond(f"🗑️ Ивент <b>{removed['name']}</b> удален.", parse_mode="html")

async def start_bot():
    await client.start(bot_token=BOT_TOKEN)
    me = await client.get_me()
    print(f"✅ Бот запущен: @{me.username} (id: {me.id})")
    await client.run_until_disconnected()

app = Flask(__name__)
CORS(app)

@app.route("/events")
def get_events():
    return jsonify(load_events())

@app.route("/delete-event", methods=["POST"])
def delete_event():
    data = request.get_json()
    name = data.get("name")
    events_list = load_events()
    events_list = [ev for ev in events_list if ev.get("name") != name]
    save_events(events_list)
    return jsonify({"status": "ok"})

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(start_bot())
