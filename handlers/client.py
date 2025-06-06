from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup

from utils.texts import (
    WELCOME,
    SELECT_SPECIALIST,
    SELECT_SERVICE,
    SELECT_DATE,
    SELECT_TIME,
    CONFIRM_BOOKING,
    BOOKING_SUCCESS,
    BOOKING_CANCELLED,
    NO_BOOKINGS,
    YOUR_BOOKINGS,
)
from services.specialist_service import SpecialistService
from services.booking_service import BookingService
from keyboards.client import (
    main_menu,
    specialists_kb,
    services_kb,
    dates_kb,
    times_kb,
    confirm_kb,
)

import datetime

router = Router(name=__name__)

# --- FSM States ---
class BookingFSM(StatesGroup):
    SELECT_SPECIALIST = State()
    SELECT_SERVICE = State()
    SELECT_DATE = State()
    SELECT_TIME = State()
    CONFIRM = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if not message.from_user or not message.from_user.id:
        await message.answer("Ошибка: пользователь не найден.")
        return
    await message.answer(WELCOME, reply_markup=main_menu())
    await state.clear()

@router.callback_query(F.data == "book")
async def choose_specialist(call: CallbackQuery, state: FSMContext):
    if not call.from_user or not call.from_user.id:
        await call.message.edit_text("Ошибка: пользователь не найден.")
        return
    specialists = await SpecialistService.list_specialists()
    await call.message.edit_text(SELECT_SPECIALIST, reply_markup=specialists_kb(specialists))
    await state.set_state(BookingFSM.SELECT_SPECIALIST)

@router.callback_query(BookingFSM.SELECT_SPECIALIST, F.data.startswith("spec_"))
async def choose_service(call: CallbackQuery, state: FSMContext):
    spec_id = int(call.data.split("_")[1])
    await state.update_data(spec_id=spec_id)
    services = await SpecialistService.list_services(spec_id)
    await call.message.edit_text(SELECT_SERVICE, reply_markup=services_kb(services))
    await state.set_state(BookingFSM.SELECT_SERVICE)

@router.callback_query(BookingFSM.SELECT_SERVICE, F.data.startswith("svc_"))
async def choose_date(call: CallbackQuery, state: FSMContext):
    svc_id = int(call.data.split("_")[1])
    await state.update_data(svc_id=svc_id)
    # For demo: next 5 days
    dates = [
        (datetime.date.today() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(5)
    ]
    await call.message.edit_text(SELECT_DATE, reply_markup=dates_kb(dates))
    await state.set_state(BookingFSM.SELECT_DATE)

@router.callback_query(BookingFSM.SELECT_DATE, F.data.startswith("date_"))
async def choose_time(call: CallbackQuery, state: FSMContext):
    date = call.data.split("_", 1)[1]
    await state.update_data(date=date)
    # For demo: fixed times
    times = ["10:00", "11:30", "13:00", "14:30", "16:00", "17:30"]
    await call.message.edit_text(SELECT_TIME, reply_markup=times_kb(times))
    await state.set_state(BookingFSM.SELECT_TIME)

@router.callback_query(BookingFSM.SELECT_TIME, F.data.startswith("time_"))
async def confirm_booking(call: CallbackQuery, state: FSMContext):
    time = call.data.split("_", 1)[1]
    await state.update_data(time=time)
    data = await state.get_data()
    spec_id = data["spec_id"]
    svc_id = data["svc_id"]
    spec = await SpecialistService.get_specialist(spec_id)
    services = await SpecialistService.list_services(spec_id)
    service = next(s for s in services if s["id"] == svc_id)
    text = (
        f"{CONFIRM_BOOKING}\n\n"
        f"{spec['avatar']} <b>{spec['name']}</b>\n"
        f"{service['emoji']} <b>{service['name']}</b> — {service['price']}₽\n"
        f"🗓 {data['date']} ⏰ {data['time']}"
    )
    await call.message.edit_text(text, reply_markup=confirm_kb())
    await state.set_state(BookingFSM.CONFIRM)

@router.callback_query(BookingFSM.CONFIRM, F.data == "confirm")
async def finish_booking(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await BookingService.book(
        user_id=call.from_user.id,
        specialist_id=data["spec_id"],
        service_id=data["svc_id"],
        date=data["date"],
        time=data["time"],
    )
    await call.message.edit_text(BOOKING_SUCCESS, reply_markup=main_menu())
    await state.clear()

@router.callback_query(BookingFSM.CONFIRM, F.data == "cancel")
async def cancel_booking(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(BOOKING_CANCELLED, reply_markup=main_menu())
    await state.clear()

@router.callback_query(F.data == "my_bookings")
async def my_bookings(call: CallbackQuery):
    bookings = await BookingService.list_user_bookings(call.from_user.id)
    if not bookings:
        await call.message.edit_text(NO_BOOKINGS, reply_markup=main_menu())
        return
    text = f"{YOUR_BOOKINGS}\n\n"
    for b in bookings:
        text += f"🗓 {b['date']} {b['time']} — <b>{b['service']}</b> у {b['specialist']} [{b['status']}]\n"
    await call.message.edit_text(text, reply_markup=main_menu())