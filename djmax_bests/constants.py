from decimal import Decimal


NEW_DLC = ["VL3", "PLI2", "ARC", "VL4"]

NEW_SONG = [722, 748, 749]

CONVERT_CONSTANT = {
    "4": Decimal("10000.0000") / Decimal("9168.72"),
    "5": Decimal("10000.0000") / Decimal("9213.12"),
    "6": Decimal("10000.0000") / Decimal("9190.92"),
    "8": Decimal("10000.0000") / Decimal("9257.52")
}


BMODE_COLOR = {
    "4": "#29db71",
    "5": "#40c0e6",
    "6": "#e9902f",
    "8": "#8392ff"
}

DIFF_COLOR = {
    "NM": "#F3B705",
    "HD": "#EC5808",
    "MX": "#F40440",
    "SC": "#D10569"
}

DLC_COLOR = {
    "R": "#ffd250",
    "RV": "#ffd250",
    "CP": "#ffb400",
    "P1": "#25deff",
    "P2": "#ff5082",
    "P3": "#e48609",
    "CE": "#ffffff",
    "BS": "#e90000",
    "TR": "#7582ff",
    "ES": "#34df26",
    "T1": "#f01cc8",
    "T2": "#c35a00",
    "T3": "#568bff",
    "TQ": "#0cda25",
    "VE": "#ff7f42",
    "VE2": "#ed8f5c",
    "VE3": "#a050ff",
    "VE4": "#ee0016",
    "VE5": "#ff9b00",
    "VL": "#49f8fc",
    "VL2": "#99ff33",
    "VL3": "#f26e7b",
    "VL4": "#d4c393",
    "PLI1": "#dbd7ae",
    "PLI2": "#2269f7",
    "GG": "#d83e0e",
    "BA": "#00d1ff",
    "ESTI": "#e9d19b",
    "FAL": "#a4fa71",
    "GF": "#ffb526",
    "MAP": "#bf2d10",
    "NXN": "#c3cc00",
    "TEK": "#f4f4f4",
    "ARC": "#ffffff",
    "CHU": "#ffd700",
    "CY": "#ee1538",
    "DM": "#99e5d8",
    "EZ2": "#00ecff",
    "GC": "#51eefe",
    "MD": "#fe3db3"
}

DLC_NAME_OVERRIDE = {
    "VL": "V LIBERTY",
    "VL2": "V LIBERTY 2",
    "VL3": "V LIBERTY 3",
    "VL4": "V LIBERTY 4",
    "PLI1": "TRIBUTE #1",
    "PLI2": "64514 Part.1",
    "GG": "GUILTY GEAR",
    "BA": "BLUE ARCHIVE",
    "ESTI": "ESTIMATE",
    "FAL": "FALCON",
    "GF": "GIRLS' FRONTLINE",
    "MAP": "MAPLESTORY",
    "NXN": "NEXON",
    "TEK": "TEKKEN",
    "CHU": "CHUNITHM",
    "CY": "CYTUS",
    "DM": "DEEMO",
    "EZ2": "EZ2ON",
    "GC": "GROOVE COASTER",
    "MD": "MUSE DASH"
}

DJPOWER_TIER_COLOR = {
    "beginner": "#a2a2a2",
    "trainee": "#92c2e8",
    "amateur": "#5abace",
    "rookie": "#4acbc6",
    "streetdj": "#63cfa5",
    "middleman": "#7be75a",
    "prodj": "#cef721",
    "highclass": "#efe74a",
    "professional": "#ffbe29",
    "trendsetter": "#ff9e21",
    "headliner": "#ff7531",
    "showstopper": "#e7594a",
    "beatmaestro": "#ff5563",
    "lord": "#bddbf7"
}

DJPOWER_TIER_DESC = {
    "beginner": "BEGINNER",
    "trainee": "TRAINEE",
    "amateur": "AMATEUR",
    "rookie": "ROOKIE",
    "streetdj": "STREET DJ",
    "middleman": "MIDDLEMAN",
    "prodj": "PRO DJ",
    "highclass": "HIGH CLASS",
    "professional": "PROFESSIONAL",
    "trendsetter": "TREND SETTER",
    "headliner": "HEADLINER",
    "showstopper": "SHOWSTOPPER",
    "beatmaestro": "BEAT MAESTRO",
    "lord": "THE LORD OF DJMAX"
}

DJPOWER_TIER_MAP = [
    ["beatmaestro",  [9970, 9950, 9930, 9900]],
    ["showstopper",  [9850, 9800, 9750, 9700]],
    ["headliner",    [9650, 9600, 9500, 9400]],
    ["trendsetter",  [9300, 9200, 9100, 9000]],
    ["professional", [8900, 8800, 8700, 8600]],
    ["highclass",    [8400, 8200, 8000, 7800]],
    ["prodj",        [7600, 7400, 7200, 7000]],
    ["middleman",    [6800, 6600, 6400, 6200]],
    ["streetdj",     [6000, 5800, 5500, 5200]],
    ["rookie",       [4900, 4600, 4300, 4000]],
    ["amateur",      [3600, 3200, 2800, 2400]],
    ["trainee",      [2000, 1500, 1000,  500]],
]
