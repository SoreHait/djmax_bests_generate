from PIL import Image

from . import api_handler, models, generators


async def generate_bests(username: str, bmode: int) -> Image.Image:
    bests_data = await api_handler.fetch_bests(username, bmode)
    return await generators.generate_bests_image(bests_data)


async def generate_bests_theoretical(bmode: int) -> Image.Image:
    song_db = await api_handler.fetch_song_db()
    bests_data = models.DMBests.get_theoretical_bests(bmode, song_db)
    return await generators.generate_bests_image(bests_data, is_max=True)


async def generate_scorelist(username: str, bmode: int, is_sc: bool, level: int) -> Image.Image:
    scorelist_data = await api_handler.fetch_scorelist(username, bmode, is_sc, level)
    return await generators.generate_scorelist_by_level(scorelist_data)


async def generate_scorelist_new(username: str, bmode: int, diff: str) -> Image.Image:
    scorelist_data = await api_handler.fetch_scorelist_new(username, bmode, diff)
    return await generators.generate_scorelist_by_pack(scorelist_data, "NEW")


async def generate_scorelist_pack(username: str, bmode: int, diff: str, pack: str) -> Image.Image:
    scorelist_data = await api_handler.fetch_scorelist_pack(username, bmode, diff, pack)
    return await generators.generate_scorelist_by_pack(scorelist_data, pack)


async def generate_scorelist_pp(username: str, bmode: int) -> Image.Image:
    scorelist_data = await api_handler.fetch_scorelist_pp(username, bmode)
    return await generators.generate_scorelist_pp(scorelist_data)
