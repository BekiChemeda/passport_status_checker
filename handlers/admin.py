# handlers/admin.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.start import show_main_menu
from utils.database import users, settings_col
from utils.decorators import admin_only

def register_handlers(bot):
    @bot.message_handler(commands=["channels"])
    def handle_channels_command(message):
        user = users.find_one({"userId": message.from_user.id})
        if not user or user.get("role") != "admin":
            return bot.reply_to(message, "⛔️ You are not authorized to use this command.")

        settings = settings_col.find_one({"_id": "global_settings"}) or {}
        channels = settings.get("channels", [])

        text = "📢 Current Subscription Channels:\n\n"
        for i, ch in enumerate(channels):
            text += f"{i + 1}. [{ch['name']}]({ch['url']})\n"

        markup = InlineKeyboardMarkup()
        for i, ch in enumerate(channels):
            markup.add(
                InlineKeyboardButton(f"❌ Remove {ch['name']}", callback_data=f"remove_channel_{i}")
            )
        markup.add(
            InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")
        )

        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("remove_channel_"))
    def remove_channel_callback(call):
        index = int(call.data.split("_")[-1])
        settings = settings_col.find_one({"_id": "global_settings"}) or {}
        channels = settings.get("channels", [])

        if index < len(channels):
            removed = channels.pop(index)
            settings_col.update_one(
                {"_id": "global_settings"},
                {"$set": {"channels": channels}}
            )
            bot.answer_callback_query(call.id, f"Removed: {removed['name']}")
        else:
            bot.answer_callback_query(call.id, "Invalid index.")

        # Refresh the channel list
        bot.delete_message(call.message.chat.id, call.message.message_id)
        handle_channels_command(call.message)

    @bot.callback_query_handler(func=lambda call: call.data == "add_channel")
    def prompt_add_channel(call):
        try:
            # Delete the home message with the buttons
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass  # Ignore if message already deleted or can't delete
        msg = bot.send_message(call.message.chat.id,
                               "📝 Send the channel in this format:\n`name - https://t.me/yourchannel`",
                               parse_mode="Markdown")
        bot.register_next_step_handler(msg, add_channel_step)

    def add_channel_step(message):
        if "-" not in message.text:
            return bot.reply_to(message, "❗ Invalid format. Use: `ChannelName - https://t.me/yourchannel`",
                                parse_mode="Markdown")

        try:
            name, url = [x.strip() for x in message.text.split("-", 1)]
            settings = settings_col.find_one({"_id": "global_settings"}) or {}
            channels = settings.get("channels", [])
            channels.append({"name": name, "url": url})

            settings_col.update_one(
                {"_id": "global_settings"},
                {"$set": {"channels": channels}},
                upsert=True
            )
            bot.reply_to(message, f"✅ Added channel: {name}")
        except Exception as e:
            bot.reply_to(message, f"❌ Failed to add channel. Error: {e}")
    @bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
    @admin_only(bot)
    def admin_panel(call):
        try:
            # Delete the home message with the buttons
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass  # Ignore if message already deleted or can't delete
        users_count = users.count_documents({})
        admins_count = users.count_documents({"role": "admin"})
        lang_counts = {
            "en": users.count_documents({"language": "en"}),
            "am": users.count_documents({"language": "am"}),
            "om": users.count_documents({"language": "om"})
        }

        text = (
            f"📊 Total users: {users_count}\n"
            f"👑 Admins: {admins_count}\n"
            f"🌍 English: {lang_counts['en']}\n"
            f"🇪🇹 Amharic: {lang_counts['am']}\n"
            f"🟩 Afaan Oromoo: {lang_counts['om']}\n\n"
            "🔧 Settings:\n"
            "\n \n /channels - to add or remove channel"
        )

        settings = settings_col.find_one()
        force_sub = settings.get("force_subscription", False) if settings else False

        markup = InlineKeyboardMarkup()
        force_btn_text = "Disable Force Subscription" if force_sub else "Enable Force Subscription"
        markup.add(InlineKeyboardButton(force_btn_text, callback_data="toggle_force_sub"))
        markup.add(InlineKeyboardButton("Close", callback_data="close_admin"))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=markup)

    @bot.callback_query_handler(func=lambda c: c.data == "toggle_force_sub")
    @admin_only(bot)
    def toggle_force_subscription(call):
        settings = settings_col.find_one() or {}
        force_sub = settings.get("force_subscription", False)
        settings_col.update_one({}, {"$set": {"force_subscription": not force_sub}}, upsert=True)
        bot.answer_callback_query(call.id, "✅ Force subscription toggled.")
        admin_panel(call)

    @bot.callback_query_handler(func=lambda c: c.data == "close_admin")
    @admin_only(bot)
    def close_admin_panel(call):
        try:
            # Delete the home message with the buttons
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass  # Ignore if message already deleted or can't delete
        show_main_menu(bot,call.message.chat.id)
