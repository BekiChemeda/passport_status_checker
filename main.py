import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import users, settings_col
from utils.decorators import admin_only
from utils.passport_api import check_by_reference, check_by_fullname
from dotenv import load_dotenv
import logging
import traceback
from threading import Thread
from time import sleep
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
bot = telebot.TeleBot(BOT_TOKEN)
lang = "en"



# Logging  Configurations
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),  # log to file
        logging.StreamHandler()  # also print to console
    ]
)



# app = Flask(__name__)
admin_states = {}
def clear_user_session(userId):
    admin_states.pop(userId, None)
    
def is_admin(userId):
    try:
        user = users.find_one({"userId": userId})
        return user and user.get("role") == "admin"
    except Exception as e:
        log_exception(e)
        return False
def log_exception(e):
    logging.error("Exception: %s\n%s", str(e), traceback.format_exc())  


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

    userId = message.from_user.id
    user = users.find_one({"userId": userId})

    if not user:
        users.insert_one({
            "userId": userId,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "role": "user"
        })
    user = users.find_one({"userId": userId})

    settings = settings_col.find_one()
    if settings and settings.get("force_subscription"):
        channels = settings.get("channels", [])
        if not channels:
            show_main_menu(bot, userId, user)
            return

        # Determine which channels the user hasn't joined and show only those
        missing = []
        for ch in channels:
            try:
                chat_identifier = ch.get("chat_id")
                if not chat_identifier:
                    url = ch.get("url", "")
                    if url.startswith("@"):
                        chat_identifier = url
                    elif url.startswith("https://t.me/") or url.startswith("http://t.me/"):
                        username = url.rstrip('/').split('/')[-1]
                        chat_identifier = f"@{username}"
                    else:
                        chat_identifier = ch.get("name")

                # convert numeric strings
                if isinstance(chat_identifier, str) and chat_identifier.lstrip('-').isdigit():
                    try:
                        chat_identifier = int(chat_identifier)
                    except Exception:
                        pass

                member = bot.get_chat_member(chat_identifier, userId)
                if member.status not in ["member", "administrator", "creator"]:
                    missing.append(ch)
            except telebot.apihelper.ApiTelegramException as e:
                # if bot can't access the channel, treat as missing (user must join / admin should fix)
                missing.append(ch)
            except Exception:
                missing.append(ch)

        if not missing:
            show_main_menu(bot, userId, user)
            return

        text = "🚫 Please join the channels below to use the bot."
        markup = InlineKeyboardMarkup()
        for ch in missing:
            url = ch.get("url")
            if url:
                if url.startswith("@"):
                    link = f"https://t.me/{url.lstrip('@')}"
                elif url.startswith("http"):
                    link = url
                else:
                    link = None
                if link:
                    markup.add(InlineKeyboardButton(ch["name"], url=link))
        markup.add(InlineKeyboardButton("✅ Joined", callback_data="check_sub"))
        bot.send_message(userId, text, reply_markup=markup)
        return

    show_main_menu(bot, userId, user)
    # print(user)


@bot.callback_query_handler(func=lambda call: call.data == "go_home")
def go_home_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    user = users.find_one({"userId": call.from_user.id})
    show_main_menu(bot, call.message.chat.id, user)


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
        "📨 Contact [Passport Checker](https://t.me/ICSEthiopia_0) for:\n"
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
        "For any issues, contact [@BEK_I](https://t.me/BEK_I)"
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
    "📨 For assistance, contact [Passport Checker Support](https://t.me/ICSEthiopia_0)"
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Back to Home", callback_data="go_home"))

    bot.send_message(call.message.chat.id, about_text, parse_mode="Markdown", reply_markup=markup)

def show_main_menu(bot, chat_id, user=None):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Check Passport Status", callback_data="check_status"),
        InlineKeyboardButton("ℹ️ About the Bot", callback_data="about")
    )
    markup.add(
        InlineKeyboardButton("🆘 Help & Instructions", callback_data="help"),
        InlineKeyboardButton("👨‍💻 Developer Info", url="https://t.me/BEK_I")
    )
    markup.add(
        InlineKeyboardButton("🆕 New Passport Registration", callback_data="new_passport"),
        InlineKeyboardButton("♻️ Renew Passport", callback_data="renew_passport")
    )
    if user and user.get("role") == "admin":
        markup.add(InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel"))

    welcome_text = (
        "👋 *Welcome to the Ethiopian Passport Status Bot!*\n\n"
        "🛂 *Easily check the status of your passport application:*\n\n"
        "✅ *Tracking Code Method:* Recommended for quick results.\n"
        "🔍 *Full Name + Branch:* Use if you lost your tracking code.\n\n"
        "📢 *Stay updated and enjoy our services!*"
    )

    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)
def get_main_menu_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="go_home"))
    return markup
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
        bot.send_message(call.message.chat.id, "Please select a method you want to check with: \n \n \n 👉Tracking code (Recomended) \n 👉Fullname + Branch - If you don't remember your tracking code.", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "track_code")
def get_ref_input(call):
        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        user = users.find_one({"userId": call.from_user.id})
        lang = user.get("language", "en")
        msg = bot.send_message(call.message.chat.id, "🔢 Please send your tracking reference code:\n E.x AAL1234567 ")
        bot.register_next_step_handler(msg, process_tracking_code, lang)

def process_tracking_code(msg, lang):
        ref = msg.text.strip()
        result = check_by_reference(ref, lang)
        # print(result)
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
    try:
        input_text = message.text.strip()
        if "-" not in input_text:
            return bot.reply_to(message, "❗ Invalid format. Use: `ChannelName - @username`", parse_mode="Markdown")

        name, identifier = [x.strip() for x in input_text.split("-", 1)]

        # Normalize and require @username (admins will add channels using @username)
        if identifier.startswith("@"):
            username = identifier
        elif "t.me" in identifier:
            username = "@" + identifier.rstrip('/').split('/')[-1]
        else:
            return bot.reply_to(message, "❗ Invalid identifier. Provide a public @username or https://t.me/username", parse_mode="Markdown")

        # Verify bot can access the channel using @username
        try:
            bot.get_chat(username)
        except telebot.apihelper.ApiTelegramException as e:
            # common cause: bot not added or wrong username
            if "chat not found" in str(e).lower() or (hasattr(e, 'description') and e.description == "Bad Request: chat not found"):
                return bot.reply_to(message, "❌ Failed to verify channel access. Ensure the bot is added to the channel as an admin and that you used the correct @username.")
            return bot.reply_to(message, f"❌ Unexpected error: {e}")

        settings = settings_col.find_one({"_id": "global_settings"}) or {}
        channels = settings.get("channels", [])
        # Store the username (leading @) in the url field for backward compatibility
        channels.append({"name": name, "url": username})

        settings_col.update_one(
            {"_id": "global_settings"},
            {"$set": {"channels": channels}},
            upsert=True
        )
        bot.reply_to(message, f"✅ Added channel: {name}")
    except Exception as e:
        log_exception(e)
        bot.reply_to(message, f"❌ Failed to add channel. Error: {e}")
        try:
            input_text = message.text.strip()
            if "-" not in input_text:
                return bot.reply_to(message, "\u2757 Invalid format. Use: `ChannelName - @username` or `ChannelName - https://t.me/yourchannel`", parse_mode="Markdown")

            name, identifier = [x.strip() for x in input_text.split("-", 1)]

            # Basic validation
            if not (identifier.startswith("@") or identifier.startswith("http")):
                return bot.reply_to(message, "\u2757 Invalid identifier. Use @username or a valid https://t.me/ link.", parse_mode="Markdown")

            # Normalize identifier and try to resolve chat info
            username_part = None
            chat_id = None

            if identifier.startswith("@"):
                username_part = identifier[1:]
            elif "t.me" in identifier:
                username_part = identifier.rstrip('/').split('/')[-1]

            # If the last segment looks like an invite code (starts with +) we cannot resolve it with get_chat.
            if username_part and username_part.startswith('+'):
                # Private channel invite link - instruct admin to forward a message
                admin_states[message.from_user.id] = {"stage": "awaiting_channel_forward", "pending_name": name}
                return bot.reply_to(message, (
                    "\u26a0\ufe0f This looks like a private invite link.\n"
                    "Please add the bot to the channel as an admin. Then forward any message from the channel to me so I can register it, or provide the public @username if available."
                ))

            # Try to get chat and its id for future checks
            if username_part:
                try:
                    # Prefer using @username when calling get_chat
                    chat_obj = bot.get_chat(f"@{username_part}")
                    chat_id = chat_obj.id
                    # verify bot is a member/admin in that chat
                    me = bot.get_me()
                    try:
                        bot_member = bot.get_chat_member(chat_id, me.id)
                        if bot_member.status in ["left", "kicked"]:
                            return bot.reply_to(message, "\u274c I am not a member of that channel. Please add the bot as an admin and try again.")
                    except Exception:
                        # get_chat_member may fail for some chats; continue but warn
                        pass
                except telebot.apihelper.ApiTelegramException as e:
                    # give a helpful message
                    if "chat not found" in str(e).lower() or e.description == "Bad Request: chat not found":
                        return bot.reply_to(message, "\u274c Failed to verify channel access. Ensure the bot is added to the channel as an admin and that you used the correct public @username.")
                    else:
                        return bot.reply_to(message, f"\u274c Unexpected error: {e}")

            # Persist the channel. Store both the human name and the resolved chat_id (if available) and url (for display)
            settings = settings_col.find_one({"_id": "global_settings"}) or {}
            channels = settings.get("channels", [])
            channel_record = {"name": name}
            if chat_id:
                channel_record["chat_id"] = chat_id
            if username_part:
                channel_record["url"] = f"https://t.me/{username_part}"
            else:
                channel_record["url"] = identifier

            channels.append(channel_record)

            settings_col.update_one(
                {"_id": "global_settings"},
                {"$set": {"channels": channels}},
                upsert=True
            )
            bot.reply_to(message, f"\u2705 Added channel: {name}")
        except Exception as e:
            log_exception(e)
            bot.reply_to(message, f"\u274c Failed to add channel. Error: {e}")


    @bot.message_handler(func=lambda m: m.chat.type == "private" and admin_states.get(m.from_user.id, {}).get("stage") == "awaiting_channel_forward")
    def register_channel_from_forward(message):
        """When an admin forwards a message from a private channel, capture the channel id and save it."""
        try:
            state = admin_states.get(message.from_user.id)
            if not state:
                return
            if not message.forward_from_chat:
                return bot.reply_to(message, "\u274c Please forward a message from the channel (not send a link).")

            ch = message.forward_from_chat
            channel_id = ch.id
            name = state.get("pending_name") or (ch.title if hasattr(ch, 'title') else 'Channel')

            settings = settings_col.find_one({"_id": "global_settings"}) or {}
            channels = settings.get("channels", [])
            # Avoid duplicates by chat_id
            for existing in channels:
                if existing.get("chat_id") == channel_id:
                    del admin_states[message.from_user.id]
                    return bot.reply_to(message, f"\u2705 Channel already registered: {existing.get('name')}")

            channel_record = {"name": name, "chat_id": channel_id}
            # If forward_from_chat has username we can store a url for convenience
            if getattr(ch, 'username', None):
                channel_record["url"] = f"https://t.me/{ch.username}"

            channels.append(channel_record)
            settings_col.update_one({"_id": "global_settings"}, {"$set": {"channels": channels}}, upsert=True)
            del admin_states[message.from_user.id]
            bot.reply_to(message, f"\u2705 Registered channel: {name}")
        except Exception as e:
            log_exception(e)
            bot.reply_to(message, f"\u274c Failed to register channel from forwarded message: {e}")
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
    markup.add(InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"))
    markup.add(InlineKeyboardButton("Close", callback_data="close_admin"))

    bot.send_message(chat_id=call.message.chat.id,
                          text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "toggle_force_sub")
@admin_only(bot)
def toggle_force_subscription(call):
    try:
        settings = settings_col.find_one({"_id": "global_settings"}) or {}
        force_sub = settings.get("force_subscription", False)
        new_force_sub = not force_sub

        settings_col.update_one(
            {"_id": "global_settings"},
            {"$set": {"force_subscription": new_force_sub}},
            upsert=True
        )

        status = "enabled" if new_force_sub else "disabled"
        bot.answer_callback_query(call.id, f"✅ Force subscription {status}.")
        admin_panel(call)
    except Exception as e:
        log_exception(e)
        bot.answer_callback_query(call.id, "❌ Failed to toggle force subscription.")

@bot.callback_query_handler(func=lambda c: c.data == "close_admin")
@admin_only(bot)
def close_admin_panel(call):
    try:
        user = users.find_one({"userId": call.message.chat.id})

        # Delete the home message with the buttons
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass  # Ignore if message already deleted or can't delete
    show_main_menu(bot,call.message.chat.id,user=user)

@bot.callback_query_handler(func=lambda c: c.data == "broadcast")
def broadcast_entry(call):
    clear_user_session(call.from_user.id)
    if not is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "Access denied.")

    try:
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✍️ Write Post", callback_data="broadcast_write"),
            InlineKeyboardButton("📢 Forward from Channel", callback_data="broadcast_forward")
        )
        bot.send_message(call.message.chat.id, "Choose broadcast method:", reply_markup=markup)
    except Exception as e:
        log_exception(e)

@bot.callback_query_handler(func=lambda c: c.data == "broadcast_write")
def broadcast_write_start(call):
    admin_states[call.from_user.id] = {"stage": "awaiting_text"}
    bot.send_message(call.message.chat.id, "✍️ Send the broadcast text:")

@bot.message_handler(func=lambda m: m.chat.type == "private" and admin_states.get(m.from_user.id, {}).get("stage") == "awaiting_text")
def receive_broadcast_text(message):
    try:
        text = message.text.strip()
        if not text:
            return bot.send_message(message.chat.id, "❌ Message cannot be empty.")
        admin_states[message.from_user.id]["text"] = text
        admin_states[message.from_user.id]["stage"] = "ask_image"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📷 Yes, Add Image", callback_data="broadcast_add_image"),
            InlineKeyboardButton("❌ No, Text Only", callback_data="broadcast_no_image")
        )
        bot.send_message(message.chat.id, "Do you want to add an image?", reply_markup=markup)
    except Exception as e:
        log_exception(e)
        bot.send_message(message.chat.id, "❌ Error processing your input.")

@bot.callback_query_handler(func=lambda c: c.data in ["broadcast_add_image", "broadcast_no_image"])
def broadcast_image_decision(call):
    try:
        state = admin_states.get(call.from_user.id)
        if not state:
            return bot.answer_callback_query(call.id, "Session expired.")
        if call.data == "broadcast_add_image":
            state["stage"] = "awaiting_image"
            bot.send_message(call.message.chat.id, "📤 Send the image now:")
        else:
            state["image"] = None
            state["stage"] = "confirm"
            preview_broadcast(call.message.chat.id, call.from_user.id)
    except Exception as e:
        log_exception(e)
        bot.send_message(call.message.chat.id, "❌ Error in image decision step.")

@bot.message_handler(content_types=['photo'], func=lambda m: m.chat.type == "private" and admin_states.get(m.from_user.id, {}).get("stage") == "awaiting_image")
def receive_broadcast_image(message):
    try:
        state = admin_states[message.from_user.id]
        state["image"] = message.photo[-1].file_id
        state["stage"] = "confirm"
        preview_broadcast(message.chat.id, message.from_user.id)
    except Exception as e:
        log_exception(e)
        bot.send_message(message.chat.id, "❌ Error receiving image.")

def preview_broadcast(chat_id, admin_id):
    try:
        state = admin_states.get(admin_id)
        text = state.get("text", "")
        image = state.get("image")

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Confirm & Send", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        )

        if image:
            bot.send_photo(chat_id, image, caption=text, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    except Exception as e:
        log_exception(e)
        bot.send_message(chat_id, "❌ Could not preview broadcast.")

@bot.callback_query_handler(func=lambda c: c.data in ["broadcast_confirm", "broadcast_cancel"])
def broadcast_confirm_or_cancel(call):
    try:
        userId = call.from_user.id
        chat_id = call.message.chat.id
        state = admin_states.get(userId)
        bot.answer_callback_query(call.id)

        if not state:
            return bot.send_message(chat_id, "⚠️ No active broadcast found.")
        if call.data == "broadcast_cancel":
            del admin_states[userId]
            return bot.send_message(chat_id, "❌ Broadcast cancelled.")
        bot.send_message(chat_id, "📤 Sending broadcast to all users...")
        Thread(target=send_broadcast_to_all, args=(userId,)).start()
    except Exception as e:
        log_exception(e)
        bot.send_message(call.message.chat.id, "❌ Broadcast failed.")

def send_broadcast_to_all(admin_id):
    try:
        state = admin_states.get(admin_id)
        if not state:
            return
        text = state.get("text", "")
        image = state.get("image")
        count, failed = 0, 0

        for user in users.find():
            uid = user.get("userId")
            try:
                if image:
                    bot.send_photo(uid, image, caption=text)
                else:
                    bot.send_message(uid, text)
                count += 1
            except Exception as e:
                failed += 1
                log_exception(e)
            sleep(0.07)

        del admin_states[admin_id]
        bot.send_message(admin_id, f"✅ Broadcast finished.\n\n✅ Sent: {count}\n❌ Failed: {failed}")
    except Exception as e:
        log_exception(e)

@bot.callback_query_handler(func=lambda c: c.data == "broadcast_forward")
def ask_forward_message(call):
    try:
        admin_states[call.from_user.id] = {"stage": "awaiting_forward"}
        bot.send_message(call.message.chat.id, "📨 Forward the message from the channel here:")
    except Exception as e:
        log_exception(e)

@bot.message_handler(func=lambda m: m.chat.type == "private" and admin_states.get(m.from_user.id, {}).get("stage") == "awaiting_forward")
def handle_forwarded_message(message):
    try:
        if not message.forward_from_chat:
            return bot.send_message(message.chat.id, "❌ Please forward a message from a channel.")
        state = admin_states[message.from_user.id]
        state["forward_msg_id"] = message.message_id
        state["chat_id"] = message.chat.id
        state["stage"] = "confirm_forward"

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Confirm & Send", callback_data="broadcast_forward_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        )
        bot.send_message(message.chat.id, "Forwarded message received. Confirm to broadcast it:", reply_markup=markup)
    except Exception as e:
        log_exception(e)
        bot.send_message(message.chat.id, "❌ Failed to process forwarded message.")

@bot.callback_query_handler(func=lambda c: c.data == "broadcast_forward_confirm")
def confirm_forwarded_broadcast(call):
    try:
        bot.answer_callback_query(call.id)
        state = admin_states.get(call.from_user.id)
        if not state:
            return bot.send_message(call.message.chat.id, "⚠️ No active forward to send.")
        source_chat_id = state["chat_id"]
        msg_id = state["forward_msg_id"]
        bot.send_message(call.message.chat.id, "📤 Broadcasting forwarded message...")
        Thread(target=send_forwarded_broadcast_to_all, args=(call.from_user.id, source_chat_id, msg_id)).start()
    except Exception as e:
        log_exception(e)
        bot.send_message(call.message.chat.id, "❌ Forwarding failed.")

def send_forwarded_broadcast_to_all(admin_id, source_chat_id, msg_id):
    try:
        count, failed = 0, 0
        for user in users.find():
            uid = user.get("userId")
            try:
                bot.forward_message(uid, source_chat_id, msg_id)
                count += 1
            except Exception as e:
                failed += 1
                log_exception(e)
            sleep(0.07)
        del admin_states[admin_id]
        bot.send_message(admin_id, f"✅ Forward broadcast done.\n\n✅ Sent: {count}\n❌ Failed: {failed}")
    except Exception as e:
        log_exception(e)
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    try:
        user_id = call.from_user.id
        settings = settings_col.find_one({"_id": "global_settings"}) or {}
        channels = settings.get("channels", [])

        if not channels:
            bot.answer_callback_query(call.id, "❌ No channels configured for subscription.")
            return

        joined_all = True
        for channel in channels:
            try:
                # Prefer stored chat_id if available
                chat_identifier = channel.get("chat_id")

                if not chat_identifier:
                    # Fallback to parsing url or username and use @username format
                    url = channel.get("url", "")
                    if url.startswith("https://t.me/") or url.startswith("http://t.me/"):
                        username = url.rstrip('/').split('/')[-1]
                        # if it's an invite token (like joinchat/XYZ or starts with +) we cannot resolve
                        if username.startswith("joinchat") or username.startswith("+"):
                            bot.answer_callback_query(call.id, "⚠️ A required channel is private and cannot be checked by username. Please ask an admin to add the bot to that channel and register it by forwarding a channel message.")
                            return
                        chat_identifier = f"@{username}"
                    elif url.startswith("@"):
                        chat_identifier = url
                    else:
                        # last-resort: use whatever is stored
                        chat_identifier = url

                # If chat_identifier looks numeric, convert to int
                try:
                    if isinstance(chat_identifier, str) and chat_identifier.lstrip('-').isdigit():
                        chat_identifier = int(chat_identifier)
                except Exception:
                    pass

                member = bot.get_chat_member(chat_identifier, user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    joined_all = False
                    break
            except telebot.apihelper.ApiTelegramException as e:
                # If the bot cannot access the channel or it's misconfigured, inform admin/user
                log_exception(e)
                # common error: chat not found -> bot not added or bad username
                if "chat not found" in str(e).lower() or (hasattr(e, 'description') and e.description == "Bad Request: chat not found"):
                    bot.answer_callback_query(call.id, "⚠️ One of the required channels is not reachable. Please ask an admin to ensure the bot is added to the channel and that the channel's public @username is correct.")
                    return
                joined_all = False
                break
            except Exception as e:
                log_exception(e)
                joined_all = False
                break

        if joined_all:
            bot.answer_callback_query(call.id, "✅ You have joined all required channels.")
            user = users.find_one({"userId": call.from_user.id})
            show_main_menu(bot, call.message.chat.id, user)
        else:
            bot.answer_callback_query(call.id, "❌ Please join all required channels.")
    except Exception as e:
        log_exception(e)
        bot.answer_callback_query(call.id, "❌ Failed to verify subscription.")
bot.remove_webhook()

print("Bot running...")
bot.infinity_polling()
