from config.config import BOT_TOKEN, ADMINS, DB_FILE
from typing import Optional

class Settings:
    bot_token: str = BOT_TOKEN if BOT_TOKEN else ''
    admins: list[int] = ADMINS
    db_file: str = DB_FILE

    # Database settings
    DATABASE = {
        'ENGINE': 'postgresql',
        'NAME': 'telezapis',
        'USER': 'telezapis_user',
        'PASSWORD': 'securepassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }

settings = Settings()