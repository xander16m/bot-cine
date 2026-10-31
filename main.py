import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, TMDB_API_KEY
from database import init_db
from handlers import general, media, watchlist

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="🍿 CinefiloBot esta activo y funcionando 24/7!")

async def start_web_server(port: int):
    """Servidor web minimo para que plataformas en la nube (como Render) mantengan el bot activo."""
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Servidor web de salud iniciado en el puerto {port}")

async def main():
    # Validar token
    if not BOT_TOKEN or BOT_TOKEN == "tu_token_de_telegram_aqui":
        logger.error(
            "\n" + "="*60 + "\n"
            "❌ ERROR: BOT_TOKEN no configurado.\n"
            "1. Abre Telegram y busca a @BotFather.\n"
            "2. Envía /newbot y sigue los pasos para obtener tu Token.\n"
            "3. Crea un archivo .env copiando .env.example y pega tu token ahí.\n"
            + "="*60
        )
        sys.exit(1)

    if not TMDB_API_KEY or TMDB_API_KEY == "tu_api_key_de_tmdb_aqui":
        logger.warning(
            "\n" + "="*60 + "\n"
            "⚠️ ADVERTENCIA: TMDB_API_KEY no configurada.\n"
            "El bot no podrá buscar películas ni plataformas de streaming.\n"
            "Consigue una clave gratuita en: https://www.themoviedb.org/settings/api\n"
            "Y añádela a tu archivo .env.\n"
            + "="*60
        )

    # Inicializar base de datos
    logger.info("Inicializando base de datos SQLite...")
    await init_db()

    # Si estamos en un hosting como Render, inicia el servidor web de salud
    port_env = os.getenv("PORT")
    if port_env:
        try:
            await start_web_server(int(port_env))
        except Exception as e:
            logger.warning(f"No se pudo iniciar el servidor web: {e}")

    # Inicializar Bot y Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Registrar rutas
    dp.include_router(general.router)
    dp.include_router(media.router)
    dp.include_router(watchlist.router)

    logger.info("Bot iniciado y escuchando mensajes...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot detenido.")


