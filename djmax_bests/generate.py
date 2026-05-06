from PIL import Image

from . import api_handler, models
from .generators import bests_generator, scorelist_generator


async def generate_bests(username: str, bmode: int) -> Image.Image:
    bests_data = await api_handler.fetch_bests(username, bmode)
    bests_data.organize()
    return await bests_generator.generate_bests_image(bests_data)


async def generate_bests_theoretical(bmode: int) -> Image.Image:
    song_db = await api_handler.fetch_song_db()
    bests_data = models.DMBests.get_theoretical_bests(bmode, song_db)
    bests_data.organize()
    return await bests_generator.generate_bests_image(bests_data, is_max=True)


async def generate_scorelist(username: str, bmode: int, is_sc: bool, level: int) -> Image.Image:
    scorelist_data = await api_handler.fetch_scorelist(username, bmode, is_sc, level)
    scorelist_data.organize()
    return await scorelist_generator.generate_scorelist_image(scorelist_data)


async def generate_scorelist_new(username: str, bmode: int) -> Image.Image:
    scorelist_data = await api_handler.fetch_scorelist_new(username, bmode)
    scorelist_data.organize()
    return await scorelist_generator.generate_scorelist_image(scorelist_data)
