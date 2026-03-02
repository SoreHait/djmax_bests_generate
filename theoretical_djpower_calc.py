from djmax_bests import api_handler, models
import asyncio


def get_theoretical_djpower(bmode: int):
    song_db = asyncio.run(api_handler.fetch_song_db())
    bests_data = models.DMBests.get_theoretical_bests(bmode, song_db)
    bests_data.organize()
    return bests_data.total_djpower_raw


for bmode in [4, 5, 6, 8]:
    maxp = get_theoretical_djpower(bmode)
    print(bmode, maxp)
