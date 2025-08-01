import telebot
import os
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers import start, check_status, admin
from utils.database import users_col

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
lang = "en"
start.register_handlers(bot)
check_status.register_handlers(bot)
admin.register_handlers(bot)




@bot.callback_query_handler(func=lambda call: call.data in ["new_passport", "renew_passport"])
def passport_service_info(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    text = (
        "📌 *Service Information*\n\n"
        "Currently, this bot *does not* support new passport registration, renewal, or personal detail corrections *directly*.\n\n"
        "However, we do offer these services through Telegram with a fast and competitive process!\n\n"
        "📨 Contact [Passport Checker](https://t.me/et_passport_status_checker_bot) for:\n"
        "• 🆕 New Passport Applications\n"
        "• ♻️ Passport Renewals\n"
        "• 🧾 Corrections & Urgent Handling"
    )
    from handlers.start import get_main_menu_button
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu_button())
@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_inline(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    text = (
        "🧾 *How to Check Your Passport Status*\n\n"
        "➤ *Method 1: By Tracking Code*\n"
        "Example: `AAL1234567`\n"
        "press *Check Status* → *Tracking Code* → Paste your code.\n\n"
        "➤ *Method 2: By Full Name + Branch*\n"
        "Example:\n"
        "`Full Name:` ABEBE KEBEDE HAILE\n"
        "`Branch:` ICS Saris Adey Abeba Branch\n"
        "Follow: *Check Status* → *Full Name Method* → Enter name and select branch.\n\n"
        "For any issues, contact [@BrightCodesSupport](https://t.me/BrightCodesSupport)"
    )
    from handlers.start import get_main_menu_button
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu_button())
@bot.callback_query_handler(func=lambda call: call.data == "about")
def about_handler(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    about_text = (
         "📢 *About Passport Status Checker Bot*\n\n"
    "This bot helps you *quickly check the status* of your Ethiopian passport application.\n\n"
    "You can check your status by:\n"
    "• Using your *Tracking Code* (recommended method)\n"
    "• Providing your *Full Name* along with your *Pickup Branch*\n\n"
    "Just enter your tracking code or full name with branch, and get instant updates!\n\n"
    "⚠️ Please note: This bot *does NOT* handle new passport registrations, renewals, or personal information changes.\n"
    "For those services, please contact the official support channels.\n\n"
    "📨 For assistance, contact [Passport Checker Support](https://t.me/et_passport_status_checker_bot)"
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Back to Home", callback_data="go_home"))

    bot.send_message(call.message.chat.id, about_text, parse_mode="Markdown", reply_markup=markup)
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST', 'HEAD'])
def webhook():
    if request.method == 'HEAD':
        return '', 200

    if request.method == 'GET':
        return '✅ Passport Bot is Running!', 200

    if request.method == 'POST':
        try:
            json_str = request.get_data().decode('utf-8')
            print(f"📩 Incoming POST update:\n{json_str}")  # Show the raw update

            update = telebot.types.Update.de_json(json_str)
            bot.process_new_updates([update])
            print("✅ Update processed successfully")
            return 'OK', 200
        except Exception as e:
            print(f"❌ Error processing update: {e}")
            return 'Internal Server Error', 500

if __name__ == "__main__":
    
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}/")
    print("Webhook set. Flask server running...")
    app.run(host="0.0.0.0", port=10000)
# bot.infinity_polling()
# print("bot is running...")
