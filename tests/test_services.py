import pytest
from services.booking_service import BookingService
from services.review_service import ReviewService

@pytest.mark.asyncio
async def test_booking_service():
    ok = await BookingService.book(42, 1, 1, "2025-06-11", "15:00")
    assert ok
    bookings = await BookingService.list_user_bookings(42)
    assert any(b['date'] == "2025-06-11" and b['time'] == "15:00" for b in bookings)
    # Test cancel
    for b in bookings:
        await BookingService.cancel(b['id'])
    bookings2 = await BookingService.list_user_bookings(42)
    assert all(b['status'] == "cancelled" for b in bookings2)

@pytest.mark.asyncio
async def test_review_service():
    ok = await ReviewService.add(43, 1, "Очень понравилось!", 5)
    assert ok
    reviews = await ReviewService.list_for_specialist(1)
    assert any(r['text'] == "Очень понравилось!" for r in reviews)

@pytest.mark.asyncio
async def test_booking_service_edge_cases():
    # Тесты для граничных случаев
    ok = await BookingService.book(9999, 9999, 9999, "2025-06-11", "15:00")
    assert not ok  # Ожидаем, что запись не будет создана