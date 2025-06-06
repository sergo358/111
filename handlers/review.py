from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.specialist_service import SpecialistService
from services.review_service import ReviewService
from keyboards.client import specialists_kb, main_menu
from utils.texts import *

router = Router(name=__name__)

class ReviewFSM(StatesGroup):
    CHOOSE_SPEC = State()
    INPUT_TEXT = State()
    INPUT_STARS = State()

@router.callback_query(F.data == "leave_review")
async def choose_specialist(call: CallbackQuery, state: FSMContext):
    specialists = await SpecialistService.list_specialists()
    await call.message.edit_text("Кому хотите оставить отзыв?", reply_markup=specialists_kb(specialists))
    await state.set_state(ReviewFSM.CHOOSE_SPEC)

@router.callback_query(ReviewFSM.CHOOSE_SPEC, F.data.startswith("spec_"))
async def input_review_text(call: CallbackQuery, state: FSMContext):
    spec_id = int(call.data.split("_")[1])
    await state.update_data(spec_id=spec_id)
    await call.message.edit_text("Оставьте свой отзыв текстом:")
    await state.set_state(ReviewFSM.INPUT_TEXT)

@router.message(ReviewFSM.INPUT_TEXT)
async def input_review_stars(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await msg.answer("Оцените специалиста от 1 до 5 (напишите число):")
    await state.set_state(ReviewFSM.INPUT_STARS)

@router.message(ReviewFSM.INPUT_STARS)
async def save_review(msg: Message, state: FSMContext):
    if not msg.text.isdigit() or not (1 <= int(msg.text) <= 5):
        await msg.answer("Введите число от 1 до 5:")
        return
    stars = int(msg.text)
    data = await state.get_data()
    await ReviewService.add(msg.from_user.id, data["spec_id"], data["text"], stars)
    await msg.answer(REVIEW_THANKS, reply_markup=main_menu())
    await state.clear()