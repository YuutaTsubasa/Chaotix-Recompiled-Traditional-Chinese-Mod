# Knuckles' Chaotix Recompiled - Traditional Chinese Translation (繁體中文化)

A Traditional Chinese (zh-TW, Taiwan) translation mod for [Knuckles' Chaotix Recompiled](https://github.com/YuutaTsubasa/ChaotixRecompiled). It covers the HUD, the zone title cards, the results screen, the special and bonus stages, the World Entrance signs, the title screen and every menu. It is a texture mod: the ROM is not changed.

《Knuckles' Chaotix Recompiled》的繁體中文化模組。HUD、關卡標題卡、結算畫面、特別關卡與獎勵關卡、世界入口的看板、標題畫面以及所有選單都已中文化。這是貼圖模組，不需要修改 ROM。

## Download and install / 下載與安裝

- Download the zip from [Releases](https://github.com/YuutaTsubasa/Chaotix-Recompiled-Traditional-Chinese-Mod/releases).
- It needs Knuckles' Chaotix Recompiled **0.7.1 or later** and your own Knuckles' Chaotix (Japan, USA) ROM.
- Copy the zip's `Mods` folder into the game's user data folder (Windows: `%APPDATA%\ChaotixRecompiled\ChaotixRecompiled`). The other platforms are listed in [mod/README_zhTW.txt](mod/README_zhTW.txt).

需要 Knuckles' Chaotix Recompiled **0.7.1 以上**和自己的 ROM。把 zip 裡的 `Mods` 資料夾複製到遊戲的使用者資料夾即可。

## Repository layout

| Path | What it is |
| --- | --- |
| `mod/` | The finished mod: `Mods/Textures`, the player README and the font licences |
| `text/glossary.json` | The approved terms (SEGA's official Traditional Chinese names where they exist) |
| `text/sprites/`, `text/mdtext/`, `text/mdsprite/` | One spec per replaced graphic: English, Chinese, font and layout |
| `tools/` | Python (Pillow) tools that draw the Chinese text and build the mod |
| `inventory/` | The list of every English text graphic in the game (text and hashes only) |
| `release/` | Changelog and the GameBanana page draft |

## Building

The tools need the original sprite sheets and dumps exported from your own ROM with Knuckles' Chaotix Recompiled (`chaotix_headless --export-sheets` / `--dump-graphics`) in `work/`, plus the fonts (Noto Sans TC, Glow Sans TC, Fusion Pixel 8px). Those exports are game data and are not part of this repository. Run `python tools/build.py`, then `python tools/check_text.py`.

## Credits and licences

- **Translation and graphics:** YuutaTsubasa, made with the help of Claude (Anthropic).
- **Fonts:** Noto Sans TC, Glow Sans TC and Fusion Pixel 8px, all under the SIL Open Font License 1.1. Their licences are in `mod/licenses/`.
- **Licence:** the tools, specs and translation text are under the [MIT License](LICENSE).
- **Game:** Knuckles' Chaotix and its text, graphics and characters belong to SEGA. This is an unofficial, non-commercial fan translation.
- **Game data in this repository:** the images use the game's palettes, and a few frames keep the original sprite art around the text (listed in `mod/README_zhTW.txt`). There is no ROM data otherwise.
