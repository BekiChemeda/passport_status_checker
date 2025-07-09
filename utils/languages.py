# utils/languages.py

LANGUAGES = {
    "en": {
        "choose_language": "🌍 Please choose your language:",
        "check_status": "✅ Check Status",
        "about_us": "ℹ️ About Us",
        "our_channel": "📢 Our Channel",
        "developer": "👨‍💻 Developer",
        "send_tracking": "🔢 Please send your tracking reference code:",
        "send_fullname": "🧑‍🦱 Enter your full name (Name Father Grandfather):",
        "choose_branch": "🏢 Choose your ICS Branch:",
        "not_found": "❌ Your passport is either not ready or the input is invalid.",
        "subscription_required": "🚫 Please join all channels to use the bot.",
        "language_saved": "✅ Language preference saved.",
    },
    "am": {
        "choose_language": "🌍 እባክዎን ቋንቋዎን ይምረጡ፡",
        "check_status": "✅ የፓስፖርት ሁኔታ",
        "about_us": "ℹ️ ስለ እኛ",
        "our_channel": "📢 ቻናላችን",
        "developer": "👨‍💻 አበልጻጊ",
        "send_tracking": "🔢 የመከታተያ ቁጥርዎን ያስገቡ፡",
        "send_fullname": "🧑‍🦱 ሙሉ ስምዎን ያስገቡ (ስም አባት አያት):",
        "choose_branch": "🏢 የኢሚግሬሽን ቢሮ ይምረጡ፡",
        "not_found": "❌ የፓስፖርት ሁኔታ አልተገኘም፣ ቁጥሩን ደግመው ይፈትሹ።",
        "subscription_required": "🚫 ቻናላቱን በመቀላቀል ብቻ ቦቱን መጠቀም ይቻላል።",
        "language_saved": "✅ ቋንቋ በትክክል ተመዝግቧል።",
    },
    "om": {
        "choose_language": "🌍 Afaan filadhu:",
        "check_status": "✅ Haala Phaaspoortii",
        "about_us": "ℹ️ Waan Nu Ibsu",
        "our_channel": "📢 Chaanaalii Keenya",
        "developer": "👨‍💻 Develoopera",
        "send_tracking": "🔢 Lakkoofsa hordoffii kee galchi:",
        "send_fullname": "🧑‍🦱 Maqaa guutuu kee barreessi (Maqaa, Abbaa, Akaakayyuu):",
        "choose_branch": "🏢 Teessoo ICS filadhu:",
        "not_found": "❌ Odeeffannoo argachuu hin dandeenye. Maqaa/lakkoofsa sirriitti galchi.",
        "subscription_required": "🚫 Chaanaala hundaitti makamuun dirqama.",
        "language_saved": "✅ Afaan kee ni eeyyamameera.",
    }
}

def tr(key, lang="en"):
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
