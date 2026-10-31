import aiosqlite
from typing import Optional, List, Dict, Any
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                media_type TEXT NOT NULL, -- 'movie' o 'tv'
                tmdb_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                year TEXT,
                poster_path TEXT,
                added_by TEXT NOT NULL,
                watched INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, media_type, tmdb_id)
            )
        """)
        await db.commit()

async def add_to_watchlist(
    chat_id: int,
    media_type: str,
    tmdb_id: int,
    title: str,
    year: Optional[str],
    poster_path: Optional[str],
    added_by: str
) -> bool:
    """Añade un elemento a la lista. Devuelve True si se añadió, False si ya existía."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
                INSERT INTO watchlist (chat_id, media_type, tmdb_id, title, year, poster_path, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (chat_id, media_type, tmdb_id, title, year, poster_path, added_by)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def get_watchlist(chat_id: int, only_pending: bool = True, limit: int = 15) -> List[Dict[str, Any]]:
    """Obtiene la lista de películas/series del grupo."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM watchlist WHERE chat_id = ?"
        params = [chat_id]
        if only_pending:
            query += " AND watched = 0"
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def mark_watched(chat_id: int, item_id: int) -> bool:
    """Marca un elemento como visto."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE watchlist SET watched = 1 WHERE chat_id = ? AND id = ?",
            (chat_id, item_id)
        )
        await db.commit()
        return cursor.rowcount > 0

async def get_random_item(chat_id: int) -> Optional[Dict[str, Any]]:
    """Elige una recomendación pendiente al azar para el grupo."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM watchlist WHERE chat_id = ? AND watched = 0 ORDER BY RANDOM() LIMIT 1",
            (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

