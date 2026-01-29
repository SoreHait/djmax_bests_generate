import os
from decimal import ROUND_FLOOR, Decimal
from PIL import Image
from PIL.ImageFont import FreeTypeFont

from . import constants


def get_djpower_tier(djpower: Decimal) -> tuple[str, int]:
    if djpower >= 9980:
        return "lord", 1
    elif djpower < 500:
        return "beginner", 1

    for tier, threshold_list in constants.DJPOWER_TIER_MAP:
        for idx, threshold in enumerate(threshold_list):
            if djpower >= threshold:
                return tier, idx + 1

    raise ValueError("DJPower tier not found")

def format_djpower_tier(tier: str, level: int) -> str:
    tier_name = constants.DJPOWER_TIER_DESC[tier]
    if tier == "lord" or tier == "beginner":
        return tier_name
    level_name = ["", "I", "II", "III", "IV"][level]
    return f"{tier_name} {level_name}"

def wrap_text(text: str, font: FreeTypeFont, wrap_width: int) -> str:
    text_width = font.getmask(text).getbbox()[2]
    if text_width > wrap_width:
        wrap_scale = text_width / wrap_width
        text = text[:int(len(text) // wrap_scale)]
        while font.getmask(text + '...').getbbox()[2] > wrap_width:
            text = text[:-1]
        text += '...'
    return text

def is_new(dlc_code: str, songid: int) -> bool:
    return (dlc_code in constants.NEW_DLC) or (songid in constants.NEW_SONG)

def get_mc_state(score: Decimal | None, max_combo: int | None) -> str | None:
    mc_state = None
    if score == Decimal("100.0"):
        mc_state = "PP"
    elif max_combo:
        mc_state = "MC"
    return mc_state

def assemble_diff_strip(is_sc: bool, level: int, diff_star_path: str) -> Image.Image:
    pattern_type = "sc" if is_sc else "nm"
    stars = [
        Image.open(os.path.join(diff_star_path, f"{pattern_type}_1.png")),
        Image.open(os.path.join(diff_star_path, f"{pattern_type}_2.png")),
        Image.open(os.path.join(diff_star_path, f"{pattern_type}_3.png")),
        Image.open(os.path.join(diff_star_path, f"{pattern_type}_0.png")),
    ]

    star_size = stars[0].size
    strip_size = (star_size[0] * 15, star_size[1])

    strip = Image.new("RGBA", strip_size)
    for i in range(15):
        if i < level:
            star_img = stars[i // 5]
        else:
            star_img = stars[3]
        strip.paste(star_img, (i * star_size[0], 0))

    return strip

def diff_coeff(diff: int, is_sc: bool) -> int:
    if is_sc:
        if diff <= 8:
            return diff + 22
        else:
            return (diff - 8) * 2 + 30
    else:
        return diff * 2

def djpower_pp(coeff: int) -> Decimal:
    return coeff * Decimal('2.22') + Decimal('2.31')

def cut_digits(num: Decimal, digit: int) -> Decimal:
    return num.quantize(Decimal(f'0.{"0" * (digit - 1)}1'), rounding=ROUND_FLOOR)
