import os, asyncio
from PIL import Image, ImageDraw, ImageFont

from djmax_bests import models, constants, api_handler
from . import constants as c


def __generate_single_song_sync(draw_pattern_text: bool, song: models.DMSongSimple, cover: Image.Image) -> Image.Image:
    with Image.open(os.path.join(c.ASSET_PATH, "card.png")) as overlay:
        bg = Image.new("RGBA", overlay.size)
        with cover.resize((160, 160)) as _cover:
            bg.paste(_cover)
        bg.alpha_composite(overlay)

    draw = ImageDraw.Draw(bg)
    font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 26)
    draw.text((8, 152), song.dlc_code, font=font_bd, fill=constants.DLC_COLOR.get(song.dlc_code, 'white'), anchor="ls")
    if draw_pattern_text:
        draw.text((152, 152), song.pattern, font=font_bd, fill=constants.DIFF_COLOR[song.pattern], anchor="rs")

    font_bd = font_bd.font_variant(size=30)
    draw.text(
        (80, 178),
        f"{song.score:.2f}%" if song.score is not None else "N/P",
        font=font_bd,
        fill='white' if song.score is not None else 'gray',
        anchor="mm"
    )

    return bg


async def generate_single_song(draw_pattern_text: bool, song: models.DMSongSimple) -> Image.Image:
    with await api_handler.get_cover(song.songid) as cover:
        img = await asyncio.to_thread(__generate_single_song_sync, draw_pattern_text, song, cover)
    return img


def assemble_background(data: models.DMScorelist) -> Image.Image:
    # Layout calculations
    height = c.T_SPACE + c.B_SPACE
    for floor in data.floors:
        floor_height = (len(floor.songs) - 1) // c.LAYOUT_WIDTH + 1
        height += c.GROUP_SEP_HEIGHT + c.CARD_GAP + floor_height * (c.CARD_SIZE[1] + c.CARD_GAP)

    bg = Image.new("RGBA", (2200, height))

    pasted_height = 0
    with Image.open(os.path.join(c.ASSET_PATH, "header.png")) as header:
        bg.paste(header, (0, pasted_height))
        pasted_height += header.height
    with Image.open(os.path.join(c.ASSET_PATH, "loop.png")) as loop:
        while pasted_height < height:
            bg.paste(loop, (0, pasted_height))
            pasted_height += loop.height

    with Image.open(os.path.join(c.ASSET_PATH, "footer.png")) as footer:
        bg.alpha_composite(footer, (0, height - footer.height))

    return bg
