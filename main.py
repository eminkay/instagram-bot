import os
import telebot
import yt_dlp
import telebot
from telebot import apihelper
import subprocess

apihelper.ENABLE_MIDDLEWARE = False  # eski thread'lerin çakışmasını önler


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


# Ortam değişkeninden token al (Render'da BOT_TOKEN olarak ayarlayacaksın)
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# cookies.txt dosyasının konumu (Render'da /etc/secrets/ altına koyacağız)
COOKIES_PATH = "/etc/secrets/cookies.txt"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Instagram Reels indirme botuna hoş geldin! 🎬\nSadece link gönder yeter.")

@bot.message_handler(func=lambda message: True)
def download_reel(message):
    url = message.text.strip()

    if "instagram.com" not in url:
        bot.reply_to(message, "⚠️ Bu geçerli bir Instagram linki değil.")
        return

    bot.reply_to(message, "🎥 Videon indiriliyor, lütfen bekle...")

    try:
        # Video indirme komutu
        output_path = "video.mp4"
        command = [
            "yt-dlp",
            "--cookies", COOKIES_PATH,
            "-o", output_path,
            url
        ]
        subprocess.run(command, check=True)

        # Dosyayı Telegram'a gönder
        with open(output_path, "rb") as video:
            bot.send_video(message.chat.id, video)

        os.remove(output_path)
    except subprocess.CalledProcessError:
        bot.reply_to(message, "❌ Videoyu indirirken hata oluştu. Muhtemelen login gerekiyor veya link geçersiz.")
    except Exception as e:
        bot.reply_to(message, f"🚨 Hata: {e}")

bot.polling(none_stop=True)
