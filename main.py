import telebot
from flask import Flask, request
import subprocess
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

COOKIES_PATH = "/etc/secrets/cookies.txt"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Flask app (Render'da web service olarak çalışacak)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Selam moruk 👋 Sadece bir Instagram Reels linki at, gerisini hallederim.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if "instagram.com" not in url:
        bot.reply_to(message, "Moruk bu Instagram linki değil 😅")
        return

    bot.reply_to(message, "📥 İndiriyorum, az bekle moruk...")

    try:
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        cmd = ["yt-dlp", "--cookiefile", COOKIES_PATH, "-o", output_template, url]
        subprocess.run(cmd, check=True)

        files = sorted(os.listdir(DOWNLOAD_DIR), key=lambda x: os.path.getctime(os.path.join(DOWNLOAD_DIR, x)), reverse=True)
        latest_file = os.path.join(DOWNLOAD_DIR, files[0])

        if os.path.getsize(latest_file) > 50 * 1024 * 1024:
            bot.reply_to(message, "⚠️ Moruk dosya 50 MB’tan büyük, Telegram izin vermiyor.")
        else:
            with open(latest_file, "rb") as video:
                bot.send_video(message.chat.id, video)
        os.remove(latest_file)

    except subprocess.CalledProcessError:
        bot.reply_to(message, "🚫 Hata oluştu moruk, linki kontrol et.")
    except Exception as e:
        bot.reply_to(message, f"❌ Bi’ şey ters gitti: {str(e)}")


# Telegram webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200


# Root endpoint (Render ping için)
@app.route("/")
def index():
    return "Instagram Bot çalışıyor 🚀", 200


if __name__ == "__main__":
    import requests

    # Render sana bir public URL verir, oraya webhook'u kurmamız gerekiyor
    # Örnek: https://instagram-bot.onrender.com
    WEBHOOK_URL = f"https://instagram-bot.onrender.com/{BOT_TOKEN}"

    # Eski webhook'u kaldır, yenisini ayarla
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")

    print(f"Webhook kuruldu: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
