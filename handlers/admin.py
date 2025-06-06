from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config.config import ADMINS
from db.repositories import get_all_specialists, get_reviews_for_specialist, get_services_for_specialist, aiosqlite
from keyboards.client import specialists_kb, main_menu
from core.settings import settings

router = Router(name=__name__)

class AddServiceFSM(StatesGroup):
    name = State()
    emoji = State()
    duration = State()
    price = State()

class DeleteServiceFSM(StatesGroup):
    select = State()
    confirm = State()

@router.message(Command("admin"))
async def admin_menu(msg: Message):
    if not msg.from_user or not msg.from_user.id:
        await msg.answer("Ошибка: пользователь не найден.")
        return
    if msg.from_user.id not in ADMINS:
        await msg.answer("Нет доступа.")
        return
    kb = [
        [{"text": "👤 Все специалисты", "callback_data": "admin_specialists"}],
        [{"text": "⭐️ Последние отзывы", "callback_data": "admin_reviews"}],
        [{"text": "➕ Добавить специалиста", "callback_data": "add_specialist"}],
        [{"text": "✏️ Редактировать специалиста", "callback_data": "edit_specialist"}],
        [{"text": "❌ Удалить специалиста", "callback_data": "delete_specialist"}],
        [{"text": "🛠️ Управление услугами", "callback_data": "manage_services"}],
        [{"text": "📊 Статистика", "callback_data": "view_statistics"}],
        [{"text": "⬅️ На главную", "callback_data": "back"}]
    ]
    await msg.answer("Панель администратора:", reply_markup={"inline_keyboard": kb})

@router.callback_query(F.data == "admin_specialists")
async def admin_specialists(call: CallbackQuery):
    if not call.from_user or not call.from_user.id:
        await call.message.edit_text("Ошибка: пользователь не найден.")
        return
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

@router.callback_query(F.data == "add_specialist")
async def add_specialist(call: CallbackQuery):
    await call.message.edit_text("Введите имя нового специалиста:")
    # Логика добавления специалиста
    name = "Иван"  # Пример имени
    avatar = "👨‍🔧"  # Пример аватара
    bio = "Новый специалист"  # Пример описания
    # Removed redundant imports as they are now at the top of the file
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute(
            "INSERT INTO specialists (name, avatar, bio) VALUES (?, ?, ?)",
            (name, avatar, bio)
        )
        await db.commit()
    await call.message.edit_text("Специалист добавлен!")

@router.callback_query(F.data == "edit_specialist")
async def edit_specialist(call: CallbackQuery):
    specialists = await get_all_specialists()
    text = "Выберите специалиста для редактирования:\n\n"
    for s in specialists:
        text += f"{s['avatar']} <b>{s['name']}</b> — {s['bio']}\n"
    await call.message.edit_text(text, reply_markup=specialists_kb(specialists), parse_mode="HTML")

@router.callback_query(F.data.startswith("edit_spec_"))
async def edit_spec_details(call: CallbackQuery):
    spec_id = int(call.data.split("_")[2])
    await call.message.edit_text(f"Редактирование специалиста с ID {spec_id} пока не реализовано.")

@router.callback_query(F.data == "delete_specialist")
async def delete_specialist(call: CallbackQuery):
    specialists = await get_all_specialists()
    text = "Выберите специалиста для удаления:\n\n"
    for s in specialists:
        text += f"{s['avatar']} <b>{s['name']}</b> — {s['bio']}\n"
    await call.message.edit_text(text, reply_markup=specialists_kb(specialists), parse_mode="HTML")

@router.callback_query(F.data.startswith("delete_spec_"))
async def delete_spec_confirm(call: CallbackQuery):
    spec_id = int(call.data.split("_")[2])
    from db.repositories import aiosqlite
    from core.settings import settings
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute("DELETE FROM specialists WHERE id = ?", (spec_id,))
        await db.commit()
    await call.message.edit_text(f"Специалист с ID {spec_id} удалён.")

@router.callback_query(F.data == "manage_services")
async def manage_services(call: CallbackQuery):
    services = await get_services_for_specialist(call.from_user.id)
    text = "Ваши услуги:\n\n" if services else "У вас нет услуг. Добавим первую?"
    for s in services:
        text += f"{s['emoji']} <b>{s['name']}</b> — {s['duration']} мин, {s['price']}₽\n"
    kb = [
        [{"text": "➕ Добавить услугу", "callback_data": "add_service"}],
        [{"text": "✏️ Редактировать услугу", "callback_data": "edit_service"}],
        [{"text": "❌ Удалить услугу", "callback_data": "delete_service"}],
        [{"text": "⬅️ Назад", "callback_data": "back"}]
    ]
    await call.message.edit_text(text, reply_markup={"inline_keyboard": kb}, parse_mode="HTML")

@router.callback_query(F.data == "add_service")
async def add_service(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите название новой услуги:")
    await state.set_state(AddServiceFSM.name)

@router.message(AddServiceFSM.name)
async def add_service_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите эмодзи для услуги:")
    await state.set_state(AddServiceFSM.emoji)

@router.message(AddServiceFSM.emoji)
async def add_service_emoji(msg: Message, state: FSMContext):
    await state.update_data(emoji=msg.text)
    await msg.answer("Введите длительность услуги в минутах:")
    await state.set_state(AddServiceFSM.duration)

@router.message(AddServiceFSM.duration)
async def add_service_duration(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Пожалуйста, введите число (минуты):")
        return
    await state.update_data(duration=int(msg.text))
    await msg.answer("Введите цену услуги в рублях:")
    await state.set_state(AddServiceFSM.price)

@router.message(AddServiceFSM.price)
async def add_service_price(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Пожалуйста, введите число (рубли):")
        return
    await state.update_data(price=int(msg.text))
    data = await state.get_data()
    # Сохраняем в БД
    from db.repositories import aiosqlite
    from core.settings import settings
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute(
            "INSERT INTO services (specialist_id, name, emoji, duration, price) VALUES (?, ?, ?, ?, ?)",
            (msg.from_user.id, data['name'], data['emoji'], data['duration'], data['price'])
        )
        await db.commit()
    await msg.answer("Услуга добавлена!")
    await state.clear()

@router.callback_query(F.data == "delete_service")
async def delete_service(call: CallbackQuery, state: FSMContext):
    services = await get_services_for_specialist(call.from_user.id)
    if not services:
        await call.message.edit_text("У вас нет услуг для удаления.")
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{s['emoji']} {s['name']}", callback_data=f"del_srv_{s['id']}")]
            for s in services
        ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )
    await call.message.edit_text("Выберите услугу для удаления:", reply_markup=kb)
    await state.set_state(DeleteServiceFSM.select)

@router.callback_query(DeleteServiceFSM.select, F.data.startswith("del_srv_"))
async def delete_service_confirm(call: CallbackQuery, state: FSMContext):
    srv_id = int(call.data.split("_")[2])
    await state.update_data(srv_id=srv_id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_del_srv")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back")]
        ]
    )
    await call.message.edit_text("Вы уверены, что хотите удалить эту услугу?", reply_markup=kb)
    await state.set_state(DeleteServiceFSM.confirm)

@router.callback_query(DeleteServiceFSM.confirm, F.data == "confirm_del_srv")
async def delete_service_do(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    srv_id = data.get("srv_id")
    from db.repositories import aiosqlite
    from core.settings import settings
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute("DELETE FROM services WHERE id = ?", (srv_id,))
        await db.commit()
    await call.message.edit_text("Услуга удалена.")
    await state.clear()

@router.callback_query(F.data == "view_statistics")
async def view_statistics(call: CallbackQuery):
    # Пример статистики
    stats = "Всего записей: 100\nВсего отзывов: 50\nСредний рейтинг: 4.8"
    await call.message.edit_text(f"Статистика:\n\n{stats}")

# АНАЛИЗ И РЕКОМЕНДАЦИИ ПО РАЗВИТИЮ ПРОЕКТА

"""
1. Управление специалистами:
   - Добавление, редактирование, удаление реализованы базово.
   - Не хватает полноценного FSM для пошагового добавления/редактирования (имя, аватар, описание и т.д.).
   - Нет подтверждения удаления (можно добавить диалог подтверждения).
   - Нет проверки на связанные данные (например, услуги и отзывы при удалении специалиста).

2. Управление услугами:
   - Только заглушки для добавления, редактирования, удаления услуг.
   - Не реализован выбор услуги для редактирования/удаления.
   - Нет FSM для пошагового добавления/редактирования услуги (название, цена, длительность, эмодзи).
   - Не реализована связь услуг со специалистами (сейчас get_services_for_specialist вызывается с id пользователя, а не специалиста).

3. Отзывы:
   - Только просмотр последних отзывов.
   - Нет возможности модерировать или удалять отзывы.
   - Нет фильтрации/поиска по отзывам.

4. Статистика:
   - Только примерная заглушка.
   - Можно добавить реальные данные: количество специалистов, услуг, записей, отзывы по периодам и т.д.

5. UI/UX:
   - Клавиатуры формируются вручную, можно вынести в отдельные функции.
   - Нет возврата назад в FSM.
   - Нет уведомлений об ошибках при работе с БД.

6. Безопасность:
   - Проверка на администратора реализована.
   - Нет логирования действий админа.

7. Архитектура:
   - Логика работы с БД частично размазана по хендлерам.
   - Рекомендуется вынести всю работу с БД в отдельные репозитории/сервисы.
   - FSM-состояния лучше вынести в отдельные файлы.

РЕКОМЕНДУЕМЫЕ ШАГИ:
- Реализовать FSM для добавления/редактирования специалистов и услуг.
- Реализовать полноценное управление услугами (CRUD).
- Добавить подтверждение удаления (специалиста/услуги).
- Реализовать просмотр и модерирование отзывов.
- Улучшить статистику.
- Вынести клавиатуры и работу с БД в отдельные модули.
- Добавить логирование действий администратора.
- Покрыть основные сценарии тестами (юнит/интеграционными).
"""