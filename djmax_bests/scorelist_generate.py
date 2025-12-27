from PIL import Image, ImageDraw, ImageFont
import os
from . import models, constants, api_handler, util
from math import ceil


IMAGE_PATH = os.path.join(os.path.dirname(__file__), "images", "scorelist")
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts")
DIFF_STAR_PATH = os.path.join(IMAGE_PATH, "diff_stars")

def generate_single_song(draw_pattern_text: bool, song: models.DMSongSimple) -> Image.Image:
    bg = Image.new("RGBA", (160, 200))
    draw = ImageDraw.Draw(bg)
    font_bd = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_bd.ttf"), 26)

    cover = api_handler.get_cover(song.songid)
    cover = cover.resize((160, 160))
    bg.paste(cover)
    overlay = Image.open(os.path.join(IMAGE_PATH, "card.png"))
    bg.alpha_composite(overlay)

    draw.text((8, 152), song.dlc_code, font=font_bd, fill=constants.DLC_COLOR.get(song.dlc_code, 'white'), anchor="ls")
    if draw_pattern_text:
        draw.text((152, 152), song.pattern, font=font_bd, fill=constants.DIFF_COLOR[song.pattern], anchor="rs")

    font_bd = font_bd.font_variant(size=30)
    draw.text((80, 178), f"{song.score}%" if song.score is not None else "N/P", font=font_bd, fill='white', anchor="mm")

    return bg

def assemble_background(height: int) -> Image.Image:
    bg = Image.new("RGBA", (2200, height))
    header = Image.open(os.path.join(IMAGE_PATH, "header.png"))
    loop = Image.open(os.path.join(IMAGE_PATH, "loop.png"))

    pasted_height = 0
    bg.paste(header, (0, pasted_height))
    pasted_height += header.height
    while pasted_height < height:
        bg.paste(loop, (0, pasted_height))
        pasted_height += loop.height

    draw = ImageDraw.Draw(bg)
    draw.rectangle([(0, height - 20), (2200, height)], fill='#1c1c1c')

    return bg

def generate_scorelist_image(data: models.DMScorelist) -> Image.Image:
    # Layout settings
    layout_width = 10
    card_gap = 20
    group_sep_height = 3
    l_space = 310
    t_space = 536
    r_space = 110
    b_space = 142
    card_size = (160, 200)
    mc_img_size = (60, 60)
    mc_pos_offset = (-12, 12)
    bmode_strip_box = (70, 20, 89, 464)

    # Layout calculations
    total_width = l_space + card_size[0] * layout_width + card_gap * (layout_width - 1) + r_space
    assert total_width == 2200
    total_height = t_space + b_space + 20 # bottom margin
    for floor in data.floors:
        floor_height = (len(floor.songs) - 1) // layout_width + 1
        total_height += group_sep_height + card_gap + floor_height * (card_size[1] + card_gap)
    mc_pos_offset = (card_size[0] - mc_img_size[0] // 2 + mc_pos_offset[0], 0 - mc_img_size[1] // 2 + mc_pos_offset[1])
    most_occurred_pattern = data.most_occurred_pattern

    bg = assemble_background(total_height)
    draw = ImageDraw.Draw(bg)
    font_rg = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_rg.ttf"), 80)
    font_bd = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_bd.ttf"), 270)

    # Grand header
    draw.rectangle(bmode_strip_box, fill=constants.BMODE_COLOR[data.bmode])
    draw.text((193, 357), data.bmode, fill='white', anchor='ms', font=font_bd)
    draw.text((873, 165), data.username, fill='white', anchor='lm', font=font_rg)

    star_strip = util.assemble_diff_strip(data.is_sc, data.level, DIFF_STAR_PATH)
    bg.alpha_composite(star_strip, (868, 231))
    font_bd = font_bd.font_variant(size=70)
    draw.text((868 + star_strip.width + 20, 228 + star_strip.height // 2), f"{most_occurred_pattern}{data.level}", fill=constants.DIFF_COLOR[most_occurred_pattern], anchor='lm', font=font_bd)

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
    mc_img = Image.open(os.path.join(IMAGE_PATH, "MC_counter.png"))
    pp_img = Image.open(os.path.join(IMAGE_PATH, "PP_counter.png"))
    bg.alpha_composite(mc_img, (current_x, 365 - mc_img_size[1]))
    bg.alpha_composite(pp_img, (current_x, 437 - mc_img_size[1]))

    current_x += mc_img_size[0] + 30
    cmc, cpp = data.count_mc_pp
    step = ceil(max(draw.textlength(str(cmc), font=font_bd), draw.textlength(str(cpp), font=font_bd)))
    current_x += step
    draw.text((current_x, 360), str(cmc), fill='white', anchor='rs', font=font_bd)
    draw.text((current_x, 432), str(cpp), fill='white', anchor='rs', font=font_bd)

    # Song section
    font_rg = font_rg.font_variant(size=24)
    font_bd = font_bd.font_variant(size=100)
    overlay = Image.new("RGBA", (total_width, total_height))
    y_offset = t_space
    x_offset = l_space
    for floor in data.floors:
        draw.rectangle([(l_space, y_offset), (total_width - r_space, y_offset + group_sep_height - 1)], fill='white')
        y_offset += group_sep_height + card_gap

        if floor.floor_constant > 0:
            draw.text((l_space - 20, y_offset), str(floor.floor_constant), fill='white', anchor='rt', font=font_bd)
            draw.text((l_space - 20, y_offset + 85), "SC Equivalent", fill='white', anchor='rt', font=font_rg)
        else:
            draw.text((l_space - 20, y_offset), "N/A", fill='white', anchor='rt', font=font_bd)
            draw.text((l_space - 20, y_offset + 85), "Lower than SC1", fill='white', anchor='rt', font=font_rg)

        for idx, song in enumerate(floor.songs):
            need_pattern_text = song.pattern != most_occurred_pattern
            card_image = generate_single_song(need_pattern_text, song)
            if idx % layout_width == 0 and idx != 0:
                x_offset = l_space
                y_offset += card_size[1] + card_gap
            overlay.paste(card_image, (x_offset, y_offset))

            if (mc_state := util.get_mc_state(song.score, song.max_combo)):
                mc_img = Image.open(os.path.join(IMAGE_PATH, f"{mc_state}_badge.png"))
                mc_paste_pos = (x_offset + mc_pos_offset[0], y_offset + mc_pos_offset[1])
                overlay.alpha_composite(mc_img, mc_paste_pos)

            x_offset += card_size[0] + card_gap
        x_offset = l_space
        y_offset += card_size[1] + card_gap

    # composite overlay at once
    bg.alpha_composite(overlay)

    # Footer
    footer = Image.open(os.path.join(IMAGE_PATH, "footer.png"))
    bg.alpha_composite(footer, (0, total_height - footer.height))

    return bg
