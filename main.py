import telebot
import subprocess
import os

# Telegram bot token (Render Environment Variables kısmına BOT_TOKEN olarak ekle)
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# cookies.txt yolu (Secret Files kısmına cookies.txt olarak ekledin zaten)
COOKIES_PATH = "/etc/secrets/cookies.txt"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
        # Dosya ismini dinamik oluştur
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--cookiefile", COOKIES_PATH,
            "-o", output_template,
            url
        ]
        subprocess.run(cmd, check=True)

        # En son indirilen dosyayı bul
        files = sorted(os.listdir(DOWNLOAD_DIR), key=lambda x: os.path.getctime(os.path.join(DOWNLOAD_DIR, x)), reverse=True)
        latest_file = os.path.join(DOWNLOAD_DIR, files[0])

        # Dosya boyutu kontrolü (Telegram sınırı 50 MB)
        if os.path.getsize(latest_file) > 50 * 1024 * 1024:
            bot.reply_to(message, "⚠️ Moruk dosya 50 MB’tan büyük, Telegram izin vermiyor.")
        else:
            with open(latest_file, "rb") as video:
                bot.send_video(message.chat.id, video)
        # Temizlik
        os.remove(latest_file)

    except subprocess.CalledProcessError:
        bot.reply_to(message, "🚫 Hata oluştu moruk, linki kontrol et.")
    except Exception as e:
        bot.reply_to(message, f"❌ Bi’ şey ters gitti: {str(e)}")

bot.polling(non_stop=True)
