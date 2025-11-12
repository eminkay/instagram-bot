import os
import telebot
import yt_dlp
import telebot
from telebot import apihelper
import subprocess
from flask import Flask, request

apihelper.ENABLE_MIDDLEWARE = False  # eski thread'lerin çakışmasını önler


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "instagram.com" not in url:
        bot.reply_to(message, "Lütfen geçerli bir Instagram Reels linki gönder 💬")
        return

    bot.reply_to(message, "🎥 Reels indiriliyor, lütfen bekle...")

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'format': 'mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)

        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {e}")

if __name__ == '__main__':
    # Webhook ayarı (Render linkini buraya yazacaksın)
    webhook_url = "https://instagram-bot-xxxx.onrender.com/" + BOT_TOKEN
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
