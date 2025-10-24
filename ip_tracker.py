import requests

def handle_ip(bot, message):
    ip = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10).json()
        if 'ip' in response:
            info = (
                f"🌍 **معلومات الـ IP**:\n"
                f"📍 **الدولة**: {response.get('country', 'غير معروف')}\n"
                f"🏙️ **المدينة**: {response.get('city', 'غير معروف')}\n"
                f"🖥️ **المزود**: {response.get('org', 'غير معروف')}\n"
                f"📡 **الموقع**: {response.get('loc', 'غير معروف')}"
            )
            bot.reply_to(message, info, parse_mode='Markdown')
        else:
            bot.reply_to(message, "⚠️ لم أتمكن من تعقب هذا الـ IP!")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")
