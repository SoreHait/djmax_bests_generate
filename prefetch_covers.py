from djmax_bests import api_handler
import asyncio, os

sem = asyncio.Semaphore(15)

async def worker(songid):
    async with sem:
        await api_handler.get_cover(songid)

async def main():
    api_handler.remove_cache()
    db = await api_handler.fetch_song_db()
    exist_covers = os.listdir("djmax_bests/covers")
    inexist_covers = []
    for song in db.root:
        if f'{song.songid}.jpg' not in exist_covers:
            inexist_covers.append(song.songid)

    print(f'{len(inexist_covers)} covers to fetch')
    await asyncio.gather(*[worker(songid) for songid in inexist_covers])

asyncio.run(main())
