# DJMAX Score Image Generator

This library use [V-ARCHIVE](https://v-archive.net/) as data source.

## Top 100 Generators

- `generate.generate_bests(username, bmode)`
    - Generate the user's top 100 chart.
    - `username`: the user's V-ARCHIVE account username.
    - `bmode`: button mode, can be one of 4, 5, 6, 8.

- `generate.generate_bests_theoretical(bmode)`
    - Generate the theoretical (max djpower) top 100 chart of the current version.
    - `bmode`: button mode, can be one of 4, 5, 6, 8.

## Scorelist Generators

- `generate.generate_scorelist(username, bmode, is_sc, level)`
    - Generate the user's score overview of a certain level.
    - `username`: the user's V-ARCHIVE account username.
    - `bmode`: button mode, can be one of 4, 5, 6, 8.
    - `is_sc`: (boolean) indicate whether the `level` is in SC levels.
    - `level`: the level to generate, 1-15.

- `generate.generate_scorelist_new(username, bmode, diff)`
    - Generate the user's score overview of new songs in current version.
    - `username`: the user's V-ARCHIVE account username.
    - `bmode`: button mode, can be one of 4, 5, 6, 8.
    - `diff`: difficulty, can be one of NM, HD, MX, SC.

- `generate.generate_scorelist_pack(username, bmode, diff, pack)`
    - Generate the user's score overview of songs in a certain pack.
    - `username`: the user's V-ARCHIVE account username.
    - `bmode`: button mode, can be one of 4, 5, 6, 8.
    - `diff`: difficulty, can be one of NM, HD, MX, SC.
    - `pack`: the pack to generate, as in V-ARCHIVE's `dlcCode`.
    - **NOTE:** You should validate the `pack` param before passing it in, the full dlc list can be retrieved with `api_handler.fetch_dlc_list()`.

- `generate.generate_scorelist_pp(username, bmode)`
    - Generate the user's perfect-played score overview.
    - `username`: the user's V-ARCHIVE account username.
    - `bmode`: button mode, can be one of 4, 5, 6, 8.

## Utilities

`prefetch_covers.py`: cache all missing covers.

# Troubleshooting

- `ValueError: list.remove(x)` / wrong convert multiplier / anything outdated
    - Delete all files under `cache` folder, or call `api_handler.remove_cache()`.
