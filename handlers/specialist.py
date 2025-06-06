from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from services.specialist_service import SpecialistService
from db.repositories import get_services_for_specialist
from keyboards.client import main_menu, services_kb, confirm_kb
from utils.texts import *

router = Router(name=__name__)

class SpecialistFSM(StatesGroup):
    ADD_NAME = State()
    ADD_DURATION = State()
    ADD_PRICE = State()
    ADD_EMOJI = State()
    CONFIRM = State()

@router.callback_query(F.data == "specialist_menu")
async def specialist_menu(call: CallbackQuery, state: FSMContext):
    services = await get_services_for_specialist(call.from_user.id)
    text = "Ваши услуги:\n\n" if services else "У вас нет услуг. Добавим первую?"
    for s in services:
        text += f"{s['emoji']} <b>{s['name']}</b> — {s['duration']} мин, {s['price']}₽\n"
    kb = [
        [{"text": "➕ Добавить услугу", "callback_data": "add_service"}],
        [{"text": "⬅️ Назад", "callback_data": "back"}]
    ]
    await call.message.edit_text(text, reply_markup={"inline_keyboard": kb}, parse_mode="HTML")

@router.callback_query(F.data == "add_service")
async def add_service_start(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите название новой услуги:")
    await state.set_state(SpecialistFSM.ADD_NAME)

@router.message(SpecialistFSM.ADD_NAME)
async def add_service_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Укажите длительность (мин):")
    await state.set_state(SpecialistFSM.ADD_DURATION)

@router.message(SpecialistFSM.ADD_DURATION)
async def add_service_duration(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Введите только число (минуты):")
        return
    await state.update_data(duration=int(msg.text))
    await msg.answer("Введите цену (₽):")
    await state.set_state(SpecialistFSM.ADD_PRICE)

@router.message(SpecialistFSM.ADD_PRICE)
async def add_service_price(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Введите только число (рубли):")
        return
    await state.update_data(price=int(msg.text))
    await msg.answer("Выберите emoji для услуги (или отправьте):")
    await state.set_state(SpecialistFSM.ADD_EMOJI)

@router.message(SpecialistFSM.ADD_EMOJI)
async def add_service_emoji(msg: Message, state: FSMContext):
    await state.update_data(emoji=msg.text)
    data = await state.get_data()
    preview = (
        f"Проверьте:\n"
        f"{data['emoji']} <b>{data['name']}</b>\n"
        f"⏱ {data['duration']} мин\n"
        f"💰 {data['price']}₽"
    )
    await msg.answer(preview, reply_markup=confirm_kb(), parse_mode="HTML")
    await state.set_state(SpecialistFSM.CONFIRM)

@router.callback_query(SpecialistFSM.CONFIRM, F.data == "confirm")
async def add_service_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    from db.repositories import aiosqlite
    from core.settings import settings
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute(
            "INSERT INTO services (specialist_id, name, duration, price, emoji) VALUES (?, ?, ?, ?, ?)",
            (call.from_user.id, data['name'], data['duration'], data['price'], data['emoji'])
        )
        await db.commit()
    await call.message.edit_text("Услуга добавлена!", reply_markup=main_menu())
    await state.clear()

@router.callback_query(SpecialistFSM.CONFIRM, F.data == "cancel")
async def add_service_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Добавление услуги отменено.", reply_markup=main_menu())
    await state.clear()