import os
from math import ceil
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from djmax_bests import models, constants, util
from . import constants as c


def __render_header_base(data: models.DMScorelist, bg: Image.Image,
                         star_strip_func: Callable[[ImageDraw.ImageDraw], None],
                         stats_func: Callable[[models.DMScorelist, Image.Image], None]) -> None:
    font_rg = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_rg.ttf"), 80)
    font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 270)
    draw = ImageDraw.Draw(bg)

    draw.rectangle(c.BMODE_STRIP_BOX, fill=constants.BMODE_COLOR[data.bmode])
    draw.text((193, 357), str(data.bmode), fill='white', anchor='ms', font=font_bd)
    draw.text((873, 165), data.username, fill='white', anchor='lm', font=font_rg)

    star_strip_func(draw)
    stats_func(data, bg)


def __render_stats_basic(data: models.DMScorelist, bg: Image.Image) -> None:
    font_rg = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_rg.ttf"), 60)
    font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 60)
    draw = ImageDraw.Draw(bg)

    draw.text((868, 360), "Avg Rate", fill='white', anchor='ls', font=font_rg)
    draw.text((868, 432), "Completion", fill='white', anchor='ls', font=font_rg)
    current_x = 1200
    avg_s = f"{data.avg_score:.2f}%"
    comp_s = f"{data.completion_rate:.2f}%"
    comp_s_len = ceil(draw.textlength(comp_s, font=font_bd))
    current_x += comp_s_len
    draw.text((current_x, 360), avg_s, fill='white', anchor='rs', font=font_bd)
    draw.text((current_x, 432), comp_s, fill='white', anchor='rs', font=font_bd)

    current_x += 30
    draw.rectangle([(current_x - 1, 310), (current_x + 1, 440)], fill='white')

    current_x += 30
    draw.text((current_x, 360), f"≥99%", fill='white', anchor='ls', font=font_rg)
    draw.text((current_x, 432), f"≥97%", fill='white', anchor='ls', font=font_rg)

    current_x += 179 + 30  # length of "≥97%" and padding
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


def render_header_standard(data: models.DMScorelist, bg: Image.Image, main_pattern: str) -> None:
    def __render_star_strip(draw: ImageDraw.ImageDraw) -> None:
        font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 70)

        sc_tier = str((data.level - 1) // 5) if data.is_sc else "" # NM HD MX SC0 SC1 SC2
        with util.assemble_diff_strip_level(is_sc=data.is_sc, level_to=data.level,
                                            diff_star_path=c.DIFF_STAR_PATH) as star_strip:
            bg.alpha_composite(star_strip, (868, 231))
            draw.text((868 + star_strip.width + 20, 228 + star_strip.height // 2),
                      f"{main_pattern}{data.level}",
                      fill=constants.DIFF_COLOR[main_pattern + sc_tier],
                      anchor='lm', font=font_bd)

    __render_header_base(data, bg, __render_star_strip, __render_stats_basic)


def render_header_by_pack(data: models.DMScorelist, bg: Image.Image, pack_name: str, pack_color: str) -> None:
    def __render_star_strip(draw: ImageDraw.ImageDraw) -> None:
        font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 70)

        with util.assemble_diff_strip_range(is_sc=data.is_sc, level_from=data.floors[-1].floor_constant,
                                            level_to=data.floors[0].floor_constant,
                                            diff_star_path=c.DIFF_STAR_PATH) as star_strip:
            bg.alpha_composite(star_strip, (868, 225))
            draw.text((868 + star_strip.width + 20, 223 + star_strip.height // 2),
                      pack_name, fill=pack_color,
                      anchor='lm', font=font_bd)

    __render_header_base(data, bg, __render_star_strip, __render_stats_basic)


def render_header_pp(data: models.DMScorelist, bg: Image.Image) -> None:
    def __render_star_strip(draw: ImageDraw.ImageDraw) -> None:
        font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 70)

        with util.assemble_diff_strip_blank(is_sc=data.is_sc, diff_star_path=c.DIFF_STAR_PATH) as star_strip:
            bg.alpha_composite(star_strip, (868, 231))
            draw.text((868 + star_strip.width // 2, 228 + star_strip.height // 2),
                      "PERFECT PLAY", fill='#fe0544',
                      anchor='mm', font=font_bd)

    def __render_stats(_data: models.DMScorelist, _bg: Image.Image) -> None:
        font_rg = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_rg.ttf"), 60)
        font_bd = ImageFont.truetype(os.path.join(c.FONT_PATH, "Respect_bd.ttf"), 60)
        draw = ImageDraw.Draw(_bg)

        current_x = 868

        draw.text((current_x, 360), "Highest SC Level", fill='white', anchor='ls', font=font_rg)
        draw.text((current_x, 432), "Highest Non-SC Level", fill='white', anchor='ls', font=font_rg)
        current_x += 670
        sc_level = _data.first_sc_level
        nonsc_level = _data.first_nonsc_level
        draw.text((current_x, 360), str(sc_level) if sc_level > 0 else "--",
                  fill='white', anchor='rs', font=font_bd)
        draw.text((current_x, 432), str(nonsc_level) if nonsc_level > 0 else "--",
                  fill='white', anchor='rs', font=font_bd)

        current_x += 10
        sc_star_name = f"sc_{(sc_level - 1) // 5 + 1 if sc_level > 0 else 0}.png"
        nonsc_star_name = f"nm_{(nonsc_level - 1) // 5 + 1 if nonsc_level > 0 else 0}.png"
        with Image.open(os.path.join(c.DIFF_STAR_PATH, sc_star_name)) as sc_star_img:
            res = sc_star_img.resize((60, 60))
            bg.alpha_composite(res, (current_x, 365 - c.MC_IMG_SIZE[1]))
        with Image.open(os.path.join(c.DIFF_STAR_PATH, nonsc_star_name)) as nonsc_star_img:
            res = nonsc_star_img.resize((60, 60))
            bg.alpha_composite(res, (current_x, 437 - c.MC_IMG_SIZE[1]))

        current_x += 30 + 60 # star width
        draw.rectangle([(current_x - 1, 310), (current_x + 1, 440)], fill='white')

        current_x += 30
        with Image.open(os.path.join(c.ASSET_PATH, "PP_counter.png")) as pp_img:
            bg.alpha_composite(pp_img, (current_x, 365 - c.MC_IMG_SIZE[1]))
            bg.alpha_composite(pp_img, (current_x, 437 - c.MC_IMG_SIZE[1]))
        current_x += c.MC_IMG_SIZE[0] + 30
        draw.text((current_x, 360), "SC", fill='white', anchor='ls', font=font_rg)
        draw.text((current_x, 432), "Non-SC", fill='white', anchor='ls', font=font_rg)
        current_x += 230
        csc, cnsc = data.count_sc_nonsc
        step = ceil(max(draw.textlength(str(csc), font=font_bd), draw.textlength(str(cnsc), font=font_bd)))
        current_x += step
        draw.text((current_x, 360), str(csc), fill='white', anchor='rs', font=font_bd)
        draw.text((current_x, 432), str(cnsc), fill='white', anchor='rs', font=font_bd)

    __render_header_base(data, bg, __render_star_strip, __render_stats)
