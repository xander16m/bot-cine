from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from services.tmdb import get_movie_details, get_tv_details, search_movie
from database import add_to_watchlist, get_watchlist, mark_watched, get_random_item

router = Router()

@router.callback_query(F.data.startswith("save:"))
async def cb_save_media(callback: CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("Datos inválidos.", show_alert=True)
        return

    media_type, tmdb_id_str = parts[1], parts[2]
    try:
        tmdb_id = int(tmdb_id_str)
    except ValueError:
        return

    # Obtener info básica para la base de datos
    if media_type == "movie":
        details = await get_movie_details(tmdb_id)
        title = details.get("title") if details else f"Película #{tmdb_id}"
        date_str = details.get("release_date") if details else ""
    else:
        details = await get_tv_details(tmdb_id)
        title = details.get("name") if details else f"Serie #{tmdb_id}"
        date_str = details.get("first_air_date") if details else ""

    year = date_str[:4] if date_str and len(date_str) >= 4 else "N/A"
    poster_path = details.get("poster_path") if details else None
    
    user = callback.from_user
    user_name = f"@{user.username}" if user.username else user.first_name

    added = await add_to_watchlist(
        chat_id=callback.message.chat.id,
        media_type=media_type,
        tmdb_id=tmdb_id,
        title=title,
        year=year,
        poster_path=poster_path,
        added_by=user_name
    )

    if added:
        await callback.answer("✅ ¡Guardada en la lista del grupo!", show_alert=False)
        await callback.message.reply(
            f"📌 *{user_name}* añadió *{title}* ({year}) a la lista de pendientes del grupo.",
            parse_mode="Markdown"
        )
    else:
        await callback.answer("ℹ️ Ya estaba guardada en la lista del grupo.", show_alert=True)

@router.message(Command("guardar"))
async def cmd_guardar(message: Message):
    query = message.text.partition(" ")[2].strip()
    if not query:
        await message.answer("ℹ️ Escribe el nombre de lo que quieres guardar. Ejemplo:\n`/guardar Interestelar`", parse_mode="Markdown")
        return

    result = await search_movie(query)
    if not result:
        await message.answer(f"❌ No encontré ningún título para *'{query}'*.", parse_mode="Markdown")
        return

    user = message.from_user
    user_name = f"@{user.username}" if user.username else user.first_name
    title = result.get("title", query)
    date_str = result.get("release_date", "")
    year = date_str[:4] if date_str and len(date_str) >= 4 else "N/A"

    added = await add_to_watchlist(
        chat_id=message.chat.id,
        media_type="movie",
        tmdb_id=result["id"],
        title=title,
        year=year,
        poster_path=result.get("poster_path"),
        added_by=user_name
    )

    if added:
        await message.answer(
            f"✅ *{title}* ({year}) ha sido guardada en la lista de pendientes.",
            parse_mode="Markdown"
        )
    else:
        await message.answer(f"ℹ️ *{title}* ya estaba en la lista de pendientes.", parse_mode="Markdown")

@router.message(Command("lista", "pendientes"))
async def cmd_lista(message: Message):
    items = await get_watchlist(message.chat.id, only_pending=True, limit=20)
    if not items:
        await message.answer(
            "📭 *La lista del grupo está vacía.*\n\n"
            "Guarda recomendaciones con `/guardar <nombre>` o usando el botón en las fichas `/peli` o `/serie`.",
            parse_mode="Markdown"
        )
        return

    text = "📋 *Lista de películas y series pendientes:*\n\n"
    for item in items:
        icon = "🎬" if item["media_type"] == "movie" else "📺"
        text += f"`#{item['id']}` {icon} *{item['title']}* ({item['year']}) — _por {item['added_by']}_\n"

    text += "\n💡 *Comandos útiles:*\n"
    text += "▫️ `/visto <número>` para marcar como vista (ej. `/visto 1`)\n"
    text += "▫️ `/azar` para que el bot elija una al azar para ver hoy."

    await message.answer(text, parse_mode="Markdown")

@router.message(Command("visto", "vista"))
async def cmd_visto(message: Message):
    arg = message.text.partition(" ")[2].strip()
    if not arg or not arg.isdigit():
        await message.answer("ℹ️ Indica el número de la lista. Ejemplo: `/visto 2`", parse_mode="Markdown")
        return

    item_id = int(arg)
    ok = await mark_watched(message.chat.id, item_id)
    if ok:
        await message.answer(f"🎉 ¡Marcada como vista la recomendación `#{item_id}`! Buen provecho 🍿", parse_mode="Markdown")
    else:
        await message.answer(f"❌ No se encontró ningún elemento pendiente con el ID `#{item_id}` en este chat.", parse_mode="Markdown")

@router.message(Command("azar", "random"))
async def cmd_random(message: Message):
    item = await get_random_item(message.chat.id)
    if not item:
        await message.answer(
            "📭 No hay películas ni series pendientes en la lista del grupo.\n"
            "¡Añade algunas primero usando `/peli` o `/guardar`!",
            parse_mode="Markdown"
        )
        return

    icon = "🎬" if item["media_type"] == "movie" else "📺"
    text = (
        "🎲 *¡La ruleta ha hablado!*\n\n"
        f"Hoy toca ver:\n"
        f"{icon} *{item['title']}* ({item['year']})\n"
        f"👤 Recomendada por: {item['added_by']}\n\n"
        f"👉 Puedes consultar detalles con: `/{'peli' if item['media_type'] == 'movie' else 'serie'} {item['title']}`"
    )
    await message.answer(text, parse_mode="Markdown")

