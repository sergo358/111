from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from utils import EMOJI_SUCCESS, EMOJI_DANGER, EMOJI_BACK
from db_manager import get_specialist_by_id, get_services_by_specialist

(
    STATE_SERVICES,
    STATE_ADD_SERVICE_NAME,
    STATE_ADD_SERVICE_DURATION,
    STATE_ADD_SERVICE_PRICE,
    STATE_ADD_SERVICE_EMOJI,
    STATE_CONFIRM_ADD_SERVICE
) = range(6)

async def start_specialist(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    # Для MVP: id специалиста == user_id
    specialist = await get_specialist_by_id(user_id)
    if not specialist:
        await update.message.reply_text(
            "Вы ещё не зарегистрированы как специалист. Обратитесь к администратору.",
        )
        return ConversationHandler.END
    await update.message.reply_text(
        f"Привет, {specialist['name']}! 😎\n\nЧто будем делать?",
        reply_markup=main_menu_specialist()
    )
    return ConversationHandler.END

async def show_services(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    services = await get_services_by_specialist(user_id)
    if not services:
        msg = "У вас пока нет услуг. Добавим первую? 😉"
    else:
        msg = "Ваши услуги:\n\n"
        for s in services:
            msg += f"{s['emoji']} *{s['name']}* — {s['duration']} мин, {s['price']}₽\n"
    await update.callback_query.edit_message_text(
        msg,
        parse_mode="Markdown",
        reply_markup=main_menu_specialist()
    )
    return ConversationHandler.END

# Фрагмент сценария добавления услуги (будет доработан)
async def add_service_start(update: Update, context: CallbackContext):
    await update.callback_query.edit_message_text(
        "Введи название новой услуги:",
        reply_markup=confirm_cancel_keyboard("cancel_add_service", "cancel_add_service")
    )
    return STATE_ADD_SERVICE_NAME

# ... (другие шаги добавления услуги)

specialist_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_specialist, pattern="i_am_specialist")],
    states={
        STATE_SERVICES: [
            CallbackQueryHandler(show_services, pattern="specialist_services"),
            CallbackQueryHandler(add_service_start, pattern="add_service"),
        ],
        # Остальные шаги — добавление услуги, редактирование и пр.
    },
    fallbacks=[
        CommandHandler("start", start_specialist),
    ],
    allow_reentry=True
)