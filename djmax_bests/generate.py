from . import api_handler, bests_generate, models, scorelist_generate
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
        print(f"Fetching: {username} - {bmode}B - {board} (BESTS - NORMAL)")
        next_bests_data = api_handler.fetch_bests(username, bmode, board)
        if next_bests_data.basic_max_djpower >= bests_data.basic_min_djpower or \
           next_bests_data.new_max_djpower >= bests_data.new_min_djpower:
            bests_data += next_bests_data
            bests_data.organize()
        else:
            break

    return bests_generate.generate_bests_image(bests_data)

# IF A PLAYER DO EXPERIENCE THE PROBLEM MENTIONED ABOVE,
# USE THIS FUNCTION INSTEAD
def generate_bests_all_boards(username: str, bmode: str) -> Image.Image:
    bests_data = models.DMBests(username=username, bmode=bmode, basic=[], new=[])
    for board in BOARD_LIST:
        print(f"Fetching: {username} - {bmode}B - {board} (BESTS - ALL BOARDS)")
        next_bests_data = api_handler.fetch_bests(username, bmode, board)
        bests_data += next_bests_data
    bests_data.organize()
    return bests_generate.generate_bests_image(bests_data)


def generate_scorelist(username: str, bmode: str, is_sc: bool, level: int):# -> Image.Image
    print(f"Fetching: {username} - {bmode}B - {'SC' if is_sc else ''}{level} (SCORELIST)")
    score_list_data = api_handler.fetch_scorelist(username, bmode, is_sc, level)
    score_list_data.organize()
    return score_list_data
