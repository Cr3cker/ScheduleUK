import aiosqlite
from datetime import datetime


async def create_table():
    '''Create a table to store requests if it doesn't exist'''

    async with aiosqlite.connect('candle.db') as db:
        await db.execute(
            'CREATE TABLE IF NOT EXISTS requests '
            '(date text, url text, user text)')
        await db.commit()

async def save_to_db(url, user):
    '''Save request to database'''

    async with aiosqlite.connect('candle.db') as db:
        await db.execute(
            'INSERT INTO requests VALUES (?, ?, ?)',
            (datetime.now(), url, user))
        await db.commit()


