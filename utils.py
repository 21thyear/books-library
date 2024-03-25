from database import cursor
from typing import List, Tuple
import asyncio

async def get_genres() -> List[str]:
    cursor.execute("SELECT name FROM genres")
    rows = cursor.fetchall()

    return [row[0] for row in rows]