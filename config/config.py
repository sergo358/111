import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x]
DB_FILE = os.getenv("DB_FILE", "telezapis.db")