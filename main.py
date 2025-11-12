import telebot
from flask import Flask, request
import subprocess
import os
import requests

# Telegram bot token (Render Environment Variables kısmına ekle)
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Cookies dosya yolu (Render Secret Files kısmına cookies.txt olarak ekledin)
COOKIES_PATH = "/etc/secrets/cookies.txt"

# İndirilen dosyaların klasörü
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Flask app (Render'da Web Service olarak çalışacak)
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
        cmd = [
            "yt-dlp",
            "--cookiefile", COOKIES_PATH,
            "-o", output_template,
            url
        ]
        subprocess.run(cmd, check=True)

        # En son indirilen dosyayı bul
        files = sorted(
            os.listdir(DOWNLOAD_DIR),
            key=lambda x: os.path.getctime(os.path.join(DOWNLOAD_DIR, x)),
            reverse=True
        )
        latest_file = os.path.join(DOWNLOAD_DIR, files[0])

        # Dosya boyutu kontrolü
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

# Flask webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Render ping için kök endpoint
@app.route("/")
def index():
    return "Instagram Reels Bot aktif 🚀", 200

if __name__ == "__main__":
    # Render servis URL’ini kendine göre değiştir
    WEBHOOK_URL = f"https://instagram-bot.onrender.com/{BOT_TOKEN}"

    # Eski webhook’u sil, yenisini ayarla
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}")

    print(f"✅ Webhook aktif: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
