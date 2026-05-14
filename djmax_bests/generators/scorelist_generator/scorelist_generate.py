import asyncio
from PIL import Image

from djmax_bests import models, constants
from . import header_renderers, songs_renderers
from .components import assemble_background


async def generate_scorelist_by_level(data: models.DMScorelist) -> Image.Image:
    main_pattern = "SC" if data.is_sc else ["NM", "HD", "MX"][(data.level - 1) // 5]

    bg = await asyncio.to_thread(assemble_background, data)

    header_renderers.render_header_standard(data, bg, main_pattern)

    with await songs_renderers.render_songs_standard(data, bg.size, main_pattern) as overlay:
        bg.alpha_composite(overlay)

    return bg


async def generate_scorelist_by_pack(data: models.DMScorelist, pack_name: str) -> Image.Image:
    if pack_name == "NEW":
        pack_color = '#f4bb00'
    else:
        pack_color = constants.DLC_COLOR.get(pack_name, "#ffffff")

    bg = await asyncio.to_thread(assemble_background, data)

    header_renderers.render_header_by_pack(data, bg, pack_name, pack_color)

    with await songs_renderers.render_songs_by_pack(data, bg.size) as overlay:
        bg.alpha_composite(overlay)

    return bg
