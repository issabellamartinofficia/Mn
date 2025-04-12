import telebot, json
from telebot.types import Message
from vps_handler import add_vps, remove_vps, run_task, get_vps_status

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)
with open("config.json") as f:
    config = json.load(f)
ADMINS = config["admins"]

# Load approved users
def load_users():
    try:
        with open("approved.json") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("approved.json", "w") as f:
        json.dump(data, f)

SESSION = load_users()

@bot.message_handler(commands=['start'])
def start(msg: Message):
    uid = str(msg.from_user.id)
    if uid in SESSION:
        return send_welcome(msg, SESSION[uid])
    for admin in ADMINS:
        bot.send_message(admin, f"🆕 Access request from {msg.from_user.first_name} ({uid})\n✅ /approve {uid}\n❌ /deny {uid}")
    bot.reply_to(msg, "⏳ Waiting for admin approval...")

def send_welcome(msg, role):
    text = f"""
👋 Welcome to Mitra Drift Shell

You are: {'🛡️ ADMIN' if role == 'admin' else '🟢 MEMBER'}

📘 Commands:
/imgb <ip> <port> <time>
/status
{"/addvps <ip> <user> <pass>\n/removevps <ip>\n/approve <id>\n/deny <id>" if role == "admin" else ""}
"""
    bot.reply_to(msg, text)

@bot.message_handler(commands=['approve'])
def approve(msg: Message):
    if str(msg.from_user.id) not in ADMINS:
        return
    try:
        uid = msg.text.split()[1]
        SESSION[uid] = 'member'
        save_users(SESSION)
        bot.send_message(uid, "✅ Access Approved! Use /help to begin.")
        bot.reply_to(msg, f"✅ Approved {uid}")
    except:
        bot.reply_to(msg, "Usage: /approve <user_id>")

@bot.message_handler(commands=['deny'])
def deny(msg: Message):
    if str(msg.from_user.id) not in ADMINS:
        return
    try:
        uid = msg.text.split()[1]
        bot.send_message(uid, "❌ Access denied by admin.")
        bot.reply_to(msg, f"Denied {uid}")
    except:
        bot.reply_to(msg, "Usage: /deny <user_id>")

@bot.message_handler(commands=['help'])
def help_cmd(msg: Message):
    uid = str(msg.from_user.id)
    role = SESSION.get(uid)
    if not role:
        return bot.reply_to(msg, "⛔ Wait for approval.")
    cmds = ["/imgb <ip> <port> <time>", "/status"]
    if role == "admin":
        cmds += ["/addvps <ip> <user> <pass>", "/removevps <ip>", "/approve <id>", "/deny <id>"]
    bot.reply_to(msg, "📘 Commands:\n" + "\n".join(cmds))

@bot.message_handler(commands=['addvps'])
def addvps_cmd(msg: Message):
    if SESSION.get(str(msg.from_user.id)) != "admin":
        return
    args = msg.text.split()
    if len(args) != 4:
        return bot.reply_to(msg, "Usage: /addvps <ip> <user> <pass>")
    ip, user, pw = args[1:]
    add_vps(ip, user, pw)
    bot.reply_to(msg, f"✅ VPS {ip} added.")

@bot.message_handler(commands=['removevps'])
def removevps_cmd(msg: Message):
    if SESSION.get(str(msg.from_user.id)) != "admin":
        return
    args = msg.text.split()
    if len(args) != 2:
        return bot.reply_to(msg, "Usage: /removevps <ip>")
    remove_vps(args[1])
    bot.reply_to(msg, f"🗑️ VPS {args[1]} removed.")

@bot.message_handler(commands=['status'])
def status_cmd(msg: Message):
    if str(msg.from_user.id) not in SESSION:
        return
    bot.reply_to(msg, get_vps_status())

@bot.message_handler(commands=['imgb'])
def imgb_cmd(msg: Message):
    if str(msg.from_user.id) not in SESSION:
        return
    args = msg.text.split()
    if len(args) != 4:
        return bot.reply_to(msg, "Usage: /imgb <ip> <port> <time>")
    ip, port, dur = args[1:]
    count = run_task(ip, port, dur)
    bot.reply_to(msg, f"🚀 Task started on {count} VPS.")

# ✅ Infinite Polling
print("🤖 Bot is running...")
bot.infinity_polling(timeout=60, long_polling_timeout=30)
