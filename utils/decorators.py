# utils/decorators.py
from functools import wraps
from utils.database import users, settings_col
from telebot.apihelper import ApiTelegramException
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
                    # Prefer stored chat_id
                    chat_identifier = ch.get("chat_id")
                    if not chat_identifier:
                        # Expect admins to store channels as @username in the `url` field
                        url = ch.get("url", "")
                        if url.startswith("@"):
                            chat_identifier = url
                        elif url.startswith("https://t.me/") or url.startswith("http://t.me/"):
                            username = url.rstrip('/').split('/')[-1]
                            chat_identifier = f"@{username}"
                        else:
                            # fallback to name (will likely fail)
                            chat_identifier = ch.get("name")

                    member = bot.get_chat_member(chat_identifier, user_id)
                    if member.status in ['left', 'kicked']:
                        bot.send_message(user_id, f"🚫 Please join {ch.get('name')} to use the bot.")
                        return
                except ApiTelegramException:
                    # Bot cannot check membership (chat not found or bot lacks access)
                    bot.send_message(user_id, f"🚫 Please join {ch.get('name')} to use the bot. If this persists, ask an admin to ensure the bot is added to the channel.")
                    return
                except Exception:
                    bot.send_message(user_id, f"🚫 Please join {ch.get('name')} to use the bot.")
                    return
            return func(message)
        return wrapper
    return decorator
