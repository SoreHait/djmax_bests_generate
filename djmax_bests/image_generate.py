from PIL import Image, ImageDraw, ImageFont
import os
from . import models
from . import api_handler


def generate_single_song(song: models.DMSong) -> Image.Image:
    image = Image.new("RGBA", (300, 80), 'white')
    draw = ImageDraw.Draw(image)
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "LINESeedKR-Rg.ttf")
    cover = api_handler.get_cover(song.songid)
    if cover.size != (80, 80):
        cover = cover.resize((80, 80))
    image.paste(cover, (0, 0))

    return image

def generate_bests_image(data: models.DMBests) -> Image.Image:
    return generate_single_song(data.basic[0])
