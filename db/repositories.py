import aiosqlite
from core.settings import settings
from core.logging import log_database_query

# Specialists
async def get_all_specialists():
    async with aiosqlite.connect(settings.db_file) as db:
        cursor = await db.execute("SELECT id, name, avatar, bio FROM specialists")
        rows = await cursor.fetchall()
        return [
            {"id": row[0], "name": row[1], "avatar": row[2], "bio": row[3]} for row in rows
        ]

async def get_specialist(spec_id):
    async with aiosqlite.connect(settings.db_file) as db:
        cursor = await db.execute(
            "SELECT id, name, avatar, bio FROM specialists WHERE id = ?", (spec_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "avatar": row[2], "bio": row[3]}
        return None

# Services
async def get_services_for_specialist(spec_id):
    async with aiosqlite.connect(settings.db_file) as db:
        cursor = await db.execute(
            "SELECT id, name, duration, price, emoji FROM services WHERE specialist_id = ?", (spec_id,)
        )
        rows = await cursor.fetchall()
        return [
            {"id": row[0], "name": row[1], "duration": row[2], "price": row[3], "emoji": row[4]}
            for row in rows
        ]

# Bookings
async def create_booking(user_id, specialist_id, service_id, date, time):
    query = "INSERT INTO bookings (user_id, specialist_id, service_id, date, time) VALUES (?, ?, ?, ?, ?)"
    log_database_query(query)
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute(query, (user_id, specialist_id, service_id, date, time))
        await db.commit()
        return True

async def get_user_bookings(user_id):
    async with aiosqlite.connect(settings.db_file) as db:
        cursor = await db.execute(
            """
            SELECT bookings.id, specialists.name, services.name, bookings.date, bookings.time, bookings.status
            FROM bookings
            JOIN specialists ON bookings.specialist_id = specialists.id
            JOIN services ON bookings.service_id = services.id
            WHERE bookings.user_id = ?
            ORDER BY bookings.date, bookings.time
            """,
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": row[0],
                "specialist": row[1],
                "service": row[2],
                "date": row[3],
                "time": row[4],
                "status": row[5],
            }
            for row in rows
        ]

async def cancel_booking(booking_id):
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,)
        )
        await db.commit()
        return True

# Reviews
async def add_review(user_id, specialist_id, text, stars):
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute(
            "INSERT INTO reviews (user_id, specialist_id, text, stars) VALUES (?, ?, ?, ?)",
            (user_id, specialist_id, text, stars),
        )
        await db.commit()
        return True

async def get_reviews_for_specialist(spec_id):
    async with aiosqlite.connect(settings.db_file) as db:
        cursor = await db.execute(
            """
            SELECT text, stars, created FROM reviews WHERE specialist_id = ?
            ORDER BY created DESC LIMIT 10
            """,
            (spec_id,),
        )
        rows = await cursor.fetchall()
        return [
            {"text": row[0], "stars": row[1], "created": row[2]}
            for row in rows
        ]