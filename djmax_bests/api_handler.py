import httpx, os, urllib.parse
from PIL import Image
from decimal import Decimal


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import models


COVER_PATH = os.path.join(os.path.dirname(__file__), 'covers')
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "sh-util-bot/gh:SoreHait/djmax_bests_generate"
}

if not os.path.exists(COVER_PATH):
    os.makedirs(COVER_PATH)

if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)

client = httpx.AsyncClient(headers=HEADERS)

async def get_cover(songid: int) -> Image.Image:
    img_path = os.path.join(COVER_PATH, f'{songid}.jpg')
    if os.path.exists(img_path):
        return Image.open(img_path)

    url = f"https://v-archive.net/s3/images/jackets/{songid}.jpg"
    print(f'Fetching cover {songid}')
    response = await client.get(url)
    if response.status_code == 200:
        with open(img_path, 'wb') as f:
            f.write(response.content)
        return Image.open(img_path)
    else:
        print(f'Failed to get cover {songid}')
        return Image.new('RGB', (80, 80), color='black')

def get_convert_constant(bmode: int) -> tuple[Decimal, Decimal]:
    maxpower_file = os.path.join(CACHE_PATH, f'maxpower_{bmode}.txt')
    if os.path.exists(maxpower_file):
        with open(maxpower_file, 'r') as f:
            maxpower = Decimal(f.read().strip())
            return Decimal("10000.0000") / maxpower, maxpower

    print(f'maxpower cache for {bmode}b invalidated, fetching new one')
    url = f"https://v-archive.net/api/v2/archive/DEV/djClass/{bmode}"
    response = httpx.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    with open(maxpower_file, 'w') as f:
        f.write(str(data["maxDjPower"]))
    maxpower = Decimal(str(data["maxDjPower"]))
    return Decimal("10000.0000") / maxpower, maxpower

async def fetch_song_db() -> "models.DMSongDB":
    from .models import DMSongDB
    db_path = os.path.join(CACHE_PATH, 'songs.json')
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return DMSongDB.model_validate_json(f.read())

    print("songdb cache invalidated, fetching new one")
    url = "https://v-archive.net/db/v2/songs.json"
    response = await client.get(url)
    response.raise_for_status()
    with open(db_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    return DMSongDB.model_validate_json(response.text)

def remove_cache():
    cache_files = os.listdir(CACHE_PATH)
    for file in cache_files:
        file_path = os.path.join(CACHE_PATH, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("Cache cleared")


def build_req_url(username: str, bmode: int, **kwargs) -> str:
    query = urllib.parse.urlencode(kwargs)
    return f"https://v-archive.net/api/v2/archive/{username}/button/{bmode}?{query}"

async def fetch_bests(username: str, bmode: int) -> "models.DMBests":
    from .models import DMBests, VAResponse
    print(f'Fetching bests for {username} - {bmode}b')
    url_basic = build_req_url(
        username,
        bmode,
        newTab = "false",
        sort = "djpower",
        order = "desc",
        limit = "70"
    )
    url_new = build_req_url(
        username,
        bmode,
        newTab = "true",
        sort = "djpower",
        order = "desc",
        limit = "30"
    )
    response_basic = await client.get(url_basic)
    response_basic.raise_for_status()
    response_new = await client.get(url_new)
    response_new.raise_for_status()

    va_resp_basic = VAResponse.model_validate_json(response_basic.text)
    va_resp_new = VAResponse.model_validate_json(response_new.text)
    return DMBests.from_va_response(va_resp_basic, va_resp_new)

async def fetch_scorelist(username: str, bmode: int, is_sc: bool, level: int) -> "models.DMScorelist":
    from .models import DMScorelist, VAResponse
    print(f'Fetching scorelist for {username} - {bmode}b - {"SC" if is_sc else "NM,HD,MX"} - level {level}')
    url = build_req_url(
        username,
        bmode,
        pattern = "SC" if is_sc else "NM,HD,MX",
        levelMin = level,
        levelMax = level
    )
    response = await client.get(url)
    response.raise_for_status()
    song_db = await fetch_song_db()
    va_resp = VAResponse.model_validate_json(response.text)
    return DMScorelist.from_va_response_level(is_sc, level, song_db, va_resp)

async def fetch_scorelist_new(username: str, bmode: int, diff: str) -> "models.DMScorelist":
    from .models import DMScorelist, VAResponse
    print(f'Fetching scorelist for {username} - {bmode}b - NEW SONGS')
    url = build_req_url(
        username,
        bmode,
        pattern = diff,
        newTab = "true"
    )
    response = await client.get(url)
    response.raise_for_status()
    song_db = await fetch_song_db()
    va_resp = VAResponse.model_validate_json(response.text)
    return DMScorelist.from_va_response_new(diff, song_db, va_resp)
