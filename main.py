import os
import requests
import time
from flask import Flask
from threading import Thread

# Код берет настройки из панели Render, а не из текста файла
TOKEN = os.environ.get("TOKEN")
MY_ID = os.environ.get("MY_ID")

if not TOKEN or not MY_ID:
    print("Ошибка: Переменные TOKEN или MY_ID не найдены!")
    exit(1)

URL = f"https://api.telegram.org/bot{TOKEN}/"
MY_ID = int(MY_ID)

app = Flask(__name__)
@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

def run_bot():
    cache = {}
    sent_alerts = set()
    offset = None
    while True:
        try:
            res = requests.get(URL + "getUpdates", params={"timeout": 30, "offset": offset, "allowed_updates": ["business_message", "deleted_business_messages"]})
            updates = res.json()
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "business_message" in update:
                        msg = update["business_message"]
                        cache[msg["message_id"]] = {
                            "text": msg.get("text") or msg.get("caption") or "[Медиа]",
                            "name": msg["from"].get("first_name", "User"),
                            "id": msg["from"].get("id")
                        }
                    elif "deleted_business_messages" in update:
                        for m_id in update["deleted_business_messages"].get("message_ids", []):
                            if m_id in cache and m_id not in sent_alerts:
                                d = cache[m_id]
                                link = f"[{d['name']}](tg://user?id={d['id']})"
                                requests.post(URL + "sendMessage", data={"chat_id": MY_ID, "text": f"🚨 **УДАЛЕНО:**\n👤 Кто: {link}\n📝 Текст: {d['text']}", "parse_mode": "Markdown"})
                                sent_alerts.add(m_id)
            if len(cache) > 500: cache.clear(); sent_alerts.clear()
        except: time.sleep(10)

if __name__ == "__main__":
    Thread(target=run_web).start()
    run_bot()
