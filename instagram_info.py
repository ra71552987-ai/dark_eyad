import instaloader
from telebot import TeleBot

def get_instagram_info(bot: TeleBot, message):
    username = message.text.strip()
    L = instaloader.Instaloader()
    
    try:
        profile = instaloader.Profile.from_username(L.context, username)

        msg = f"""
⌯ ✅ معلومات الإنستغرام:
[💙] اسم المستخدم: {profile.username}
[👤] الاسم الكامل: {profile.full_name}
[📝] السيرة الذاتية: {profile.biography}
[👥] عدد المتابعين: {profile.followers}
[🗣] عدد الذين تتابعهم: {profile.followees}
[💞] عدد المنشورات: {profile.mediacount}
[🔗] الرابط الخارجي: {profile.external_url if profile.external_url else 'لا يوجد'}
"""
        bot.send_message(message.chat.id, msg, parse_mode='HTML')

    except instaloader.exceptions.ProfileNotExistsException:
        bot.send_message(message.chat.id, "⚠️ الحساب غير موجود.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ حدث خطأ أثناء جلب معلومات الإنستغرام:\n{str(e)}")