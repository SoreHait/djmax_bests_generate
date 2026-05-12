import os
from PIL import Image, ImageDraw, ImageFont

from djmax_bests import models, util
from . import constants as c
from .components import generate_single_song


font_rg = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_rg.ttf"), 24)
font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 100)
mc_pos = (c.CARD_SIZE[0] - c.MC_IMG_SIZE[0] // 2 + c.MC_POS_OFFSET[0], 0 - c.MC_IMG_SIZE[1] // 2 + c.MC_POS_OFFSET[1])


async def by_difficulty(data: models.DMScorelist, dimension: tuple[int, int], main_pattern: str | None):
    overlay = Image.new("RGBA", dimension)
    draw = ImageDraw.Draw(overlay)
    y_offset = c.T_SPACE
    x_offset = c.L_SPACE
    for floor in data.floors:
        draw.rectangle([
            (c.L_SPACE, y_offset),
            (dimension[0] - c.R_SPACE, y_offset + c.GROUP_SEP_HEIGHT - 1)],
            fill='white')
        y_offset += c.GROUP_SEP_HEIGHT + c.CARD_GAP

        if floor.floor_constant > 0:
            scaled = floor.floor_constant * 10
            integer = scaled // 10
            decimal = scaled % 10
            if data.is_sc:
                constant_offset = int((integer - data.level) * 3 + (decimal - 1))
                draw.text((c.L_SPACE - 20, y_offset), "0" if constant_offset == 0 else f"{constant_offset:+}",
                          fill='white', anchor='rt', font=font_bd)
                if constant_offset == 0:
                    draw.text((c.L_SPACE - 20, y_offset + 85), "Baseline", fill='white', anchor='ra', font=font_rg)
                elif constant_offset == 1:
                    draw.multiline_text((c.L_SPACE - 20, y_offset + 85), "Relative Difficulty\nCompared to Baseline",
                                        fill='white', anchor='ra', font=font_rg, align='right')
                elif integer != data.level and decimal == 1:
                    draw.text((c.L_SPACE - 20, y_offset + 85), f"SC{integer} Baseline", fill='white', anchor='ra',
                              font=font_rg)
                elif integer != data.level and decimal == 3:
                    draw.text((c.L_SPACE - 20, y_offset + 85), f"SC{integer} +2", fill='white', anchor='ra',
                              font=font_rg)
            else:
                draw.text((c.L_SPACE - 20, y_offset), f"SC{integer}", fill='white', anchor='rt', font=font_bd)

        else:
            draw.text((c.L_SPACE - 20, y_offset), "N/A", fill='white', anchor='rt', font=font_bd)

        for s_idx, song in enumerate(floor.songs):
            need_pattern_text = song.pattern != main_pattern
            with await generate_single_song(need_pattern_text, song) as card_image:
                if s_idx % c.LAYOUT_WIDTH == 0 and s_idx != 0:
                    x_offset = c.L_SPACE
                    y_offset += c.CARD_SIZE[1] + c.CARD_GAP
                overlay.paste(card_image, (x_offset, y_offset))

            if mc_state := util.get_mc_state(song.score, song.max_combo):
                with Image.open(os.path.join(c.ASSET_PATH, f"{mc_state}_badge.png")) as mc_img:
                    mc_paste_pos = (x_offset + mc_pos[0], y_offset + mc_pos[1])
                    overlay.alpha_composite(mc_img, mc_paste_pos)

            x_offset += c.CARD_SIZE[0] + c.CARD_GAP
        x_offset = c.L_SPACE
        y_offset += c.CARD_SIZE[1] + c.CARD_GAP
