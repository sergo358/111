from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from utils import (
    main_menu_client, specialists_list_keyboard, generate_calendar,
    available_time_keyboard, confirm_cancel_keyboard, EMOJI_SUCCESS, EMOJI_DANGER, EMOJI_STAR, EMOJI_BACK, get_specialist_avatar
)
from db_manager import get_all_specialists, get_available_dates, get_available_times, book_appointment
from localization import (
    GREETING_CLIENT, CHOOSE_SPECIALIST, CHOOSE_DATE, CHOOSE_TIME, CONFIRM_BOOKING, BOOKING_DONE, CANCELLED, UNKNOWN_COMMAND
)

# States for ConversationHandler
(
    STATE_SPECIALIST,
    STATE_DATE,
    STATE_TIME,
    STATE_CONFIRM
) = range(4)

# --- Стартовое меню клиента ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        GREETING_CLIENT,
        reply_markup=main_menu_client(),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# --- Начать запись (шаг 1: выбор специалиста) ---
def start_booking(update: Update, context: CallbackContext):
    specialists = get_all_specialists()
    update.callback_query.edit_message_text(
        CHOOSE_SPECIALIST,
        reply_markup=specialists_list_keyboard(specialists)
    )
    return STATE_SPECIALIST

def choose_specialist(update: Update, context: CallbackContext):
    query = update.callback_query
    spec_id = int(query.data.split("_")[-1])
    context.user_data['spec_id'] = spec_id
    available_dates = get_available_dates(spec_id)
    query.edit_message_text(
        CHOOSE_DATE,
        reply_markup=generate_calendar(
            year=available_dates['year'],
            month=available_dates['month'],
            available_dates=available_dates['dates']
        )
    )
    return STATE_DATE

def choose_date(update: Update, context: CallbackContext):
    query = update.callback_query
    date_str = query.data.replace("calendar_day_", "")
    context.user_data['date'] = date_str
    spec_id = context.user_data['spec_id']
    times = get_available_times(spec_id, date_str)
    query.edit_message_text(
        CHOOSE_TIME,
        reply_markup=available_time_keyboard(times)
    )
    return STATE_TIME

def choose_time(update: Update, context: CallbackContext):
    query = update.callback_query
    time_str = query.data.replace("choose_time_", "")
    context.user_data['time'] = time_str
    spec_id = context.user_data['spec_id']
    date = context.user_data['date']
    specialist = next(s for s in get_all_specialists() if s['id'] == spec_id)
    avatar = get_specialist_avatar(spec_id)
    msg = (
        f"{EMOJI_STAR} *Проверьте ваш выбор:*\n\n"
        f"{avatar} *{specialist['name']}*\n"
        f"🗓️ {date}\n"
        f"⏰ {time_str}\n\n"
        f"Все верно?"
    )
    query.edit_message_text(
        msg,
        reply_markup=confirm_cancel_keyboard("confirm_booking", "cancel_booking"),
        parse_mode="Markdown"
    )
    return STATE_CONFIRM

def confirm_booking(update: Update, context: CallbackContext):
    user = update.effective_user
    spec_id = context.user_data['spec_id']
    date = context.user_data['date']
    time = context.user_data['time']
    result = book_appointment(user.id, spec_id, date, time)
    if result:
        update.callback_query.edit_message_text(
            BOOKING_DONE.format(date=date, time=time),
            reply_markup=main_menu_client()
        )
    else:
        update.callback_query.edit_message_text(
            f"{EMOJI_DANGER} К сожалению, слот уже занят. Попробуйте другое время.",
            reply_markup=main_menu_client()
        )
    return ConversationHandler.END

def cancel_booking(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        CANCELLED,
        reply_markup=main_menu_client()
    )
    return ConversationHandler.END

def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text(UNKNOWN_COMMAND, reply_markup=main_menu_client())

# --- ConversationHandler для записи за 3 клика ---
booking_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_booking, pattern="find_specialist")],
    states={
        STATE_SPECIALIST: [CallbackQueryHandler(choose_specialist, pattern="choose_specialist_")],
        STATE_DATE: [CallbackQueryHandler(choose_date, pattern="calendar_day_")],
        STATE_TIME: [CallbackQueryHandler(choose_time, pattern="choose_time_")],
        STATE_CONFIRM: [
            CallbackQueryHandler(confirm_booking, pattern="confirm_booking"),
            CallbackQueryHandler(cancel_booking, pattern="cancel_booking"),
        ],
    },
    fallbacks=[
        CommandHandler("start", start),
        MessageHandler(Filters.command, unknown_command)
    ],
    allow_reentry=True
)