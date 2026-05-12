import os, asyncio
from math import ceil
from PIL import Image, ImageDraw, ImageFont

from djmax_bests import models, constants, api_handler, util
from . import constants as c
from .components import assemble_background


async def generate_scorelist_image(data: models.DMScorelist) -> Image.Image:
    # Layout calculations
    total_height = c.T_SPACE + c.B_SPACE
    for floor in data.floors:
        floor_height = (len(floor.songs) - 1) // c.LAYOUT_WIDTH + 1
        total_height += c.GROUP_SEP_HEIGHT + c.CARD_GAP + floor_height * (c.CARD_SIZE[1] + c.CARD_GAP)

    main_pattern = "SC" if data.is_sc or data.level == 0 else ["NM", "HD", "MX"][(data.level - 1) // 5]
    sc_tier = str((data.level - 1) // 5) if data.is_sc else ""


    bg = await asyncio.to_thread(assemble_background, total_height)
    total_width = bg.width
    draw = ImageDraw.Draw(bg)
    font_rg = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_rg.ttf"), 80)
    font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 270)

    # Grand header
    draw.rectangle(c.BMODE_STRIP_BOX, fill=constants.BMODE_COLOR[data.bmode])
    draw.text((193, 357), str(data.bmode), fill='white', anchor='ms', font=font_bd)
    draw.text((873, 165), data.username, fill='white', anchor='lm', font=font_rg)

    with util.assemble_diff_strip(data.is_sc, data.level, c.DIFF_STAR_PATH) as star_strip:
        bg.alpha_composite(star_strip, (868, 231))
        font_bd = font_bd.font_variant(size=70)
        if data.level > 0:
            draw.text((868 + star_strip.width + 20, 228 + star_strip.height // 2), f"{main_pattern}{data.level}", fill=constants.DIFF_COLOR[main_pattern + sc_tier], anchor='lm', font=font_bd)
        else:
            draw.text((868 + star_strip.width // 2, 228 + star_strip.height // 2), "NEW SONGS", fill='#f4bb00', anchor='mm', font=font_bd)

    current_x = 1210
    font_bd = font_bd.font_variant(size=60)
    avg_s = f"{data.avg_score:.2f}%"
    comp_s = f"{data.completion_rate:.2f}%"
    comp_s_len = ceil(draw.textlength(comp_s, font=font_bd))
    current_x += comp_s_len
    draw.text((current_x, 360), avg_s, fill='white', anchor='rs', font=font_bd)
    draw.text((current_x, 432), comp_s, fill='white', anchor='rs', font=font_bd)

    current_x += 30
    draw.rectangle([(current_x - 1, 310), (current_x + 1, 440)], fill='white')

    current_x += 30
    draw.text((current_x, 360), f"≥99%", fill='white', anchor='ls', font=font_bd)
    draw.text((current_x, 432), f"≥97%", fill='white', anchor='ls', font=font_bd)

    current_x += 179 + 30 # length of "≥97%" and padding
    c99, c97 = data.count_99_97
    step = ceil(max(draw.textlength(str(c99), font=font_bd), draw.textlength(str(c97), font=font_bd)))
    current_x += step
    draw.text((current_x, 360), str(c99), fill='white', anchor='rs', font=font_bd)
    draw.text((current_x, 432), str(c97), fill='white', anchor='rs', font=font_bd)

    current_x += 30
    draw.rectangle([(current_x - 1, 310), (current_x + 1, 440)], fill='white')

    current_x += 30
    with Image.open(os.path.join(c.ASSET_PATH, "MC_counter.png")) as mc_img:
        bg.alpha_composite(mc_img, (current_x, 365 - c.MC_IMG_SIZE[1]))
    with Image.open(os.path.join(c.ASSET_PATH, "PP_counter.png")) as pp_img:
        bg.alpha_composite(pp_img, (current_x, 437 - c.MC_IMG_SIZE[1]))

    current_x += c.MC_IMG_SIZE[0] + 30
    cmc, cpp = data.count_mc_pp
    step = ceil(max(draw.textlength(str(cmc), font=font_bd), draw.textlength(str(cpp), font=font_bd)))
    current_x += step
    draw.text((current_x, 360), str(cmc), fill='white', anchor='rs', font=font_bd)
    draw.text((current_x, 432), str(cpp), fill='white', anchor='rs', font=font_bd)

    # Song section
    # TODO: Refactor all this shit

    with  as overlay:


        # composite overlay at once
        bg.alpha_composite(overlay)

    return bg
