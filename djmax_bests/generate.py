from . import api_handler, image_generate, models
from PIL import Image


BOARD_LIST = ["SC", "MX", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]

def generate_bests(username: str, bmode: str) -> Image.Image:
    bests_data = models.DMBests(username=username, bmode=bmode, basic=[], new=[])
    for board in BOARD_LIST:
        print(f"Fetching: {username} - {bmode}B - {board}")
        next_bests_data = api_handler.fetch_board_data(username, bmode, board)
        if next_bests_data.basic_max_djpower >= bests_data.basic_min_djpower or \
           next_bests_data.new_max_djpower >= bests_data.new_min_djpower:
            bests_data += next_bests_data
            bests_data.justify()
        else:
            break

    return image_generate.generate_bests_image(bests_data)
