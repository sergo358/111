from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from utils import EMOJI_STAR, EMOJI_BACK
from db_manager import get_all_specialists

(
    STATE_REVIEW_CHOOSE_SPEC,
    STATE_REVIEW_INPUT
) = range(2)

async def start_review(update: Update, context: CallbackContext):
    specialists = await get_all_specialists()
    kb = [[
        {"text": f"{s['avatar']} {s['name']}", "callback_data": f"review_spec_{s['id']}"}
    ] for s in specialists]
    kb.append([{"text": f"{EMOJI_BACK} Назад", "callback_data": "back_to_main"}])
    await update.callback_query.edit_message_text(
        "Кому хотите оставить отзыв? 😊",
        reply_markup={"inline_keyboard": kb}
    )
    return STATE_REVIEW_CHOOSE_SPEC

async def input_review(update: Update, context: CallbackContext):
    spec_id = int(update.callback_query.data.split("_")[-1])
    context.user_data["review_spec_id"] = spec_id
    await update.callback_query.edit_message_text(
        f"Напишите свой отзыв для специалиста. Не забудьте про звёздочки {EMOJI_STAR}!",
    )
    return STATE_REVIEW_INPUT

async def save_review(update: Update, context: CallbackContext):
    review_text = update.message.text
    # Тут — запись отзыва в базу
    await update.message.reply_text(
        "Спасибо за ваш отзыв! 🥰",
    )
    return ConversationHandler.END

review_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_review, pattern="leave_review")],
    states={
        STATE_REVIEW_CHOOSE_SPEC: [CallbackQueryHandler(input_review, pattern="review_spec_")],
        STATE_REVIEW_INPUT: [MessageHandler(Filters.text & ~Filters.command, save_review)],
    },
    fallbacks=[
        CommandHandler("start", start_review),
    ]
)