from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler
from db_manager import get_user_bookings, cancel_booking_by_id
from utils import EMOJI_SUCCESS, EMOJI_DANGER, EMOJI_BACK

async def show_bookings(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    bookings = await get_user_bookings(user_id)
    if not bookings:
        msg = "У вас пока нет записей. Запишитесь к специалисту!"
        await update.callback_query.edit_message_text(msg)
        return ConversationHandler.END
    msg = "Ваши записи:\n\n"
    kb = []
    for b in bookings:
        msg += f"{b['date']} {b['time']} — {b['service']} у {b['specialist']}\n"
        kb.append([{"text": f"❌ Отменить {b['date']} {b['time']}", "callback_data": f"cancel_booking_{b['id']}"}])
    kb.append([{"text": f"{EMOJI_BACK} Назад", "callback_data": "back_to_main"}])
    await update.callback_query.edit_message_text(
        msg,
        reply_markup={"inline_keyboard": kb}
    )
    return ConversationHandler.END

async def cancel_booking(update: Update, context: CallbackContext):
    booking_id = int(update.callback_query.data.split("_")[-1])
    await cancel_booking_by_id(booking_id)
    await update.callback_query.edit_message_text(
        f"{EMOJI_SUCCESS} Запись отменена.",
    )
    return ConversationHandler.END

bookings_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(show_bookings, pattern="my_bookings")],
    states={},
    fallbacks=[
        CallbackQueryHandler(cancel_booking, pattern="cancel_booking_")
    ]
)