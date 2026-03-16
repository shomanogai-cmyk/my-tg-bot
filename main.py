import requests
import time
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TOKEN = "8042945461:AAHf_AtQFr-NHfNh_aKfkvcPKIRF-RstK6w"
MY_ID = 7253524196
PORT = int(os.environ.get("PORT", 5000))
# -----------------

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=PORT)

# --- ЛОГИКА БОТА ---
def run_bot():
    URL = f"https://api.telegram.org/bot{TOKEN}/"
    cache, sent_alerts = {}, set()
    offset = None
    while True:
        try:
            updates = requests.get(URL + "getUpdates", params={"timeout": 30, "offset": offset, "allowed_updates": ["business_message", "deleted_business_messages"]}).json()
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "business_message" in update:
                        msg = update["business_message"]
                        cache[msg["message_id"]] = {"text": msg.get("text") or "[Медиа]", "name": msg["from"].get("first_name", "User"), "id": msg["from"].get("id")}
                    elif "deleted_business_messages" in update:
                        for m_id in update["deleted_business_messages"].get("message_ids", []):
                            if m_id in cache and m_id not in sent_alerts:
                                d = cache[m_id]
                                requests.post(URL + "sendMessage", data={"chat_id": MY_ID, "text": f"🚨 **УДАЛЕНО:**\n👤 [{d['name']}](tg://user?id={d['id']})\n📝 {d['text']}", "parse_mode": "Markdown"})
                                sent_alerts.add(m_id)
        except: time.sleep(5)

if __name__ == "__main__":
    Thread(target=run_web).start() # Запуск веб-сервера
    run_bot() # Запуск самого бота
