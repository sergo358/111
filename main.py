import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from core.logging import setup_logging
from core.bot import bot, dp
from db.init_db import init_db

from handlers.client import router as client_router
from handlers.specialist import router as specialist_router
from handlers.review import router as review_router
from handlers.admin import router as admin_router

async def main():
    setup_logging()
    await init_db()
    dp.include_router(client_router)
    dp.include_router(specialist_router)
    dp.include_router(review_router)
    dp.include_router(admin_router)
    storage = MemoryStorage()
    await dp.start_polling(bot, storage=storage)

if __name__ == "__main__":
    asyncio.run(main())