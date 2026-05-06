from PIL import Image
from djmax_bests import models
from .components import assemble_background, assemble_song_cards


async def generate_bests_image(data: models.DMBests, is_max: bool = False) -> Image.Image:
    basic_start = (100, 691)
    new_start = (100, 3405)

    bg = assemble_background(data, is_max)
    basic_section = await assemble_song_cards(data.basic, "basic")
    new_section = await assemble_song_cards(data.new, "new")
    bg.alpha_composite(basic_section, basic_start)
    bg.alpha_composite(new_section, new_start)

    return bg
