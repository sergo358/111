from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config.config import ADMINS
from db.repositories import get_all_specialists, get_reviews_for_specialist
from keyboards.client import specialists_kb, main_menu

router = Router(name=__name__)

@router.message(Command("admin"))
async def admin_menu(msg: Message):
    if msg.from_user.id not in ADMINS:
        await msg.answer("Нет доступа.")
        return
    kb = [
        [{"text": "👤 Все специалисты", "callback_data": "admin_specialists"}],
        [{"text": "⭐️ Последние отзывы", "callback_data": "admin_reviews"}],
        [{"text": "⬅️ На главную", "callback_data": "back"}]
    ]
    await msg.answer("Панель администратора:", reply_markup={"inline_keyboard": kb})

@router.callback_query(F.data == "admin_specialists")
async def admin_specialists(call: CallbackQuery):
    specialists = await get_all_specialists()
    text = "Список специалистов:\n\n"
    for s in specialists:
        text += f"{s['avatar']} <b>{s['name']}</b> — {s['bio']}\n"
    await call.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "admin_reviews")
async def admin_reviews(call: CallbackQuery):
    specialists = await get_all_specialists()
    text = "Последние отзывы:\n\n"
    for s in specialists:
        reviews = await get_reviews_for_specialist(s['id'])
        for r in reviews:
            text += f"{s['avatar']} <b>{s['name']}</b>: {r['text']} ({r['stars']}⭐️)\n"
    await call.message.edit_text(text or "Нет отзывов.", reply_markup=main_menu(), parse_mode="HTML")