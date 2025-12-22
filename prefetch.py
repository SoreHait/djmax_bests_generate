from djmax_bests import api_handler

api_handler.remove_cache()
db = api_handler.fetch_song_db()
for song in db.root:
    api_handler.get_cover(song.songid)
