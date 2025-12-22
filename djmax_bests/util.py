from . import constants
from decimal import Decimal
from PIL.ImageFont import FreeTypeFont


def get_overridden_dlc_name(dlc_code: str, og_name: str) -> str:
    return constants.DLC_NAME_OVERRIDE.get(dlc_code, og_name)

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
