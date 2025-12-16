import requests
from . import models
from PIL import Image
import os


COVER_PATH = os.path.join(os.path.dirname(__file__), 'covers')
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')

if not os.path.exists(COVER_PATH):
    os.makedirs(COVER_PATH)

if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)


def get_cover(songid: int) -> Image.Image:
    img_path = os.path.join(COVER_PATH, f'{songid}.jpg')
    if os.path.exists(img_path):
        return Image.open(img_path)

    url = f"https://v-archive.net/static/images/jackets/{songid}.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        with open(img_path, 'wb') as f:
            f.write(response.content)
        return Image.open(img_path)
    else:
        print(f'Failed to get cover {songid}')
        return Image.new('RGB', (80, 80), color='red')


def build_board_req_url(username: str, bmode: str, board: str) -> str:
    base_url = f"https://v-archive.net/api/archive/{username}/board/{bmode}/{board}"
    return base_url

def fetch_board_data(username: str, bmode: str, board: str) -> models.DMBests:
    url = build_board_req_url(username, bmode, board)
    response = requests.get(url)
    response.raise_for_status()
    va_resp = models.VAResponse.model_validate_json(response.text)
    return models.DMBests.from_VAResponse(username, bmode, va_resp)


def fetch_song_db() -> models.DMSongDB:
    db_path = os.path.join(CACHE_PATH, 'songs.json')
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return models.DMSongDB.model_validate_json(f.read())

    url = "https://v-archive.net/db/songs.json"
    response = requests.get(url)
    response.raise_for_status()
    with open(db_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    return models.DMSongDB.model_validate_json(response.text)
