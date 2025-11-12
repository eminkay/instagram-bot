import os
import telebot
import yt_dlp
import telebot
from telebot import apihelper

apihelper.ENABLE_MIDDLEWARE = False  # eski thread'lerin çakışmasını önler


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 Selam! Instagram Reels linkini gönder, senin için indirip yollarım 📥"
    )

@bot.message_handler(func=lambda m: True)
def download_instagram_reel(message):
    url = message.text.strip()

    if "instagram.com" not in url:
        bot.reply_to(message, "❌ Geçerli bir Instagram Reels linki gönder.")
        return

    bot.reply_to(message, "🎬 Videoyu indiriyorum, biraz bekle...")

    try:
        ydl_opts = {
            "outtmpl": "reel.%(ext)s",
            "quiet": True,
            "format": "mp4",
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)
            video_path = base + ".mp4"

        with open(video_path, "rb") as video:
            bot.send_video(message.chat.id, video)

        bot.reply_to(message, "✅ Reels başarıyla indirildi!")
        os.remove(video_path)

    except Exception as e:
        print(f"Hata: {e}")
        bot.reply_to(message, "⚠️ Bir hata oluştu, lütfen tekrar dene.")

print("🚀 Bot başlatıldı, Reels linklerini bekliyor...")
bot.infinity_polling()

