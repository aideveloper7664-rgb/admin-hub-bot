import os
import json
import telebot
from telebot import types

# ============================================================
# ✅ ENV VARIABLE SE TOKEN LE
# ============================================================
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable not set!")

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# ✅ TERI SETTINGS (YAHAN KUCH NAHI BADALNA)
# ============================================================
PUBLIC_CHANNEL = "@admsfss"
JOIN_LINK = "https://t.me/admsfss"
LOGIN_URL = "https://bejewelled-pudding-c5f589.netlify.app/"

# ============================================================
# FILES
# ============================================================
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.txt")

def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r+") as f:
        users = set(line.strip() for line in f if line.strip())
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

# ============================================================
# 📌 /start COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        full_name = message.from_user.first_name or "User"
        username = f"@{message.from_user.username}" if message.from_user.username else "N/A"

        save_user(user_id)
        data = load_data()
        if str(user_id) not in data:
            data[str(user_id)] = {"points": 0}
            save_data(data)

        # CHECK IF USER JOINED CHANNEL
        try:
            status = bot.get_chat_member(PUBLIC_CHANNEL, user_id).status
            if status in ["member", "administrator", "creator"]:
                show_main_menu(chat_id)
                return
        except:
            pass

        # SHOW JOIN BUTTON
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("🔓 JOIN CHANNEL", url=JOIN_LINK),
            types.InlineKeyboardButton("✅ I HAVE JOINED", callback_data="check_joined")
        )

        join_text = (
            f"👋 Welcome {full_name}!\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Username: {username}\n\n"
            f"⚠️ Please join our channel to continue.\n"
            f"🔗 Then click 'I HAVE JOINED'."
        )
        bot.send_message(chat_id, join_text, reply_markup=keyboard, parse_mode="Markdown")

    except Exception as e:
        print(f"[ERROR /start] {e}")
        bot.send_message(chat_id, "❌ Something went wrong. Please try again.")

# ============================================================
# ✅ JOIN CHECK BUTTON
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def check_joined(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id

        try:
            status = bot.get_chat_member(PUBLIC_CHANNEL, user_id).status
            if status not in ["member", "administrator", "creator"]:
                bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)
                return
        except:
            bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)
            return

        bot.delete_message(chat_id, call.message.message_id)
        show_main_menu(chat_id)
        bot.answer_callback_query(call.id, "✅ Verified! Loading menu...")

    except Exception as e:
        print(f"[ERROR check_joined] {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred. Try again.")

# ============================================================
# 🏠 MAIN MENU
# ============================================================
def show_main_menu(chat_id):
    try:
        login_link = f"{LOGIN_URL}?id={chat_id}"
        user = bot.get_chat(chat_id)
        full_name = user.first_name or "User"

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("🚀 OPEN AI HUB", url=login_link),
            types.InlineKeyboardButton("📢 SHARE BOT", url="https://t.me/share/url?url=https://t.me/YOUR_BOT_USERNAME")
        )

        msg = (
            f"✅ Welcome back, {full_name}!\n\n"
            f"🆔 Your Chat ID: `{chat_id}`\n\n"
            f"🔐 Click below to open the AI Hub panel.\n"
            f"🧠 Features: DeepSeek • ChatGPT • NanoBanana • QR\n\n"
            f"⚠️ Note: Your device info will be collected for verification."
        )
        bot.send_message(chat_id, msg, reply_markup=keyboard, parse_mode="Markdown")

    except Exception as e:
        print(f"[ERROR show_main_menu] {e}")
        bot.send_message(chat_id, "❌ Failed to show menu. Please try again.")

# ============================================================
# 📊 ADMIN COMMANDS
# ============================================================
@bot.message_handler(commands=['stats'])
def stats(message):
    if str(message.from_user.id) != "7770804901":
        bot.reply_to(message, "❌ You are not authorized.")
        return
    data = load_data()
    users = len(data)
    bot.reply_to(message, f"📊 <b>Stats</b>\n\nTotal Users: {users}", parse_mode="HTML")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) != "7770804901":
        bot.reply_to(message, "❌ You are not authorized.")
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "❌ Please provide a message to broadcast.")
        return
    data = load_data()
    count = 0
    for user_id in data.keys():
        try:
            bot.send_message(user_id, f"📢 <b>Announcement</b>\n\n{text}", parse_mode="HTML")
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ Broadcast sent to {count} users.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = (
        "🤖 <b>Available Commands</b>\n\n"
        "/start — Start the bot\n"
        "/stats — Total users (admin only)\n"
        "/broadcast [msg] — Send message to all (admin only)\n"
        "/help — Show this menu\n\n"
        "🔐 Join @admsfss to access AI Hub."
    )
    bot.reply_to(message, help_text, parse_mode="HTML")

# ============================================================
# ▶️ START BOT
# ============================================================
print("✅ Bot is running...")
init_data()
bot.infinity_polling()
