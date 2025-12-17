from decimal import Decimal
from djmax_bests import api_handler, util


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

songdb = api_handler.fetch_song_db()
_4b_b_counts = {}
_5b_b_counts = {}
_6b_b_counts = {}
_8b_b_counts = {}

_4b_n_counts = {}
_5b_n_counts = {}
_6b_n_counts = {}
_8b_n_counts = {}

for song in songdb.root:
    if song.patterns.BMode_4.MX:
        coeff = diff_coeff(song.patterns.BMode_4.MX.level, False)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _4b_n_counts:
                _4b_n_counts[coeff] += 1
            else:
                _4b_n_counts[coeff] = 1
        else:
            if coeff in _4b_b_counts:
                _4b_b_counts[coeff] += 1
            else:
                _4b_b_counts[coeff] = 1
    if song.patterns.BMode_4.SC:
        coeff = diff_coeff(song.patterns.BMode_4.SC.level, True)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _4b_n_counts:
                _4b_n_counts[coeff] += 1
            else:
                _4b_n_counts[coeff] = 1
        else:
            if coeff in _4b_b_counts:
                _4b_b_counts[coeff] += 1
            else:
                _4b_b_counts[coeff] = 1

    if song.patterns.BMode_5.MX:
        coeff = diff_coeff(song.patterns.BMode_5.MX.level, False)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _5b_n_counts:
                _5b_n_counts[coeff] += 1
            else:
                _5b_n_counts[coeff] = 1
        else:
            if coeff in _5b_b_counts:
                _5b_b_counts[coeff] += 1
            else:
                _5b_b_counts[coeff] = 1
    if song.patterns.BMode_5.SC:
        coeff = diff_coeff(song.patterns.BMode_5.SC.level, True)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _5b_n_counts:
                _5b_n_counts[coeff] += 1
            else:
                _5b_n_counts[coeff] = 1
        else:
            if coeff in _5b_b_counts:
                _5b_b_counts[coeff] += 1
            else:
                _5b_b_counts[coeff] = 1

    if song.patterns.BMode_6.MX:
        coeff = diff_coeff(song.patterns.BMode_6.MX.level, False)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _6b_n_counts:
                _6b_n_counts[coeff] += 1
            else:
                _6b_n_counts[coeff] = 1
        else:
            if coeff in _6b_b_counts:
                _6b_b_counts[coeff] += 1
            else:
                _6b_b_counts[coeff] = 1
    if song.patterns.BMode_6.SC:
        coeff = diff_coeff(song.patterns.BMode_6.SC.level, True)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _6b_n_counts:
                _6b_n_counts[coeff] += 1
            else:
                _6b_n_counts[coeff] = 1
        else:
            if coeff in _6b_b_counts:
                _6b_b_counts[coeff] += 1
            else:
                _6b_b_counts[coeff] = 1

    if song.patterns.BMode_8.MX:
        coeff = diff_coeff(song.patterns.BMode_8.MX.level, False)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _8b_n_counts:
                _8b_n_counts[coeff] += 1
            else:
                _8b_n_counts[coeff] = 1
        else:
            if coeff in _8b_b_counts:
                _8b_b_counts[coeff] += 1
            else:
                _8b_b_counts[coeff] = 1
    if song.patterns.BMode_8.SC:
        coeff = diff_coeff(song.patterns.BMode_8.SC.level, True)
        if util.is_new(song.dlc_code, song.songid):
            if coeff in _8b_n_counts:
                _8b_n_counts[coeff] += 1
            else:
                _8b_n_counts[coeff] = 1
        else:
            if coeff in _8b_b_counts:
                _8b_b_counts[coeff] += 1
            else:
                _8b_b_counts[coeff] = 1

_4b_b_counts = [(k, v) for k, v in sorted(_4b_b_counts.items(), reverse=True)]
_5b_b_counts = [(k, v) for k, v in sorted(_5b_b_counts.items(), reverse=True)]
_6b_b_counts = [(k, v) for k, v in sorted(_6b_b_counts.items(), reverse=True)]
_8b_b_counts = [(k, v) for k, v in sorted(_8b_b_counts.items(), reverse=True)]

_4b_n_counts = [(k, v) for k, v in sorted(_4b_n_counts.items(), reverse=True)]
_5b_n_counts = [(k, v) for k, v in sorted(_5b_n_counts.items(), reverse=True)]
_6b_n_counts = [(k, v) for k, v in sorted(_6b_n_counts.items(), reverse=True)]
_8b_n_counts = [(k, v) for k, v in sorted(_8b_n_counts.items(), reverse=True)]

_4b_max = 0
_4b_b_max_count = 0
_4b_n_max_count = 0
for coeff, count in _4b_b_counts:
    if count + _4b_b_max_count > 70:
        count = 70 - _4b_b_max_count
    _4b_max += djpower_pp(coeff) * count
    _4b_b_max_count += count
    if _4b_b_max_count >= 70:
        break
for coeff, count in _4b_n_counts:
    if count + _4b_n_max_count > 30:
        count = 30 - _4b_n_max_count
    _4b_max += djpower_pp(coeff) * count
    _4b_n_max_count += count
    if _4b_n_max_count >= 30:
        break

_5b_max = 0
_5b_b_max_count = 0
_5b_n_max_count = 0
for coeff, count in _5b_b_counts:
    if count + _5b_b_max_count > 70:
        count = 70 - _5b_b_max_count
    _5b_max += djpower_pp(coeff) * count
    _5b_b_max_count += count
    if _5b_b_max_count >= 70:
        break
for coeff, count in _5b_n_counts:
    if count + _5b_n_max_count > 30:
        count = 30 - _5b_n_max_count
    _5b_max += djpower_pp(coeff) * count
    _5b_n_max_count += count
    if _5b_n_max_count >= 30:
        break

_6b_max = 0
_6b_b_max_count = 0
_6b_n_max_count = 0
for coeff, count in _6b_b_counts:
    if count + _6b_b_max_count > 70:
        count = 70 - _6b_b_max_count
    _6b_max += djpower_pp(coeff) * count
    _6b_b_max_count += count
    if _6b_b_max_count >= 70:
        break
for coeff, count in _6b_n_counts:
    if count + _6b_n_max_count > 30:
        count = 30 - _6b_n_max_count
    _6b_max += djpower_pp(coeff) * count
    _6b_n_max_count += count
    if _6b_n_max_count >= 30:
        break

_8b_max = 0
_8b_b_max_count = 0
_8b_n_max_count = 0
for coeff, count in _8b_b_counts:
    if count + _8b_b_max_count > 70:
        count = 70 - _8b_b_max_count
    _8b_max += djpower_pp(coeff) * count
    _8b_b_max_count += count
    if _8b_b_max_count >= 70:
        break
for coeff, count in _8b_n_counts:
    if count + _8b_n_max_count > 30:
        count = 30 - _8b_n_max_count
    _8b_max += djpower_pp(coeff) * count
    _8b_n_max_count += count
    if _8b_n_max_count >= 30:
        break

print('4', _4b_max)
print('5', _5b_max)
print('6', _6b_max)
print('8', _8b_max)
