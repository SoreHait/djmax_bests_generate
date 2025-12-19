from . import api_handler, image_generate, models
from PIL import Image


BOARD_LIST = ["SC", "MX", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]

# THIS FUNCTION DOES NOT RETURN CORRECT RESULTS IN SOME SPECIFIC CASES
# THE ONLY CORRECT APPROACH IS TO ITERATE THROUGH ALL BOARDS
# -------------
# FOR EXAMPLE, IF A PLAYER HAS LOW POWER ON SC PATTERNS (eg. 20-30) AND MX PATTERNS (eg. 10-20)
# BUT HIGH POWER ON LOWER PATTERNS (eg. 30+), THIS FUNCTION WILL TERMINATE EARLY IN MX
# AND SKIP THOSE HIGH POWER ON LOWER PATTERNS, BUT THIS IS AN EDGE CASE
# AND A NORMAL PLAYER SHOULD NOT HAVE A TOP 100 LIKE THAT
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

# IF A PLAYER DO EXPERIENCE THE PROBLEM MENTIONED ABOVE,
# USE THIS FUNCTION INSTEAD
def generate_bests_all_boards(username: str, bmode: str) -> Image.Image:
    bests_data = models.DMBests(username=username, bmode=bmode, basic=[], new=[])
    for board in BOARD_LIST:
        print(f"Fetching: {username} - {bmode}B - {board} (ALL BOARDS MODE)")
        next_bests_data = api_handler.fetch_board_data(username, bmode, board)
        bests_data += next_bests_data
    bests_data.justify()
    return image_generate.generate_bests_image(bests_data)
