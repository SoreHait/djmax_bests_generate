# DJMAX Score Image Generator

The **ONLY** module you should care: `djmax_bests.generate`.

This library connects to v-archive as data source.

## Top 100 Generator

`generate.generate_bests`: returns a `PIL.Image` with the provided username and button mode (4568).

## Scorelist Generator

`generate.generate_scorelist`: returns a `PIL.Image` with the provided username and button mode (4568) of a certain level. Pass in a bool `is_sc` to indicate whether the `level` is in SC levels.

# Utilities

`prefetch_covers.py`: fetch all missing covers.
