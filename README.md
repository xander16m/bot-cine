# 🎬 Bot de Telegram: CinefiloBot (Series y Películas)

Un bot de Telegram completo y pensado para grupos donde se habla de cine y series.

## 🚀 Funcionalidades

1. **Ficha de Película (`/peli <nombre>`)**:
   - Cartel oficial en alta resolución.
   - Puntuación (⭐/10), duración, año y géneros.
   - Sinopsis en español.
   - **Plataformas de streaming** disponibles en tu país (Netflix, Prime Video, Max, Disney+, etc. gracias a JustWatch).
   - Botón directo para reproducir el **Tráiler oficial de YouTube**.
   - Botón directo para añadir a la lista de pendientes del grupo.

2. **Ficha de Serie (`/serie <nombre>`)**:
   - Todo lo anterior adaptado a series: temporadas, episodios emitidos y plataformas donde verla.

3. **Lista comunitaria del grupo ("Watchlist")**:
   - `/guardar <nombre>` o botón **"📌 Guardar en Lista"**: Añade la recomendación a la base de datos del grupo.
   - `/lista`: Muestra los títulos pendientes que el grupo aún tiene por ver y quién los recomendó.
   - `/visto <número>`: Marca la película/serie como vista.

4. **Ruleta "¿Qué vemos hoy?" (`/azar`)**:
   - Selecciona aleatoriamente una película pendiente de la lista del grupo para resolver las discusiones de indecisión.

---

## 🛠️ Configuración (Paso a Paso)

Solo necesitas 2 claves gratuitas:

### Paso 1: Obtener el Token de Telegram (1 minuto)
1. Abre Telegram y busca al bot oficial: `@BotFather`.
2. Escribe `/newbot`.
3. Dale un nombre a tu bot (ejemplo: `Mi Grupo Cine Bot`) y luego un nombre de usuario terminado en `bot` (ejemplo: `cinefilo_grupo_bot`).
4. `@BotFather` te dará un **Token HTTP API** (parecido a `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
5. Copia ese token.

> **Importante para Grupos:** En `@BotFather`, envía `/setprivacy`, selecciona tu bot y ponlo en `Disable` (Desactivado). Esto permite que el bot lea los comandos `/peli`, `/serie`, etc., cuando los miembros del grupo escriban.

---

### Paso 2: Obtener la API Key de TMDb (2 minutos, Gratis)
1. Entra en [The Movie Database (TMDb)](https://www.themoviedb.org/signup) y créate una cuenta gratuita.
2. Ve a tu perfil -> **Configuración** -> **API** (o entra directo a [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)).
3. Solicita una clave de API (elige tipo "Personal").
4. Copia tu **API Key (v3 auth)**.

---

### Paso 3: Configurar el archivo `.env`
Copia el archivo `.env.example` y renómbralo a `.env` (o edítalo directamente):

```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
TMDB_API_KEY=tu_api_key_de_tmdb
DEFAULT_COUNTRY=ES
LANGUAGE=es-ES
```

*Nota para `DEFAULT_COUNTRY`:*
- `ES` = España
- `MX` = México
- `AR` = Argentina
- `CO` = Colombia
- `CL` = Chile
- `US` = Estados Unidos

---

## ▶️ Cómo Iniciar el Bot

Simplemente haz doble clic en el archivo:
```text
iniciar_bot.bat
```

O desde la terminal:
```bash
.\.venv\Scripts\python main.py
```

