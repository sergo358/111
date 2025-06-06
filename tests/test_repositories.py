import asyncio
import pytest

from db.init_db import init_db
from db.repositories import (
    get_all_specialists,
    get_specialist,
    get_services_for_specialist,
    create_booking,
    get_user_bookings,
    cancel_booking,
    add_review,
    get_reviews_for_specialist,
)

@pytest.mark.asyncio
async def test_specialists_and_services():
    await init_db()
    specs = await get_all_specialists()
    assert len(specs) >= 1
    spec_id = specs[0]['id']
    one = await get_specialist(spec_id)
    assert one['id'] == spec_id
    services = await get_services_for_specialist(spec_id)
    assert isinstance(services, list)

@pytest.mark.asyncio
async def test_booking_cycle():
    await init_db()
    user_id = 9999
    spec_id = 1
    service_id = 1
    date = "2025-06-10"
    time = "13:00"
    ok = await create_booking(user_id, spec_id, service_id, date, time)
    assert ok
    bookings = await get_user_bookings(user_id)
    assert any(b['date'] == date and b['time'] == time for b in bookings)
    for b in bookings:
        await cancel_booking(b['id'])
    bookings2 = await get_user_bookings(user_id)
    assert all(b['status'] == "cancelled" for b in bookings2)

@pytest.mark.asyncio
async def test_reviews():
    await init_db()
    user_id = 1111
    spec_id = 1
    text = "Отличный мастер!"
    stars = 5
    ok = await add_review(user_id, spec_id, text, stars)
    assert ok
    reviews = await get_reviews_for_specialist(spec_id)
    assert any(r['text'] == text for r in reviews)