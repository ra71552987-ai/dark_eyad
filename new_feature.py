import requests

def ai_respond(bot, chat_id, user_text):
    try:
        # التحقق من وجود جملة "أريني ماعندك يابشر؟؟"
        if user_text.strip().lower() == "أريني ماعندك يابشر؟؟":
            commands_list = """
📜 *قائمة أوامر الذكاء الاصطناعي* :

• /start - بدء استخدام البوت
• أي رسالة عادية - سأجيب عليها بذكاء
• "أريني ماعندك يابشر؟؟" - لعرض هذه القائمة
• أسئلة الذكاء الاصطناعي - مثل:
  - "ما هو سر الكون؟"
  - "كيف أتعلم البرمجة؟"
  - "أخبرني نكتة"

😈 Worm GPT جاهز لخدمتك!
            """
            bot.send_message(chat_id, commands_list, parse_mode="Markdown")
            return

        response = requests.get(
            "https://dev-pycodz-blackbox.pantheonsite.io/DEvZ44d/DarkCode.php",
            params={"text": user_text}
        )

        if response.status_code == 200:
            reply = response.text
            bot.send_message(chat_id, f"😈 رد الذكاء الاصطناعي:\n{reply}")
        else:
            bot.send_message(chat_id, "❌ حدث خطأ في الاتصال بخدمة الذكاء الاصطناعي.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ خطأ أثناء المعالجة: {str(e)}")
