from PIL import Image, ImageDraw, ImageFont
import os
from . import models
from . import api_handler
from decimal import Decimal


def generate_single_song(idx: int, type: str, song: models.DMSong) -> Image.Image:
    image = Image.new("RGBA", (270, 80), 'white')
    draw = ImageDraw.Draw(image)
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "LINESeedKRJP.ttf")
    cover = api_handler.get_cover(song.songid)
    if cover.size != (80, 80):
        cover = cover.resize((80, 80))
    image.paste(cover, (0, 0))

    mc_state = ""
    if song.score == Decimal("100.0"):
        mc_state = "PP"
    elif song.maxCombo:
        mc_state = "MC"

    font = ImageFont.truetype(font_path, 20)
    draw.text((90, 15), song.title, font=font, fill='black', anchor="lm")
    draw.text((90, 42), f"{song.pattern}{song.level}", font=font, fill='black', anchor="lm")
    draw.text((150, 42), f"{song.score:.2f}%", font=font, fill='black', anchor="lm")
    draw.text((260, 42), f"{mc_state}", font=font, fill='black', anchor="rm")
    draw.text((90, 68), f"{song.djpower:.4f}", font=font, fill='black', anchor="lm")
    draw.text((260, 68), f"{type} #{idx}", font=font, fill='black', anchor="rm")

    return image

def generate_bests_image(data: models.DMBests) -> Image.Image:
    # Layout: 5*20
    size = (270*5, 80*20+80)
    image = Image.new("RGBA", size, 'white')
    draw = ImageDraw.Draw(image)
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "LINESeedKRJP.ttf")
    font = ImageFont.truetype(font_path, 40)

    # Userinfo
    draw.text((20, 25), f"{data.username} - {data.bmode}B - {data.total_djpower:.4f} ({data.total_djpower_raw:.4f})", font=font, fill='black', anchor="lm")

    # BASIC section header
    draw.text((size[0]-20, 25), f"{data.total_basic_djpower:.4f} - BASIC", font=font, fill='black', anchor="rm")
    for idx, song in enumerate(data.basic):
        song_image = generate_single_song(idx + 1, "B", song)
        x = (idx % 5) * 270
        y = (idx // 5) * 80 + 40
        image.paste(song_image, (x, y))

    # NEW section header
    draw.text((size[0]-20, 80*14+40+25), f"{data.total_new_djpower:.4f} - NEW", font=font, fill='black', anchor="rm")
    for idx, song in enumerate(data.new):
        song_image = generate_single_song(idx + 1, "N", song)
        x = (idx % 5) * 270
        y = (idx // 5) * 80 + 80*14 + 40*2
        image.paste(song_image, (x, y))

    return image
