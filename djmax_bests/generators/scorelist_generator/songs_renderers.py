import os
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from djmax_bests import models, util
from . import constants as c
from .components import generate_single_song


font_rg = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_rg.ttf"), 30)
font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 90)
mc_pos = (c.CARD_SIZE[0] - c.MC_IMG_SIZE[0] // 2 + c.MC_POS_OFFSET[0], 0 - c.MC_IMG_SIZE[1] // 2 + c.MC_POS_OFFSET[1])


async def __render_base(group_header_func: Callable[[models.DMScorelistFloor, ImageDraw.ImageDraw, int], None],
                        data: models.DMScorelist, dimension: tuple[int, int],
                        need_pattern_text_func: Callable[[models.DMSongSimple], bool]) -> Image.Image:
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

        group_header_func(floor, draw, y_offset)

        for s_idx, song in enumerate(floor.songs):
            with await generate_single_song(need_pattern_text_func(song), song) as card_image:
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

    return overlay


async def render_songs_standard(data: models.DMScorelist, dimension: tuple[int, int], main_pattern: str) -> Image.Image:
    def __draw_group_header(floor: models.DMScorelistFloor, draw: ImageDraw.ImageDraw, y_offset: int) -> None:
        if floor.floor_constant > 0:
            if data.is_sc:
                # draw in SC deviation value
                scaled = floor.floor_constant * 10
                integer = scaled // 10
                decimal = scaled % 10
                constant_offset = int((integer - data.level) * 3 + (decimal - 1))
                draw.text((c.L_SPACE - 20, y_offset), f"{constant_offset:+}",
                          fill='white', anchor='rt', font=font_bd)
                draw.text((c.L_SPACE - 20, y_offset + 85), str(floor.floor_constant),
                          fill='white', anchor='ra', font=font_rg)
            else:
                # draw in plain SC value
                draw.text((c.L_SPACE - 20, y_offset), f"{floor.floor_diff}{floor.floor_constant}",
                          fill='white', anchor='rt', font=font_bd)

        else:
            draw.text((c.L_SPACE - 20, y_offset), "N/A", fill='white', anchor='rt', font=font_bd)

    def __need_pattern_text_func(song: models.DMSongSimple) -> bool:
        return song.pattern != main_pattern

    return await __render_base(__draw_group_header, data, dimension, __need_pattern_text_func)


async def render_songs_by_pack(data: models.DMScorelist, dimension: tuple[int, int]) -> Image.Image:
    def __draw_group_header(floor: models.DMScorelistFloor, draw: ImageDraw.ImageDraw, y_offset: int) -> None:
        draw.text((c.L_SPACE - 20, y_offset), f"{floor.floor_diff}{floor.floor_constant}",
                  fill='white', anchor='rt', font=font_bd)

    return await __render_base(__draw_group_header, data, dimension, lambda _: False)
