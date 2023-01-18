import aiosqlite
from datetime import datetime


async def create_table():
    async with aiosqlite.connect('candle.db') as db:
        await db.execute(
            'CREATE TABLE IF NOT EXISTS requests '
            '(date text, url text, user text)')
        await db.commit()

async def save_to_db(url, user):
    async with aiosqlite.connect('candle.db') as db:
        await db.execute(
            'INSERT INTO requests VALUES (?, ?, ?)',
            (datetime.now(), url, user))
        await db.commit()

        
