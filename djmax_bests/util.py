import requests
from PIL import Image
import os


COVER_PATH = os.path.join(os.path.dirname(__file__), 'covers')

if not os.path.exists(COVER_PATH):
    os.makedirs(COVER_PATH)

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
