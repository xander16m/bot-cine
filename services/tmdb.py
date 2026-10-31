import httpx
from typing import Optional, Dict, Any, List
from config import TMDB_API_KEY, LANGUAGE, DEFAULT_COUNTRY

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def _get_auth():
    """Genera parámetros o cabeceras según el tipo de clave de TMDb."""
    if not TMDB_API_KEY:
        return {}, {}
    # Si la clave tiene más de 40 caracteres, probablemente sea un Read Access Token (v4)
    if len(TMDB_API_KEY) > 40:
        return {}, {"Authorization": f"Bearer {TMDB_API_KEY}"}
    return {"api_key": TMDB_API_KEY}, {}

async def search_movie(query: str) -> Optional[Dict[str, Any]]:
    """Busca una película por título y devuelve el primer resultado relevante."""
    params, headers = _get_auth()
    params.update({
        "query": query,
        "language": LANGUAGE,
        "include_adult": "false",
        "page": 1
    })

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/search/movie", params=params, headers=headers, timeout=10.0)
            data = resp.json()
            results = data.get("results", [])
            if results:
                return results[0]
            return None
        except Exception as e:
            print(f"Error buscando película: {e}")
            return None

async def get_movie_details(movie_id: int, country: str = DEFAULT_COUNTRY) -> Optional[Dict[str, Any]]:
    """Obtiene ficha detallada con trailer y proveedores de streaming."""
    params, headers = _get_auth()
    params.update({
        "language": LANGUAGE,
        "append_to_response": "videos,watch/providers"
    })

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/movie/{movie_id}", params=params, headers=headers, timeout=10.0)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception as e:
            print(f"Error obteniendo detalles de película: {e}")
            return None

async def search_tv(query: str) -> Optional[Dict[str, Any]]:
    """Busca una serie por título y devuelve el primer resultado relevante."""
    params, headers = _get_auth()
    params.update({
        "query": query,
        "language": LANGUAGE,
        "include_adult": "false",
        "page": 1
    })

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/search/tv", params=params, headers=headers, timeout=10.0)
            data = resp.json()
            results = data.get("results", [])
            if results:
                return results[0]
            return None
        except Exception as e:
            print(f"Error buscando serie: {e}")
            return None

async def get_tv_details(tv_id: int, country: str = DEFAULT_COUNTRY) -> Optional[Dict[str, Any]]:
    """Obtiene ficha detallada de una serie con trailer y proveedores de streaming."""
    params, headers = _get_auth()
    params.update({
        "language": LANGUAGE,
        "append_to_response": "videos,watch/providers"
    })

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/tv/{tv_id}", params=params, headers=headers, timeout=10.0)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception as e:
            print(f"Error obteniendo detalles de serie: {e}")
            return None

def parse_media_info(data: Dict[str, Any], media_type: str = "movie", country: str = DEFAULT_COUNTRY) -> Dict[str, Any]:
    """Parsea la respuesta de TMDb para formatear el mensaje de Telegram."""
    is_movie = (media_type == "movie")

    title = data.get("title") if is_movie else data.get("name")
    orig_title = data.get("original_title") if is_movie else data.get("original_name")
    date_str = data.get("release_date") if is_movie else data.get("first_air_date")
    year = date_str[:4] if date_str and len(date_str) >= 4 else "N/A"

    vote_avg = data.get("vote_average", 0)
    rating = f"{vote_avg:.1f}/10 ⭐" if vote_avg else "Sin calificación"

    # Duración o Temporadas
    if is_movie:
        runtime = data.get("runtime")
        if runtime:
            hours = runtime // 60
            minutes = runtime % 60
            duration = f"{hours}h {minutes}m" if hours else f"{minutes}m"
        else:
            duration = "Desconocida"
    else:
        seasons = data.get("number_of_seasons", 1)
        episodes = data.get("number_of_episodes", "?")
        duration = f"{seasons} temp. ({episodes} caps)"

    # Géneros
    genres = [g.get("name") for g in data.get("genres", [])]
    genres_str = ", ".join(genres[:3]) if genres else "General"

    # Sinopsis
    overview = data.get("overview", "").strip()
    if not overview:
        overview = "Sin sinopsis disponible en español."
    elif len(overview) > 400:
        overview = overview[:397] + "..."

    # Poster
    poster_path = data.get("poster_path")
    poster_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None

    # Trailer
    trailer_url = None
    videos = data.get("videos", {}).get("results", [])
    for v in videos:
        if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser"]:
            trailer_url = f"https://www.youtube.com/watch?v={v.get('key')}"
            break

    # Proveedores de streaming (JustWatch)
    providers_all = data.get("watch/providers", {}).get("results", {})
    country_data = providers_all.get(country, {})
    flatrate = country_data.get("flatrate", [])
    free = country_data.get("free", [])
    rent_buy = country_data.get("rent", [])

    streaming_platforms = []
    for p in (flatrate + free):
        name = p.get("provider_name")
        if name and name not in streaming_platforms:
            streaming_platforms.append(name)

    return {
        "id": data.get("id"),
        "media_type": media_type,
        "title": title,
        "original_title": orig_title,
        "year": year,
        "rating": rating,
        "duration": duration,
        "genres": genres_str,
        "overview": overview,
        "poster_url": poster_url,
        "trailer_url": trailer_url,
        "streaming": streaming_platforms,
        "country": country
    }

