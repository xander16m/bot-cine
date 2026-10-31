from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import TMDB_API_KEY, DEFAULT_COUNTRY
from services.tmdb import (
    search_movie,
    get_movie_details,
    search_tv,
    get_tv_details,
    parse_media_info
)

router = Router()

def build_media_caption(info: dict) -> str:
    icon = "🎬" if info["media_type"] == "movie" else "📺"
    orig = f" _({info['original_title']})_" if info['original_title'] and info['original_title'] != info['title'] else ""
    
    # Plataformas streaming
    if info["streaming"]:
        streaming_text = "🔹 " + ", ".join(info["streaming"])
    else:
        streaming_text = "🚫 No disponible en suscripción (o solo alquiler/compra)."

    caption = (
        f"{icon} *{info['title']}* ({info['year']}){orig}\n"
        f"⭐ *Nota:* {info['rating']}  |  ⏳ {info['duration']}\n"
        f"🎭 *Géneros:* {info['genres']}\n\n"
        f"📝 *Sinopsis:*\n{info['overview']}\n\n"
        f"📡 *¿Dónde ver? ({info['country']}):*\n{streaming_text}"
    )
    return caption

def build_media_keyboard(info: dict) -> InlineKeyboardMarkup:
    buttons = []
    row1 = []
    
    # Botón de Tráiler
    if info.get("trailer_url"):
        row1.append(InlineKeyboardButton(text="▶️ Ver Tráiler", url=info["trailer_url"]))
    
    # Botón Guardar en la Watchlist
    row1.append(InlineKeyboardButton(
        text="📌 Guardar en Lista",
        callback_data=f"save:{info['media_type']}:{info['id']}"
    ))
    
    buttons.append(row1)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(Command("peli", "pelicula"))
async def cmd_movie(message: Message):
    if not TMDB_API_KEY:
        await message.answer("⚠️ Falta configurar la `TMDB_API_KEY` en el archivo `.env`.")
        return

    query = message.text.partition(" ")[2].strip()
    if not query:
        await message.answer("ℹ️ Indica el nombre de la película. Ejemplo:\n`/peli El Padrino`", parse_mode="Markdown")
        return

    # Buscar película
    result = await search_movie(query)
    if not result:
        await message.answer(f"❌ No encontré ninguna película con el nombre *'{query}'*.", parse_mode="Markdown")
        return

    # Obtener detalles completos
    details = await get_movie_details(result["id"], country=DEFAULT_COUNTRY)
    if not details:
        await message.answer("❌ Hubo un error al obtener la información de la película.")
        return

    info = parse_media_info(details, media_type="movie", country=DEFAULT_COUNTRY)
    caption = build_media_caption(info)
    keyboard = build_media_keyboard(info)

    if info.get("poster_url"):
        try:
            await message.answer_photo(
                photo=info["poster_url"],
                caption=caption,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return
        except Exception:
            pass  # Si falla la carga de imagen por Telegram, enviar mensaje de texto

    await message.answer(caption, reply_markup=keyboard, parse_mode="Markdown")

@router.message(Command("serie"))
async def cmd_serie(message: Message):
    if not TMDB_API_KEY:
        await message.answer("⚠️ Falta configurar la `TMDB_API_KEY` en el archivo `.env`.")
        return

    query = message.text.partition(" ")[2].strip()
    if not query:
        await message.answer("ℹ️ Indica el nombre de la serie. Ejemplo:\n`/serie Succession`", parse_mode="Markdown")
        return

    result = await search_tv(query)
    if not result:
        await message.answer(f"❌ No encontré ninguna serie con el nombre *'{query}'*.", parse_mode="Markdown")
        return

    details = await get_tv_details(result["id"], country=DEFAULT_COUNTRY)
    if not details:
        await message.answer("❌ Hubo un error al obtener la información de la serie.")
        return

    info = parse_media_info(details, media_type="tv", country=DEFAULT_COUNTRY)
    caption = build_media_caption(info)
    keyboard = build_media_keyboard(info)

    if info.get("poster_url"):
        try:
            await message.answer_photo(
                photo=info["poster_url"],
                caption=caption,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return
        except Exception:
            pass

    await message.answer(caption, reply_markup=keyboard, parse_mode="Markdown")

