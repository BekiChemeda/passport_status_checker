import telebot
import os
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers import start, check_status, admin
from utils.database import users_col
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import users_col, settings_col
from utils.decorators import admin_only
from utils.passport_api import check_by_reference, check_by_fullname
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
bot = telebot.TeleBot(BOT_TOKEN)
lang = "en"


# app = Flask(__name__)


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.delete_message(message.message.chat.id, message.message.message_id)
    except Exception:
        pass
    user_id = message.from_user.id
    user = users_col.find_one({"userId": user_id})

    if not user:
        users_col.insert_one({
            "userId": user_id,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "role": "user"
        })
    user = users_col.find_one({"userId": user_id})

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
    show_main_menu(bot, user_id, user)
    # print(user)


@bot.callback_query_handler(func=lambda call: call.data == "go_home")
def go_home_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    show_main_menu(bot, call.message.chat.id)


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
        "For any issues, contact [@BYTECODE](https://t.me/BYTE_CODE_SUPPORT_BOT)"
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
        InlineKeyboardButton("✅ Check Status", callback_data="check_status")
    )
    markup.add(
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
@bot.callback_query_handler(func=lambda c: c.data == "check_status")
def handle_check_status(call):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        user = users_col.find_one({"userId": call.from_user.id})
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
        user = users_col.find_one({"userId": call.from_user.id})
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
    user = users_col.find_one({"userId": call.from_user.id})
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
        user = users_col.find_one({"userId": call.from_user.id})
        lang = user.get("language", "en")
        result = check_by_fullname(full_name, branch, lang)
        bot.send_message(call.message.chat.id, result,parse_mode="MarkdownV2", reply_markup=get_main_menu_button())


@bot.message_handler(commands=["channels"])
def handle_channels_command(message):
    user = users_col.find_one({"userId": message.from_user.id})
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
    users_count = users_col.count_documents({})
    admins_count = users_col.count_documents({"role": "admin"})
    lang_counts = {
        "en": users_col.count_documents({"language": "en"}),
        "am": users_col.count_documents({"language": "am"}),
        "om": users_col.count_documents({"language": "om"})
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

bot.remove_webhook()

print("Bot running...")
bot.infinity_polling()
