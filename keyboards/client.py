from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = [
        [InlineKeyboardButton(text="🟢 Записаться", callback_data="book")],
        [InlineKeyboardButton(text="⭐️ Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="💬 Оставить отзыв", callback_data="leave_review")],
        [InlineKeyboardButton(text="👑 Панель специалиста", callback_data="specialist_menu")],
        [InlineKeyboardButton(text="⚙️ Админка", callback_data="admin_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def specialists_kb(specialists):
    kb = [
        [InlineKeyboardButton(text=f"{s['avatar']} {s['name']}", callback_data=f"spec_{s['id']}")]
        for s in specialists
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def services_kb(services):
    kb = [
        [InlineKeyboardButton(text=f"{s['emoji']} {s['name']} ({s['price']}₽)", callback_data=f"svc_{s['id']}")]
        for s in services
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def dates_kb(dates):
    kb = [
        [InlineKeyboardButton(text=d, callback_data=f"date_{d}")]
        for d in dates
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def times_kb(times):
    kb = [
        [InlineKeyboardButton(text=t, callback_data=f"time_{t}")]
        for t in times
    ]
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
        ]
    )