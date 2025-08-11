# utils/decorators.py
from functools import wraps
from utils.database import users, settings_col
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_only(bot):
    def decorator(func):
        @wraps(func)
        def wrapper(call):
            user = users.find_one({"userId": call.from_user.id})
            if user and user.get("role") == "admin":
                return func(call)
            else:
                bot.answer_callback_query(call.id, "❌ You are not authorized.")
        return wrapper
    return decorator

def force_subscription_required(bot):
    def decorator(func):
        @wraps(func)
        def wrapper(message):
            settings = settings_col.find_one()
            if not settings or not settings.get("force_subscription"):
                return func(message)
            channels = settings.get("channels", [])
            user_id = message.from_user.id
            for ch in channels:
                try:
                    member = bot.get_chat_member(ch["name"], user_id)
                    if member.status in ['left', 'kicked']:
                        bot.send_message(user_id, f"🚫 Please join {ch['name']} to use the bot.")
                        return
                except Exception:
                    bot.send_message(user_id, f"🚫 Please join {ch['name']} to use the bot.")
                    return
            return func(message)
        return wrapper
    return decorator
