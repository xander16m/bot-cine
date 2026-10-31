from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "🎬 *¡Bienvenido al Bot de Cine y Series!* 🍿\n\n"
        "Estoy diseñado para ayudar a grupos cinéfilos y seriéfilos.\n\n"
        "📌 *Comandos principales:*\n"
        "▫️ `/peli <nombre>` — Busca información, nota, tráiler y dónde ver una película.\n"
        "▫️ `/serie <nombre>` — Busca información y plataformas de una serie.\n"
        "▫️ `/guardar <nombre>` — Guarda un título en la lista comunitaria.\n"
        "▫️ `/lista` — Muestra la lista de recomendaciones pendientes del grupo.\n"
        "▫️ `/azar` — ¿Indecisos? Elige una película pendiente al azar.\n"
        "▫️ `/visto <número>` — Marca una recomendación como ya vista.\n\n"
        "💡 *Consejo:* Puedes pulsar el botón *'📌 Guardar'* en cualquier ficha para añadirla a la lista del grupo automáticamente."
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("help", "ayuda"))
async def cmd_help(message: Message):
    text = (
        "🍿 *Guía de Comandos Rápidos:*\n\n"
        "🎬 *Buscar Películas:* `/peli Inception`\n"
        "📺 *Buscar Series:* `/serie Breaking Bad`\n"
        "📌 *Ver Lista del Grupo:* `/lista`\n"
        "🎲 *Película al Azar:* `/azar`\n"
        "✅ *Marcar como Vista:* `/visto 3` (usa el número de ID de `/lista`)\n"
    )
    await message.answer(text, parse_mode="Markdown")

