from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.start import get_main_menu_button
from utils.database import users
from utils.passport_api import check_by_reference, check_by_fullname

def register_handlers(bot):

    @bot.callback_query_handler(func=lambda c: c.data == "check_status")
    def handle_check_status(call):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        user = users.find_one({"userId": call.from_user.id})
        lang = user.get("language", "en")

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔢 Tracking Code", callback_data="track_code"),
            InlineKeyboardButton("🏢 Full Name + Branch", callback_data="track_name")
        )
        markup.add(InlineKeyboardButton("🏠 Home ", callback_data="go_home"))
        bot.send_message(call.message.chat.id, "🔢 Please send your tracking reference code:\n E.x AAL1234567", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data == "track_code")
    def get_ref_input(call):
        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        user = users.find_one({"userId": call.from_user.id})
        lang = user.get("language", "en")
        msg = bot.send_message(call.message.chat.id, "🔢 Please send your tracking reference code:")
        bot.register_next_step_handler(msg, process_tracking_code, lang)

    def process_tracking_code(msg, lang):
        ref = msg.text.strip()
        result = check_by_reference(ref, lang)
        print(result)
        bot.send_message(msg.chat.id, result,parse_mode="MarkdownV2", reply_markup=get_main_menu_button())

    @bot.callback_query_handler(func=lambda c: c.data == "track_name")
    def get_fullname_input(call):
        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        user = users.find_one({"userId": call.from_user.id})
        lang = user.get("language", "en")
        msg = bot.send_message(call.message.chat.id, "🧑‍🦱 Enter your full name (Name Father Grandfather):")
        bot.register_next_step_handler(msg, ask_branch, lang)

    def ask_branch(msg, lang):
        full_name = msg.text.strip()
        branches = [
            "ICS Saris Adey Abeba Branch", "ICS Adama Branch", "ICS Assosa Branch",
            "ICS Bahirdar Branch", "ICS Dessie Branch", "ICS Gambella Branch",
            "ICS Hawassa Branch", "ICS Hosana Branch", "ICS Jigjiga Branch",
            "ICS Jimma Branch", "ICS Semera Branch", "ICS Dire Dawa Branch",
            "ICS Mekelle Branch"
        ]
        markup = InlineKeyboardMarkup()
        for branch in branches:
            markup.add(InlineKeyboardButton(branch, callback_data=f"branch|{full_name}|{branch}"))
        bot.send_message(msg.chat.id, "🏢 Choose your ICS Branch:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("branch|"))
    def handle_branch_selection(call):
        _, full_name, branch = call.data.split("|", 2)
        user = users.find_one({"userId": call.from_user.id})
        lang = user.get("language", "en")
        result = check_by_fullname(full_name, branch, lang)
        bot.send_message(call.message.chat.id, result,parse_mode="MarkdownV2", reply_markup=get_main_menu_button())
