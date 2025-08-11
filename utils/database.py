# utils/database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from .env into os.environ
try:

    uri = os.getenv("MONGO_URI")

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.server_info()

    print("MONGO_URI:", os.getenv("MONGO_URI"))

    db = client["passport_bot"]

    users_col = db["users"]
    settings_col = db["settings"]
except Exception as e:
    print("error connecting to db", e)
# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv
#
# load_dotenv()
#
# uri = os.getenv("MONGO_URI")
# try:
#     client = MongoClient(uri, serverSelectionTimeoutMS=5000)
#     print()  # Forces connection
#     print("✅ Connected to MongoDB")
# except Exception as e:
#     print("❌ Connection failed:", e)
