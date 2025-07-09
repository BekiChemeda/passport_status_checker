
# 🇪🇹 Ethiopian Passport Status Checker Bot

This is a Telegram bot that allows users to check the **status of their Ethiopian passport application** using either:

- ✅ Tracking Code  
- ✅ Full Name + Branch

It also offers info on **how to register**, **renew**, and get **urgent services** via Telegram.

---

## 🚀 Features

- 🛂 Check passport status via tracking code or full name
- 🌐 Multi-branch support
- 📚 Help command with examples
- 🔄 Inline navigation with clean UX
- 🧑‍💻 Admin-only features to manage channels
- 🌍 Hosted on [Render](https://render.com) using **Flask + Webhooks**

---

## 🛠 Tech Stack

- Python with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Flask (for webhook endpoint)
- MongoDB (via `pymongo`)
- Render (for deployment)

---

## 🐍 Installation

```bash
git clone https://github.com/BekiChemeda/passport_status_checker.git
cd passport_status_checker
pip install -r requirements.txt
````

Create a `.env` file and add:

```env
BOT_TOKEN=your_bot_token
WEBHOOK_URL=https://your-render-app.onrender.com/webhook
MONGO_URI=your_mongodb_connection_string
```

---

## 🧪 Run Locally (for development)

```bash
python main.py
```

---

## 🌐 Run with Webhook (for production)

Make sure you’re using `Flask` and `set_webhook()` in your `main.py` like this:

```python
bot.set_webhook(url=WEBHOOK_URL)
```

Then deploy to [Render](https://render.com):

### 📦 Files Required:

* `main.py` (your main bot logic)
* `requirements.txt`
* `Procfile`

### 🔧 Render Setup:

* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `python main.py`
* **Environment Variables**:

  * `BOT_TOKEN`
  * `WEBHOOK_URL`
  * `MONGO_URI`

---

## 🧾 Example Inputs

* **Tracking Code**: `AAL1234567`
* **Full Name**: `ABEBE KEBEDE HAILE`
* **Branch**: `ICS Saris Adey Abeba Branch`

---

## 🤖 Usage

| Command     | Description                               |
| ----------- | ----------------------------------------- |
| `/start`    | Starts the bot and shows main menu        |
| `/help`     | Shows how to use the bot                  |
| `/channels` | (Admin) View and manage required channels |

---

## 💡 Notes

* This bot does not register or renew passports directly.

---

## 📄 License

MIT License © 2025 Beki Chemeda


