import telebot
import yt_dlp

# Telegram Bot Token
BOT_TOKEN = "8355946944:AAEHxTgusJ3skFHsZH9I54IX7k-GkxX_2zY"  # örn: 8355946944:AAEHxTgusJ3...

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Selam! Instagram linkini gönder, videoyu indirip sana atayım.")

@bot.message_handler(func=lambda message: True)
def download_instagram_video(message):
    url = message.text.strip()
    bot.reply_to(message, "📥 Videoyu indiriyorum, biraz bekle...")
    try:
        ydl_opts = {
            'outtmpl': 'video.mp4',
            'quiet': True,
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open("video.mp4", "rb") as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Hata oluştu: {e}")

print("🤖 Bot çalışıyor...")
bot.infinity_polling()

