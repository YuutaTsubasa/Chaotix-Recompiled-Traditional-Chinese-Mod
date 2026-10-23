Knuckles' Chaotix Recompiled - Traditional Chinese (zh-TW) translation mod
=========================================================================
Version 1.1.0 (2026-10-23)

納克魯斯 卡歐提斯 繁體中文化模組

What it is
----------
A graphics mod for Knuckles' Chaotix Recompiled that redraws the game's
English text in Traditional Chinese (Taiwan), using the names and terms of
SEGA's official Traditional Chinese where they exist. It is a set of
replacement pictures, packed as a mod pack; the game and the ROM are not
changed, and removing the files brings the English back.

Requirements
------------
- Knuckles' Chaotix Recompiled 0.9.0 or later. This version is a mod pack
  (a folder of its own in Mods), which older versions of the game don't
  read. For 0.7.1 to 0.8.x, use version 1.0.1 of this mod.
- Your own copy of the Knuckles' Chaotix (32X) ROM, installed in Knuckles'
  Chaotix Recompiled as usual. No ROM is included.

Install
-------
Copy the "Mods" folder of this package into the game's user data folder,
so that this mod ends up in its own folder, Mods/ChaotixZhTW, there (merge
it with the Mods folder that may already be there). Then start the game.
OPTIONS > EXTRAS > MODS lists it as "Traditional Chinese (zh-TW)", where it
can be turned off and on, or moved above or below other mods.

If you installed 1.0.x of this mod before, delete its files from
Mods/Textures first (32x_*.png, mdtext_*, mdsprite_*): loose files there
override every mod pack.

The user data folder is:
- Windows: %APPDATA%\ChaotixRecompiled\ChaotixRecompiled
  (paste this into the Explorer address bar)
- Linux:   ~/.local/share/ChaotixRecompiled/ChaotixRecompiled
- macOS:   ~/Library/Application Support/ChaotixRecompiled/ChaotixRecompiled
- Android: the Mods folder is ChaotixRecompiled/Mods in the phone's storage
  once you allow it (OPTIONS > EXTRAS > MODS > MODS FOLDER opens Android's
  "All files access" page), and Android/data/org.chaotixrecompiled/files/Mods
  until then. Copy the contents of this package's Mods folder (the
  ChaotixZhTW folder) into it.
- iOS / iPadOS: the app's Documents, which the Files app shows as
  On My iPhone (iPad) > Chaotix; copy the Mods folder there.
- A portable install (started with --user-dir DIR): DIR.

To turn it off, use OPTIONS > EXTRAS > MODS. To uninstall, delete the
Mods/ChaotixZhTW folder.

What is translated
------------------
- Title screen: the lines under the logo and PUSH START; the title menu
  (SCENARIO QUEST, TRAINING, OPTIONS).
- OPTIONS: the control configuration (TYPE, CALL / HOLD / JUMP /
  HOLD&JUMP), SOUND TEST, COLOR TEST, EXIT; the SOUND TEST title bar
  (--- SOUND TEST ---) and S.E.
- DATA LOAD: the banners (DATA LOAD, PLAY, DELETE), the save slots (NO
  SAVE, NEW, DATA 1-3, CLEAR), the SAVEMODE box (AUTO, MANUAL) and the
  DELETE confirmation (REALLY?, NO, YES).
- TRAINING, PLAY STYLE, PLAYER SELECT, COMBI SELECT: the banners, the zone
  names, CPU, the headers and the character names.
- In the game: the HUD (SCORE, TIME, RINGS), the zone title cards, PAUSE,
  the results (bonuses, TOTAL, CLEAR), the goal sign, the World Entrance
  signs and attraction board, the EXIT / UP / DOWN blocks, the special and
  bonus stage messages, the speech bubbles, -DEMO-.

Kept in English
---------------
- The CHAOTIX logo, the (c)SEGA copyright line, the title card's barcode.
- Lv (Lv1-Lv5, and the Lv. marks of a used save slot), 1P / 2P, the
  A: / B: / C: button letters, the FM / PSG / PWM channel labels of the
  SOUND TEST.
- The SOUND TEST song titles.
- The cast list on the title cards (ESPIO!! KNUCKLES!! ...): too small to
  hold Chinese.
- Digits and times (and the number after S.E.); the "!" after PAUSE and in
  the special stage; the COLOR TEST screen and the debug graphics.

Not seen in the game
--------------------
The names of the hidden characters Bomb (炸彈) and Heavy (海威) on the
character select, and the TRAINING zone names other than Isolated Island
(TRAINING lists only the zones a save has reached), are made the same way
as the ones that were checked, but were not seen in the game.

Game data in this package
-------------------------
No ROM data is included, except: the pictures use the game's own colour
palettes, and in the frames where the text sits on a picture, the picture
around the text is the original sprite art with the English letters
removed. Those frames are:
- 32x_13_26: the HOLD! speech bubble
- 32x_13_40: -DEMO-
- 32x_23_06: the goal sign (CLEAR)
- 32x_26_01: 500 PTS.
- 32x_26_1a, 32x_26_1b, 32x_26_1c: the EXIT block
- 32x_26_20, 32x_26_21: the UP and DOWN blocks
- 32x_29_23: CHALLENGE AGAIN!! (its arrows)
- 32x_2d_02: LOCK ON
- 32x_3d_03: NO CLEAR (its dots)
- 32x_40_07: L E V E L (title card)
- 32x_40_08, 32x_40_09, 32x_40_0a, 32x_40_0b, 32x_40_0c, 32x_40_10: the
  title cards' zone name panels
- 32x_4d_03: GOT .... pts!
- 32x_55_0a, 32x_55_0b: the title screen's panel under the logo
- 32x_58_00: the COMBI / CATCHER sign
- 32x_59_00, 32x_59_01: the World Entrance EXIT and PLAY signs
- 32x_5e_00: the World Entrance attraction board
All the other pictures are drawn from scratch (the text and plain shapes).
The mdtext_ and mdsprite_ .txt files list hashes (fingerprints) of the
game's tiles, which the game uses to find the text; they hold no graphics.

Fonts
-----
The Chinese is drawn with these fonts, all under the SIL Open Font License
1.1 (the licences are in the licenses folder):
- Noto Sans TC Black (Google, Adobe) - the menus and most 14-22 px text
- Glow Sans TC Condensed Heavy (Project Welai) - the 32X zone names
- Fusion Pixel 8px (TakWolf) - the small text; it includes glyphs from
  Boutique Bitmap 7x7, Galmuri, Misaki and Miseki Bitmap, whose licences
  are in licenses/fusion-pixel-font-parts
No font files are included, only pictures drawn with them.

Credits
-------
Translation and graphics: YuutaTsubasa
Made with the help of Claude (Anthropic).

Knuckles' Chaotix is (c) SEGA. This is an unofficial fan translation, not
affiliated with or endorsed by SEGA.
