import aiosqlite
from core.settings import settings

async def init_db():
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS specialists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar TEXT,
            bio TEXT
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            specialist_id INTEGER,
            name TEXT NOT NULL,
            duration INTEGER,
            price INTEGER,
            emoji TEXT,
            FOREIGN KEY (specialist_id) REFERENCES specialists(id)
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            specialist_id INTEGER,
            service_id INTEGER,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'booked'
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            specialist_id INTEGER,
            text TEXT,
            stars INTEGER,
            created TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.commit()

        # Seed test specialists and services if empty
        cursor = await db.execute("SELECT COUNT(*) FROM specialists")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.execute(
                "INSERT INTO specialists (name, avatar, bio) VALUES (?, ?, ?)",
                ("Ирина", "💇‍♀️", "Парикмахер высшей категории. Люблю создавать красоту!"),
            )
            await db.execute(
                "INSERT INTO specialists (name, avatar, bio) VALUES (?, ?, ?)",
                ("Мария", "💆‍♀️", "Опытный мастер по уходу за волосами."),
            )
            await db.execute(
                "INSERT INTO specialists (name, avatar, bio) VALUES (?, ?, ?)",
                ("Ольга", "💄", "Стилист-колорист. Мои прически — ваше настроение!"),
            )
            await db.executemany(
                "INSERT INTO services (specialist_id, name, duration, price, emoji) VALUES (?, ?, ?, ?, ?)",
                [
                    (1, "Стрижка женская", 40, 1500, "✂️"),
                    (1, "Укладка волос", 30, 1000, "💁‍♀️"),
                    (1, "Окрашивание", 90, 3500, "🎨"),
                    (2, "Массаж головы", 20, 700, "🤲"),
                    (2, "Лечение волос", 45, 2000, "🧴"),
                    (3, "Вечерняя укладка", 60, 2500, "🌟"),
                    (3, "Окрашивание прядей", 55, 1800, "🖌️"),
                ]
            )
            await db.commit()

async def optimize_db():
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute("CREATE INDEX IF NOT EXISTS idx_specialists_name ON specialists(name);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_bookings_date_time ON bookings(date, time);")
        await db.commit()

async def seed_test_data():
    async with aiosqlite.connect(settings.db_file) as db:
        await db.execute("INSERT INTO bookings (user_id, specialist_id, service_id, date, time, status) VALUES (1, 1, 1, '2025-06-10', '10:00', 'booked');")
        await db.execute("INSERT INTO reviews (user_id, specialist_id, text, stars) VALUES (1, 1, 'Отлично!', 5);")
        await db.commit()