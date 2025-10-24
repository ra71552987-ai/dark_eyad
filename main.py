import os
import time
import threading
from datetime import datetime
import telebot
from telebot import types

import ip_tracker
import tiktok_downloader
import tiktok_info
import instagram_info
import new_feature

# --- تحميل التوكنات من ملفات txt ---
def read_token(filename):
    with open(filename, "r") as f:
        return f.read().strip()

TOKEN = read_token("token.txt")
MONITOR_BOT_TOKEN = read_token("monitor_token.txt")
MONITOR_CHAT_ID = "6709092382"

# --- إعداد البوتات ---
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
monitor_bot = telebot.TeleBot(MONITOR_BOT_TOKEN, parse_mode="HTML")

ADMIN_ID = 6709092382
user_state = {}

CHANNELS = ["@Syria_8_122", "@lego3X", "@lego0x"]

# --- نظام المراقبة ---
def send_to_monitor(action, details):
    try:
        text = f"""
<b>🔔 {action}</b>
<pre>{details}</pre>
⏱ <i>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</i>
"""
        monitor_bot.send_message(MONITOR_CHAT_ID, text)
    except Exception as e:
        print(f"Monitor Error: {e}")

# --- التحقق من الاشتراك ---
def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def send_subscription_check(chat_id):
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("✅ تحقّق", callback_data="check_subs"))
    bot.send_message(chat_id, "🔐 يجب الاشتراك في القنوات التالية لاستخدام البوت:", reply_markup=markup)

# --- أدوات الإدارة ---
def brod(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg = message.text
    with open("id.txt", "r") as file:
        users = file.readlines()
    success, failed = 0, 0
    for user in users:
        try:
            bot.send_message(user.strip(), msg)
            success += 1
        except:
            failed += 1
    bot.reply_to(message, f"✅ {success} نجاح / ❌ {failed} فشل")
    send_to_monitor("📢 إرسال إذاعة", f"👤 {message.from_user.first_name}\n📊 {success} نجاح, {failed} فشل")

def ban_user(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    user_id = message.text.strip()
    if not user_id.isdigit():
        bot.reply_to(message, "⚠️ يرجى إدخال أيدي صحيح")
        return
    with open("ban.txt", "a") as f:
        f.write(f"{user_id}\n")
    try:
        bot.send_message(user_id, "⛔ تم حظرك")
    except: pass
    bot.reply_to(message, f"✅ تم حظر المستخدم {user_id}")
    send_to_monitor("⛔ حظر مستخدم", f"🆔 {user_id}")

def unban_user(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    user_id = message.text.strip()
    if not user_id.isdigit():
        bot.reply_to(message, "⚠️ يرجى إدخال أيدي صحيح")
        return
    with open("ban.txt", "r") as f:
        banned = f.readlines()
    if f"{user_id}\n" in banned:
        banned.remove(f"{user_id}\n")
        with open("ban.txt", "w") as f:
            f.writelines(banned)
        try:
            bot.send_message(user_id, "✅ تم إلغاء حظرك")
        except: pass
        bot.reply_to(message, f"✅ تم إلغاء حظر {user_id}")
        send_to_monitor("✅ إلغاء حظر", f"🆔 {user_id}")
    else:
        bot.reply_to(message, "⚠️ المستخدم غير محظور")

def show_stats(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    users = len(open("id.txt").readlines())
    banned = len(open("ban.txt").readlines())
    msg = f"""
📊 <b>إحصائيات البوت</b>
👥 المستخدمين: {users}
🚫 المحظورين: {banned}
🕒 الوقت: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    bot.reply_to(message, msg)
    send_to_monitor("📊 عرض إحصائيات", f"👤 {message.from_user.first_name}")

def check_bot_status(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg = f"""
⚙️ <b>حالة البوت</b>
🧵 الخيوط النشطة: {threading.active_count()}
🕒 الوقت الحالي: {time.ctime()}
"""
    bot.reply_to(message, msg)

# --- /start ---
@bot.message_handler(commands=['start'], chat_types=['private'])
def send_welcome(message):
    user_id = message.from_user.id

    if str(user_id) + "\n" in open("ban.txt").readlines():
        bot.reply_to(message, "⛔ أنت محظور من استخدام البوت")
        return

    if not is_subscribed(user_id):
        send_subscription_check(user_id)
        return

    with open("id.txt", "a+") as f:
        f.seek(0)
        if f"{user_id}\n" not in f.readlines():
            f.write(f"{user_id}\n")
            send_to_monitor("🚀 مستخدم جديد", f"🆔 {user_id} | 👤 {message.from_user.first_name}")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📍 تتبع IP", callback_data="track_ip"),
        types.InlineKeyboardButton("🎬 تحميل TikTok", callback_data="download_tiktok"),
        types.InlineKeyboardButton("🔍 جمع معلومات TikTok", callback_data="info_tiktok"),
        types.InlineKeyboardButton("📸 جمع معلومات إنستغرام", callback_data="info_instagram"),
        types.InlineKeyboardButton("🤖 ذكاء اصطناعي", callback_data="ai")
    )
    if str(user_id) == str(ADMIN_ID):
        markup.add(
            types.InlineKeyboardButton("📢 إذاعة", callback_data="brod"),
            types.InlineKeyboardButton("📊 إحصائيات", callback_data="info"),
            types.InlineKeyboardButton("🚫 حظر", callback_data="ban"),
            types.InlineKeyboardButton("✅ إلغاء الحظر", callback_data="unban"),
            types.InlineKeyboardButton("⚙️ فحص البوت", callback_data="check_bot")
        )

    bot.send_message(user_id, "مرحباً بك! اختر الميزة:", reply_markup=markup)

# --- الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if not is_subscribed(user_id):
        send_subscription_check(call.message.chat.id)
        return

    if data == "track_ip":
        user_state[call.message.chat.id] = "ip"
        bot.send_message(call.message.chat.id, "أرسل عنوان IP:")
        send_to_monitor("🛰 طلب تتبع IP", f"🆔 {user_id}")
    elif data == "download_tiktok":
        user_state[call.message.chat.id] = "tiktok"
        bot.send_message(call.message.chat.id, "أرسل رابط فيديو TikTok:")
        send_to_monitor("📥 تحميل TikTok", f"🆔 {user_id}")
    elif data == "info_tiktok":
        user_state[call.message.chat.id] = "info_tiktok"
        bot.send_message(call.message.chat.id, "أرسل اسم مستخدم TikTok:")
        send_to_monitor("🔍 جمع معلومات TikTok", f"🆔 {user_id}")
    elif data == "info_instagram":
        user_state[call.message.chat.id] = "info_instagram"
        bot.send_message(call.message.chat.id, "أرسل اسم مستخدم إنستغرام:")
        send_to_monitor("📸 جمع معلومات Instagram", f"🆔 {user_id}")
    elif data == "ai":
        user_state[call.message.chat.id] = "ai"
        bot.send_message(call.message.chat.id, "🧠 أرسل سؤالك للذكاء الاصطناعي:")
        send_to_monitor("🤖 ذكاء اصطناعي", f"🆔 {user_id}")
    elif data == "check_subs":
        if is_subscribed(user_id):
            bot.send_message(call.message.chat.id, "✅ تم التحقق! يمكنك الآن استخدام البوت.")
            send_welcome(call.message)
        else:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على اشتراكك بجميع القنوات.")
    elif data == "brod" and str(user_id) == str(ADMIN_ID):
        msg = bot.send_message(call.message.chat.id, "✉️ أرسل رسالة الإذاعة:")
        bot.register_next_step_handler(msg, brod)
    elif data == "info" and str(user_id) == str(ADMIN_ID):
        show_stats(call.message)
    elif data == "ban" and str(user_id) == str(ADMIN_ID):
        msg = bot.send_message(call.message.chat.id, "🚫 أرسل أيدي المستخدم:")
        bot.register_next_step_handler(msg, ban_user)
    elif data == "unban" and str(user_id) == str(ADMIN_ID):
        msg = bot.send_message(call.message.chat.id, "✅ أرسل أيدي المستخدم:")
        bot.register_next_step_handler(msg, unban_user)
    elif data == "check_bot" and str(user_id) == str(ADMIN_ID):
        check_bot_status(call.message)

# --- الرسائل في المحادثات الخاصة فقط ---
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_message(message):
    state = user_state.get(message.chat.id)
    
    if not is_subscribed(message.from_user.id):
        send_subscription_check(message.chat.id)
        return

    send_to_monitor("💬 رسالة خاصة", f"🆔 {message.from_user.id} | 👤 {message.from_user.first_name}\n✉️ {message.text}")

    if state == "ip":
        ip_tracker.handle_ip(bot, message)
    elif state == "tiktok":
        tiktok_downloader.handle_tiktok(bot, message)
    elif state == "info_tiktok":
        tiktok_info.get_tiktok_info(bot, message)
    elif state == "info_instagram":
        instagram_info.get_instagram_info(bot, message)
    elif state == "ai":
        new_feature.ai_respond(bot, message.chat.id, message.text)
    else:
        bot.reply_to(message, "يرجى اختيار ميزة من /start أولاً.")

# --- التعامل مع المجموعات ---
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_message(message):
    # الرد فقط إذا تم ذكر البوت
    if f"@{bot.get_me().username}" in message.text:
        bot.reply_to(message, "مرحبًا! للاستخدام يرجى مراسلتي في الخاص @{}".format(bot.get_me().username))

if __name__ == "__main__":
    print("✅ البوت يعمل الآن...")
    send_to_monitor("✅ تم تشغيل البوت", "البوت الآن يعمل ويستقبل الأوامر")
    bot.infinity_polling()