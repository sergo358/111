import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

load_dotenv()
TOKEN = os.getenv("TOKEN")

async def start(update, context):
    await update.message.reply_text("Привет! Я твой бот.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()