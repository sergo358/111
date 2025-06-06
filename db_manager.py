# db_manager.py
# Модуль работы с SQLite для тестовой базы специалистов и услуг

import aiosqlite
import os

DB_FILE = "telezapis.db"

# --- Инициализация тестовой базы ---
async def init_test_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE specialists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar TEXT,
            bio TEXT
        );
        """)
        await db.execute("""
        CREATE TABLE services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            specialist_id INTEGER,
            name TEXT NOT NULL,
            duration INTEGER, -- мин
            price INTEGER,    -- руб
            emoji TEXT,
            FOREIGN KEY (specialist_id) REFERENCES specialists(id)
        );
        """)
        # Добавим тестовых специалистов
        specialists = [
            ("Ирина", "💇‍♀️", "Парикмахер высшей категории. Люблю создавать красоту!"),
            ("Мария", "💆‍♀️", "Опытный мастер по уходу за волосами. Всегда рада видеть новых клиентов!"),
            ("Ольга", "💄", "Стилист-колорист. Мои прически — ваше настроение!"),
        ]
        for name, avatar, bio in specialists:
            await db.execute(
                "INSERT INTO specialists (name, avatar, bio) VALUES (?, ?, ?)",
                (name, avatar, bio)
            )
        # Добавим тестовые услуги для каждого специалиста
        services = [
            (1, "Стрижка женская", 40, 1500, "✂️"),
            (1, "Укладка волос", 30, 1000, "💁‍♀️"),
            (1, "Окрашивание", 90, 3500, "🎨"),
            (2, "Массаж головы", 20, 700, "🤲"),
            (2, "Лечение волос", 45, 2000, "🧴"),
            (3, "Вечерняя укладка", 60, 2500, "🌟"),
            (3, "Окрашивание прядей", 55, 1800, "🖌️"),
        ]
        for specialist_id, name, duration, price, emoji in services:
            await db.execute(
                "INSERT INTO services (specialist_id, name, duration, price, emoji) VALUES (?, ?, ?, ?, ?)",
                (specialist_id, name, duration, price, emoji)
            )
        await db.commit()

# --- Запросы для получения специалистов и услуг ---
async def get_all_specialists():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT id, name, avatar, bio FROM specialists")
        rows = await cursor.fetchall()
        return [
            {"id": row[0], "name": row[1], "avatar": row[2], "bio": row[3]}
            for row in rows
        ]

async def get_services_by_specialist(specialist_id):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT id, name, duration, price, emoji FROM services WHERE specialist_id = ?",
            (specialist_id,)
        )
        rows = await cursor.fetchall()
        return [
            {"id": row[0], "name": row[1], "duration": row[2], "price": row[3], "emoji": row[4]}
            for row in rows
        ]

# --- Получение информации о специалисте по id ---
async def get_specialist_by_id(specialist_id):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT id, name, avatar, bio FROM specialists WHERE id = ?",
            (specialist_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "avatar": row[2], "bio": row[3]}
        return None

# --- Получение информации об услуге по id ---
async def get_service_by_id(service_id):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT id, specialist_id, name, duration, price, emoji FROM services WHERE id = ?",
            (service_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "specialist_id": row[1],
                "name": row[2],
                "duration": row[3],
                "price": row[4],
                "emoji": row[5]
            }
        return None