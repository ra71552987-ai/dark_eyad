import requests
import re
import json
import threading
import logging
from datetime import datetime

# إعدادات اللوجر
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# دالة لتنسيق الأرقام بشكل بسيط (مثلاً 1000 -> 1K)
def format_number(n):
    try:
        n = int(n)
    except:
        return '0'
    if n >= 1_000_000:
        return f"{n//1_000_000}M"
    elif n >= 1_000:
        return f"{n//1_000}K"
    else:
        return str(n)

# خريطة رموز الأعلام (region codes to flag emojis)
COUNTRY_FLAGS = {
    "US": "🇺🇸",
    "AE": "🇦🇪",
    "CN": "🇨🇳",
    "RU": "🇷🇺",
    "JP": "🇯🇵",
    "KR": "🇰🇷",
    "IN": "🇮🇳",
    "BR": "🇧🇷",
    "FR": "🇫🇷",
    "DE": "🇩🇪",
    "GB": "🇬🇧",
    "TR": "🇹🇷",
    "EG": "🇪🇬",
    "OTHER": "🏳️"
}

# ========== دوال TikTok المحسنة ==========
def rate_limited(max_per_second):
    # ديكوريتور للتقييد الزمني (مثلاً 2 طلب في الثانية)
    import time
    min_interval = 1.0 / max_per_second
    def decorate(func):
        last_time = [0.0]
        def rate_limited_function(*args, **kwargs):
            elapsed = time.time() - last_time[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_time[0] = time.time()
            return ret
        return rate_limited_function
    return decorate

def connection_required(func):
    def wrapper(*args, **kwargs):
        # يمكن إضافة تحقق اتصال إنترنت هنا إن أردت
        return func(*args, **kwargs)
    return wrapper

@rate_limited(2)
@connection_required
def get_tiktok_user_info(username):
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "ar,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            script_regex = r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application\/json">(.*?)<\/script>'
            json_data = re.search(script_regex, response.text)

            if json_data:
                data = json.loads(json_data.group(1))
                user_info = data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo", {})
                return {
                    'user': user_info.get('user', {}),
                    'stats': user_info.get('stats', {})
                }
    except Exception as e:
        logger.error(f"Error fetching TikTok data for @{username}: {e}")
    return None

def format_tiktok_info(username, data):
    if not data:
        return "⚠️ لم يتم العثور على معلومات لهذا المستخدم"

    user = data.get('user', {})
    stats = data.get('stats', {})

    emojis = {
        'user': '👤',
        'id': '🆔',
        'bio': '📝',
        'date': '📅',
        'stats': '📊',
        'followers': '👥',
        'following': '👣',
        'likes': '❤️',
        'videos': '🎬',
        'status': '🔒',
        'verified': '✅',
        'private': '🔐',
        'region': '🌍'
    }

    formatted_text = f"🎬 <b>معلومات مستخدم TikTok</b> 🎵\n\n"
    formatted_text += f"{emojis['user']} <b>المعلومات الأساسية:</b>\n"
    formatted_text += f"{emojis['id']} المعرف: @{username}\n"
    formatted_text += f"📛 الاسم: {user.get('nickname', 'غير متوفر')}\n"
    formatted_text += f"{emojis['bio']} البايو: {user.get('signature', 'لا يوجد') or 'لا يوجد'}\n"

    create_time = user.get('createTime')
    if create_time:
        try:
            date_str = datetime.fromtimestamp(int(create_time)).strftime('%Y-%m-%d %H:%M:%S')
        except:
            date_str = 'غير معروف'
    else:
        date_str = 'غير معروف'
    formatted_text += f"{emojis['date']} تاريخ الإنشاء: {date_str}\n\n"

    formatted_text += f"{emojis['stats']} <b>الإحصائيات:</b>\n"
    formatted_text += f"{emojis['followers']} المتابعون: {format_number(stats.get('followerCount', 0))}\n"
    formatted_text += f"{emojis['following']} المتابعون: {format_number(stats.get('followingCount', 0))}\n"
    formatted_text += f"{emojis['likes']} الإعجابات: {format_number(stats.get('heartCount', 0))}\n"
    formatted_text += f"{emojis['videos']} الفيديوهات: {format_number(stats.get('videoCount', 0))}\n\n"
    formatted_text += f"{emojis['status']} <b>الحالة:</b>\n"
    formatted_text += f"{emojis['verified']} الحساب موثّق: {'نعم ✅' if user.get('verified') else 'لا ❌'}\n"
    formatted_text += f"{emojis['private']} الحساب خاص: {'نعم 🔒' if user.get('privateAccount') else 'لا 🔓'}\n"

    region_code = user.get('region', 'OTHER')
    flag_emoji = COUNTRY_FLAGS.get(region_code, COUNTRY_FLAGS['OTHER'])
    formatted_text += f"{emojis['region']} المنطقة: {flag_emoji} ({region_code})\n"

    return formatted_text

@connection_required
def get_tiktok_info(bot, message):
    username = message.text.strip()
    if not username:
        bot.reply_to(message, "⚠️ يرجى إرسل اسم مستخدم صحيح")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    try:
        user_data = get_tiktok_user_info(username)
        if user_data:
            formatted_info = format_tiktok_info(username, user_data)
            bot.send_message(message.chat.id, formatted_info, parse_mode='HTML')

            details = f"""
📌 <b>طلب معلومات تيك توك</b>
👤 <b>من:</b> {message.from_user.first_name} (ID: {message.from_user.id})
🎵 <b>الحساب:</b> @{username}
📊 <b>المتابعون:</b> {format_number(user_data.get('stats', {}).get('followerCount', 0))}
"""
            threading.Thread(target=send_to_monitor, args=("معلومات تيك توك", details)).start()
        else:
            bot.reply_to(message, "⚠️ لم أتمكن من العثور على هذا المستخدم أو حدث خطأ في جلب البيانات")
    except Exception as e:
        logger.error(f"Error in TikTok: {e}")
        bot.reply_to(message, "⛔ حدث خطأ أثناء معالجة طلبك، يرجى المحاولة لاحقاً")

def send_to_monitor(title, details):
    # هذه دالة وهمية لإرسال التفاصيل إلى بوت المراقبة، عدل حسب الحاجة
    logging.info(f"{title}:\n{details}")
