from config.config import BOT_TOKEN, ADMINS, DB_FILE

class Settings:
    bot_token: str = BOT_TOKEN
    admins: list[int] = ADMINS
    db_file: str = DB_FILE

settings = Settings()