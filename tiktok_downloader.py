import requests

def handle_tiktok(bot, message):
    url = message.text.strip()
    bot.send_chat_action(message.chat.id, 'upload_video')

    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=10).json()

        if response.get('data') and response['data'].get('play'):
            video_url = response['data']['play']
            caption = response['data'].get('title', '🎬 فيديو تيك توك')

            video_data = requests.get(video_url, timeout=30).content

            bot.send_video(
                message.chat.id,
                video_data,
                caption=caption,
                supports_streaming=True
            )

            # إرسال لوج للمراقبة (اختياري)
            try:
                bot.send_message(
                    6634366422,  # غيّره إلى Chat ID المراقبة
                    f"📥 <b>تحميل فيديو تيك توك</b>\n"
                    f"👤 المستخدم: @{message.from_user.username or 'غير معروف'}\n"
                    f"🆔 ID: <code>{message.from_user.id}</code>\n"
                    f"🔗 الرابط: {url}",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        else:
            bot.reply_to(message, "⚠️ لم أتمكن من تحميل الفيديو. تأكد من صحة الرابط.")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء التحميل:\n<code>{str(e)}</code>", parse_mode="HTML")
