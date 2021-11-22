import os
from telegram import Bot


BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_CHATID = os.environ.get("CHAT_ID")


class Notifications():

    def __init__(self):
        self.my_cv_bot = Bot(token=BOT_TOKEN)

    def send_message(self, name, email):
        self.my_cv_bot.sendMessage(chat_id=GROUP_CHATID,
                                   text=f"Notification de contacto de eMAGN."
                                        f"\nName: {name}\nEmail: {email}\n")
