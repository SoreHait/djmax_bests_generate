from PIL import Image, ImageDraw, ImageFont
import os
from . import models, constants, api_handler, util


IMAGE_PATH = os.path.join(os.path.dirname(__file__), "images", "scorelist")
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts")

def generate_single_song(draw_pattern_text: bool, song: models.DMSongSimple) -> Image.Image:
    bg = Image.new("RGBA", (160, 200), 'black')
    draw = ImageDraw.Draw(bg)
    font_bd = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_bd.ttf"), 30)

    cover = api_handler.get_cover(song.songid)
    cover = cover.resize((160, 160))
    bg.paste(cover)

    draw.text((10, 141), song.dlc_code, font=font_bd, fill=constants.DLC_COLOR.get(song.dlc_code, 'white'), anchor="lm")
    if draw_pattern_text:
        draw.text((150, 141), song.pattern, font=font_bd, fill=constants.DIFF_COLOR[song.pattern], anchor="rm")

    draw.text((80, 179), f"{song.score}%" if song.score is not None else "N/P", font=font_bd, fill='white', anchor="mm")

    return bg

def generate_scorelist_image(data: models.DMScorelist) -> Image.Image:
    # Layout settings
    layout_width = 10
    card_gap = 20
    group_sep_height = 2
    l_space = 300
    t_space = 400
    r_space = 100
    b_space = 200
    card_size = (160, 200)
    mc_img_size = (60, 60)
    mc_pos_offset = (-12, 12)

    # Layout calculations
    total_width = l_space + card_size[0] * layout_width + card_gap * (layout_width - 1) + r_space
    total_height = t_space + b_space
    for floor in data.floors:
        floor_height = (len(floor.songs) - 1) // layout_width + 1
        total_height += group_sep_height + card_gap + floor_height * (card_size[1] + card_gap)
    mc_pos_offset = (card_size[0] - mc_img_size[0] // 2 + mc_pos_offset[0], 0 - mc_img_size[1] // 2 + mc_pos_offset[1])
    most_occurred_pattern = data.most_occurred_pattern

    bg = Image.new("RGBA", (total_width, total_height), '#242424')
    draw = ImageDraw.Draw(bg)
    font_lt = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_lt.ttf"), 58)
    font_rg = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_rg.ttf"), 150)
    font_bd = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_bd.ttf"), 150)

    # Grand header
    draw.text((200, 200), f"{data.username} {data.bmode}B", fill='white', anchor='lm', font=font_rg)
    draw.text((1200, 200), f"{most_occurred_pattern}{data.level}", fill=constants.DIFF_COLOR[most_occurred_pattern], anchor='lm', font=font_bd)

    # Song section
    font_rg = font_rg.font_variant(size=24)
    font_bd = font_bd.font_variant(size=100)
    overlay = Image.new("RGBA", (total_width, total_height))
    y_offset = t_space
    x_offset = l_space
    for floor in data.floors:
        draw.rectangle([(l_space, y_offset), (total_width - r_space, y_offset + group_sep_height)], fill='white')
        y_offset += group_sep_height + card_gap

        if floor.floor_constant > 0:
            draw.text((l_space - 20, y_offset), str(floor.floor_constant), fill='white', anchor='rt', font=font_bd)
            draw.text((l_space - 20, y_offset + 85), "SC Equiv.", fill='white', anchor='rt', font=font_rg)
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
                mc_img = Image.open(os.path.join(IMAGE_PATH, f"{mc_state}.png"))
                mc_img = mc_img.resize(mc_img_size)
                mc_paste_pos = (x_offset + mc_pos_offset[0], y_offset + mc_pos_offset[1])
                overlay.alpha_composite(mc_img, mc_paste_pos)

            x_offset += card_size[0] + card_gap
        x_offset = l_space
        y_offset += card_size[1] + card_gap

    # composite overlay at once
    bg.alpha_composite(overlay)

    # Footer
    draw.text((total_width // 2, total_height - b_space), "ぷろとたいぷ", fill='white', anchor='mt', font=font_lt)

    return bg
