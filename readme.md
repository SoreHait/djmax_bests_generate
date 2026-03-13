# DJMAX Score Image Generator

The **ONLY** module you should care: `djmax_bests.generate`.

This library connects to [V-ARCHIVE](https://v-archive.net/) as data source.

## Top 100 Generators

- `generate.generate_bests(username, bmode)`
    - Generate the user's top 100 chart.
    - Returns a `PIL.Image` with the provided username and button mode (4568).

- `generate.generate_bests_theoretical(bmode)`
    - Generate the theoretical (max djpower) top 100 chart of the current version.
    - Returns a `PIL.Image` with the provided button mode.

## Scorelist Generators

- `generate.generate_scorelist(username, bmode, is_sc, level)`
    - Generate the user's score overview of a certain level.
    - Returns a `PIL.Image` with the provided username and button mode of a certain level. The `is_sc` param (boolean) is used to indicate whether the `level` is in SC levels.

- `generate.generate_scorelist_new(username, bmode)`
    - Generate the user's score overview of new songs in current version, only in SC difficulty.
    - Returns a `PIL.Image` with the provided username and button mode.

## Utilities

`prefetch_covers.py`: cache all missing covers.

# Troubleshooting
- `ValueError: list.remove(x)` / wrong convert multiplier
    - Delete all files under `cache` folder, or call `api_handler.remove_cache()`.
