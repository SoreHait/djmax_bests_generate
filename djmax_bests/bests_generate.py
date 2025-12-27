from PIL import Image, ImageDraw, ImageFont
import os
from . import models, constants, api_handler, util
from random import random


IMAGE_PATH = os.path.join(os.path.dirname(__file__), "images", "bests")
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts")
EMBLEM_PATH = os.path.join(IMAGE_PATH, "emblems")
EMBLEM_BG_PATH = os.path.join(IMAGE_PATH, "emblem_bg")
DIFF_STAR_PATH = os.path.join(IMAGE_PATH, "diff_stars")

def generate_single_song(idx: int, type: str, song: models.DMSong) -> Image.Image:
    overlay = Image.open(os.path.join(IMAGE_PATH, f"{type}_card.png"))
    bg = Image.new("RGBA", overlay.size)
    draw = ImageDraw.Draw(bg)
    cover = api_handler.get_cover(song.songid)
    cover = cover.resize((160, 160))
    bg.paste(cover)
    bg.alpha_composite(overlay)

    font_bd = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_bd.ttf"), 23)
    font_rg = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_rg.ttf"), 30)
    draw.text((10, 141), song.dlc_code, font=font_bd, fill=constants.DLC_COLOR.get(song.dlc_code, 'white'), anchor="lm")
    draw.text((165, 21), util.wrap_text(song.title, font_rg, 300), font=font_rg, fill='white', anchor="lm")

    font_bd = font_bd.font_variant(size=30)
    draw.text((230, 95), f"{song.score:.2f}%", font=font_bd, fill='white', anchor="lm")
    draw.text((292, 135), f"{song.djpower:.4f}", font=font_bd, fill='#F0BE40', anchor="lm")

    font_bd = font_bd.font_variant(size=26)
    draw.text((516, 17), f"#{idx}", font=font_bd, fill="black" if type == "new" else "#333333", anchor="mm")

    is_sc = song.pattern == "SC"
    diff_strip = util.assemble_diff_strip(is_sc, song.level, DIFF_STAR_PATH)
    bg.alpha_composite(diff_strip, (165, 52))

    if (mc_state := util.get_mc_state(song.score, song.max_combo)):
        mc_overlay = Image.open(os.path.join(IMAGE_PATH, f"{mc_state}.png"))
        bg.alpha_composite(mc_overlay)

    return bg

def generate_bests_image(data: models.DMBests) -> Image.Image:
    gap = 20
    basic_start = (100, 688)
    new_start = (100, 3398)
    bmode_strip_box = (119, 36, 151, 468)
    emblem_lt = (1029, 154)

    bg = Image.open(os.path.join(IMAGE_PATH, "bg.png"))
    draw = ImageDraw.Draw(bg)
    font_bd = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_bd.ttf"), 320)
    font_rg = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_rg.ttf"), 80)
    font_lt = ImageFont.truetype(os.path.join(FONT_PATH, "Respect_lt.ttf"), 58)

    # Userinfo
    djpower_tier, djpower_level = util.get_djpower_tier(data.total_djpower)
    djpower_desc = util.format_djpower_tier(djpower_tier, djpower_level)
    djpower_color = constants.DJPOWER_TIER_COLOR[djpower_tier]

    if random() < 0.1 and os.path.exists(os.path.join(EMBLEM_PATH, f"{djpower_tier}_0.png")): # Easter egg
        djpower_level = 0

    if os.path.exists(os.path.join(EMBLEM_BG_PATH, f"{data.username}.png")):
        emblem_bg = Image.open(os.path.join(EMBLEM_BG_PATH, f"{data.username}.png"))
        bg.alpha_composite(emblem_bg, emblem_lt)

    emblem = Image.open(os.path.join(EMBLEM_PATH, f"{djpower_tier}_{djpower_level}.png"))
    bg.alpha_composite(emblem, emblem_lt)
    draw.rectangle(bmode_strip_box, fill=constants.BMODE_COLOR[data.bmode])
    draw.text((282, 370), data.bmode, font=font_bd, fill='white', anchor="ms")
    draw.text((1535, 212), data.username, font=font_rg, fill='white', anchor="lm")
    font_bd = font_bd.font_variant(size=64)
    draw.text((1535, 306), djpower_desc, font=font_bd, fill=djpower_color, anchor="lm")
    font_rg = font_rg.font_variant(size=120)
    draw.text((1535, 400), f"{data.total_djpower:.4f}", font=font_rg, fill='white', anchor="lm")
    font_rg = font_rg.font_variant(size=42)
    draw.text((1795, 489), f"{data.total_djpower_raw:.4f}", font=font_rg, fill='white', anchor="lm")

    font_rg = font_rg.font_variant(size=76)
    font_rg_s = font_rg.font_variant(size=46)

    # BASIC section
    draw.text((2520, 580), f"{data.total_basic_djpower:.4f}", font=font_rg, fill='white', anchor="mm")
    draw.text((2850, 600), f"{data.total_basic_djpower_raw:.4f}", font=font_rg_s, fill='white', anchor="mm")
    for idx, song in enumerate(data.basic):
        song_image = generate_single_song(idx + 1, "basic", song)
        x = basic_start[0] + (idx % 5) * (560 + gap)
        y = basic_start[1] + (idx // 5) * (160 + gap)
        bg.paste(song_image, (x, y))

    # NEW section
    draw.text((2520, 3292), f"{data.total_new_djpower:.4f}", font=font_rg, fill='white', anchor="mm")
    draw.text((2850, 3312), f"{data.total_new_djpower_raw:.4f}", font=font_rg_s, fill='white', anchor="mm")
    for idx, song in enumerate(data.new):
        song_image = generate_single_song(idx + 1, "new", song)
        x = new_start[0] + (idx % 5) * (560 + gap)
        y = new_start[1] + (idx // 5) * (160 + gap)
        bg.paste(song_image, (x, y))

    # footnote
    songdb = api_handler.fetch_song_db()
    draw.text((570, 4545), f"{constants.CONVERT_CONSTANT[data.bmode]:.8f}", font=font_lt, fill='white', anchor="ls")
    draw.text((375, 4616), ', '.join(constants.NEW_DLC), font=font_lt, fill='white', anchor="ls")
    draw.text((385, 4687), ", ".join(songdb.get_title(songid) for songid in constants.NEW_SONG), font=font_lt, fill='white', anchor="ls")

    return bg
