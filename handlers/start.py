from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import users, settings_col
from utils.languages import tr

def register_handlers(bot):

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        try:
            bot.delete_message(message.message.chat.id, message.message.message_id)
        except Exception:
            pass
        user_id = message.from_user.id
        user = users.find_one({"userId": user_id})

        if not user:
            users.insert_one({
                "userId": user_id,
                "first_name": message.from_user.first_name,
                "username": message.from_user.username,
                "role": "user"
            })
        user = users.find_one({"userId": user_id})

        settings = settings_col.find_one()
        if settings and settings.get("force_subscription"):
            joined_all = True
            text = "🚫 Please join all channels to use the bot."
            markup = InlineKeyboardMarkup()
            for ch in settings.get("channels", []):
                markup.add(InlineKeyboardButton(ch["name"], url=ch["url"]))
            markup.add(InlineKeyboardButton("✅ Joined", callback_data="check_sub"))
            bot.send_message(user_id, text, reply_markup=markup)
            return
        show_main_menu(bot, user_id,user)
        # print(user)

    @bot.callback_query_handler(func=lambda call: call.data == "go_home")
    def go_home_callback(call):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        show_main_menu(bot, call.message.chat.id)


def show_main_menu(bot, chat_id, user=None):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Check Status", callback_data="check_status"),
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("🆘 Help", callback_data="help"),
    )
    markup.add(
        InlineKeyboardButton("🆕 New Passport Registration", callback_data="new_passport"),
        InlineKeyboardButton("♻️ Passport Renewal", callback_data="renew_passport")
    )
    if user and user.get("role") == "admin":
        markup.add(InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel"))

    bot.send_message(chat_id, f"""👋 Welcome to the Ethiopian Passport Status Bot!

🛂 You can check the status of your passport application using either:
✅ Your Tracking Code (Recommended)
🔍 Your Full Name and Branch (if you lost your code)
""", reply_markup=markup)
def get_main_menu_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="go_home"))
    return markup
