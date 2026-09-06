import os
import re
import time
import telebot

# --- CONFIGURATION ---
# Replit / Koyeb / Render ke Environment Variables (Secrets) se Token read karega
BOT_TOKEN = os.environ.get("8973023915:AAF-oHw-Tl-3wn8JPfZxJjk2CVS3GJLGgKQ")

# Yahan apna Telegram Channel Username daalein (e.g. "@my_deals_channel")
CHANNEL_ID = "@99/- mesho deals" 

if not BOT_TOKEN:
    print("❌ Error: 'BOT_TOKEN' environment variable nahi mila!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# URL Extract karne ke liye helper function
def extract_urls(text):
    if not text:
        return []
    # Regex pattern to match all HTTP/HTTPS links
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)

# 1. PHOTO + CAPTION HANDLER (Affiliate Links + Product Image)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        photo_id = message.photo[-1].file_id
        caption = message.caption if message.caption else ""
        links = extract_urls(caption)
        
        # Link nikaal kar layout banana
        link_text = links[0] if links else "Link unavailable"
        
        # Post Template
        post = f"""🔥 **LOOT DEAL / TRENDING PRODUCT** 🔥

🛒 **Buy Now / Claim Offer:**
👉 {link_text}

━━━━━━━━━━━━━━━━━━━━━
📢 Join Channel: {CHANNEL_ID}"""

        # Channel par send karein
        bot.send_photo(CHANNEL_ID, photo=photo_id, caption=post, parse_mode="Markdown")
        bot.reply_to(message, "✅ **Photo Deal successfully channel par post ho gayi!**")
        
    except Exception as e:
        # Fallback agar Markdown parse error aaye
        try:
            bot.send_photo(CHANNEL_ID, photo=photo_id, caption=post)
            bot.reply_to(message, "✅ **Photo Deal posted (Plain Text Mode).**")
        except Exception as err:
            bot.reply_to(message, f"❌ **Error:** {str(err)}")

# 2. TEXT MESSAGE HANDLER (Multiple Affiliate Links / Deals)
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Ignore commands like /start
    if message.text.startswith('/'):
        if message.text == '/start':
            bot.reply_to(message, "👋 Welcome! Mujhe koi bhi Deal Link ya Photo bhejien, main use formatted way mein aapke channel par post kar doonga.")
        return

    links = extract_urls(message.text)
    
    if not links:
        bot.reply_to(message, "⚠️ **Kripya koi Affiliate/Product Link wala message bhejein!**")
        return

    successful_posts = 0
    for link in links:
        post = f"""🔥 **HOT DEAL FOUND** 🔥

🛒 **Buy Link:**
👉 {link}

━━━━━━━━━━━━━━━━━━━━━
📢 Join Channel: {CHANNEL_ID}"""

        try:
            bot.send_message(CHANNEL_ID, post, parse_mode="Markdown")
            successful_posts += 1
            time.sleep(1) # Telegram rate limiting / Anti-Spam delay
        except Exception as e:
            # Markdown failure backup
            try:
                bot.send_message(CHANNEL_ID, post)
                successful_posts += 1
            except Exception as err:
                print(f"Error posting link {link}: {err}")
            
    bot.reply_to(message, f"✅ **Total {successful_posts} deal(s) channel par post ho chuki hain!**")

# 3. BOT POLLING & RESTART LOOP
if __name__ == '__main__':
    print("🚀 Bot start ho gaya hai...")
    while True:
        try:
            bot.polling(non_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"⚠️ Bot network error: {e}. 5 seconds mein auto-retry ho raha hai...")
            time.sleep(5)
