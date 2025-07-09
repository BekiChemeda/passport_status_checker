# utils/database.py
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["passport_bot"]

users_col = db["users"]
settings_col = db["settings"]
