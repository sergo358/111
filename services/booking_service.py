from db.repositories import (
    create_booking,
    get_user_bookings,
    cancel_booking,
)

class BookingService:
    @staticmethod
    async def book(user_id, specialist_id, service_id, date, time):
        return await create_booking(user_id, specialist_id, service_id, date, time)

    @staticmethod
    async def list_user_bookings(user_id):
        return await get_user_bookings(user_id)

    @staticmethod
    async def cancel(booking_id):
        return await cancel_booking(booking_id)