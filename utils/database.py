from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file into environment

MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI is None:
    raise Exception("MONGO_URI is not set")

client = MongoClient(MONGO_URI)
db = client["passport_bot"]

users_col = db["users"]
settings_col = db["settings"]
