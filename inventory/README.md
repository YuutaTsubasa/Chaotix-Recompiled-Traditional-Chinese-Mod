# Text graphics inventory (phase 1)

Every graphic with English text found in Knuckles' Chaotix (32X) as run by
Knuckles' Chaotix Recompiled, for a Traditional Chinese mod made only of
replacement images (`Mods/Textures`, see the game repo's `docs/TEXTURE_MODS.md`).
Nothing is translated or drawn here.

- `inventory.json`: one entry per graphic (139). 32X entries give bank and
  frame (the replacement file is `32x_<bank>_<frame>.png`, or that cell of
  the sheet `32x_<bank>.png`); Mega Drive entries give the tile hashes
  (`md_<hash>.png`) and the screen box. Both decoded fonts are in `fonts`.
- `sheets/`: crops at 3x. `32x_<bank>_<frame>.png` is one sprite (dark grey =
  transparent), `md_<id>.png` the screen area of an MD item (Mega Drive layer
  only), `contact_*.png` all of a group on one page, `font_8x16_game_font.png`
  the menus' 8x16 font as decoded from the ROM.

## Count

| | entries | of which really need translating |
| --- | --- | --- |
| 32X sprites | 106 | ~95 (not: barcode, copyright, the 2 debug graphics, the HUD/special "!" sprites, the Lv1-5 suffixes if kept) |
| Mega Drive tile text | 33 | all, but see the blockers |

Grouped by scene (a shared graphic is listed once, under its first scene):

| Scene | Kind | Items |
| --- | --- | --- |
| SEGA logo, intro | 32X | no text but the SEGA logo itself (bank 30, and the waving logo); leave as is |
| Title screen | 32X bank 55 | logo halves 0a/0b (contain the tagline "FEATURING KNUCKLES THE ECHIDNA. / WELCOME TO THE NEXT LEVEL / IN 32X WORLD" and the PUSH START box), 09 PUSH START, 0d copyright |
| Title menu (SCENARIO QUEST / TRAINING / OPTIONS) | MD 8x8 font | 3 strings |
| OPTIONS | MD 8x8 font | CONTROL CONFIGURATION, 1P/2P TYPE 1, A:CALL, B:HOLD, C:JUMP, SOUND TEST, COLOR TEST, EXIT |
| SOUND TEST | MD | FM1-6, PSG1-3, PWM, "--- SOUND TEST ---" (low priority) |
| COLOR TEST | MD | "MARS", "MD", hex numbers: debug, not listed |
| DATA LOAD (Scenario Quest) | MD banners | DATA LOAD, NO SAVE, NEW, PLAY, DELETE, DATA n (header and the next slot's), time 0:00:00 (digits) |
| TRAINING zone select | MD | TRAINING banner, zone name (8x16 font), PLAY, EXIT |
| PLAY STYLE | MD | PLAY STYLE, 1P, 2P, 1P/CPU selectors, PLAYER SELECT banner |
| PLAYER SELECT | MD 8x16 font | PLAYER SELECT, character names (KNUCKLES THE ECHIDNA, MIGHTY THE ARMADILLO, ESPIO THE CHAMELEON, CHARMY BEE, VECTOR THE CROCODILE, BOMB THE MECHANIC, HEAVY THE MECHANIC: ASCII at ROM 0x3267A) |
| Title card (every level) | 32X bank 40 | L E V E L (07), one 200x52 picture per zone (08 Botanic Base, 09 Marina Madness, 0a Amazing Arena, 0b Techno Tower, 0c Speed Slider, 10 Isolated Island; each with "NEWTROGIC HIGH ZONE" above and "CHAOTIX" below), cast list (0d), barcode (0f) |
| HUD (levels, bonus, special, results) | 32X bank 13 | POINTS, RINGS, TIME, PAUSE(+!), LIMITS, ATTACK, HURRY, UP, SCORE, LEVEL (yellow) + red flashing copies of RINGS, TIME, LIMITS, ATTACK, SCORE, the HOLD! bubble, -DEMO-; digits are separate frames |
| Level end | 32X bank 23 | CLEAR on the goal sign (06) |
| Results / level messages | 32X bank 4A | 44 word sprites: YOU GOT THROUGH, TIME/RING/SECRET BONUS, TOTAL, SCORE UP!, PLAYER MISS, five zone names, Lv1-5, START THE CLOCK!, TO NEXT LEVEL! (yellow and white), GO FOR GOAL!, GET ENEMIES!, SCORE POINTS, FINISH, IT'S A NEW RECORD!, RINGS |
| Amazing Arena | 32X | NO CLEAR (3d_03), CHALLENGE AGAIN!! (29_23) |
| Techno Tower | 32X | LOCK ON (2d_02, 5 px letters) |
| World Entrance (lobby) | 32X | EXIT / PLAY signs (59_00/01), COMBI/CATCHER sign (58_00), attraction board NEWTROGIC HIGH ZONE / ATTRACTION INFORMATION (5e_00), CLEAR, LEVEL (5e_01/02) |
| Bonus stage | 32X bank 26 | 500 PTS., EXIT (3 colours), UP, DOWN blocks |
| Special stage | 32X bank 4D | TIME, COURSE, OUT, GOT .. pts!, BAD!, TOO, COOOOL, NEXT, !, TO GO, SPHERES, BLUE, GET (+ HUD RINGS / LIMITS) |
| Debug | 32X bank 24 | "Test", skull with text (low priority) |

There is no game over, time over or continue screen in this game (no lives,
no time limit), and the monitor icons (bank 12) have no letters.

## Whole-word images vs letter fonts

**Easy, whole-word or whole-picture images (all 106 32X items).** Every 32X
text is its own sprite: a word (HUD, results, special stage), a phrase
(PUSH START, CHALLENGE AGAIN!!) or a whole picture (title card zone names,
signs). A replacement can be any picture of the same size, or larger towards
the right and down (not left or up), up to 127 px from the draw position.

Things to watch:

- **Phrases built from word sprites** (results bank 4A, special stage bank
  4D): "YOU GOT THROUGH" is three sprites, "IT'S A NEW RECORD!" four, "GET
  nn BLUE SPHERES TO GO" five plus digits, and the game places each word.
  Chinese word order differs, so the practical approach is to draw the whole
  Chinese phrase into the first word's sprite (it may grow right/down) and
  make the other word sprites empty (transparent), as long as the phrase
  fits within 127 px of the first word's position and does not run into the
  numbers. The same words are shared by several phrases (TO, NEXT, LEVEL!,
  SCORE exist twice, in yellow and white, which helps). Which phrases are
  shown when (START THE CLOCK!, GO FOR GOAL!, GET ENEMIES!, ... are probably
  the attraction objectives / TIME ATTACK messages) was not seen on screen
  and should be checked before choosing the split.
- **Results zone name + Lv suffix**: separate sprites (zone name 4a_0c-10,
  then Lv1-5 4a_11-15).
- **Title logo**: the tagline and the PUSH START box are inside the two
  logo halves 55_0a / 55_0b, and the words cross the split.
- **Title card**: the 200x52 picture holds three lines; the zone name has
  about 24 px of height, the two small lines about 7 px.
- **COMBI / CATCHER sign (58_00)**: both words are drawn in the same 46x8
  area in different palette indices and palette cycling alternates them; a
  replacement must use the same two index sets.
- **Special stage words are drawn scaled** (they zoom in the tube); the
  replacement is scaled the same way.
- **Colours**: pixel values are 32X palette indices (keep to the values the
  dump uses; 0 transparent). The red HUD words are separate frames.

**Hard, reusable letter fonts (Mega Drive layer).**

- **8x8 menu font** (title menu, OPTIONS): one tile per letter, shared by
  every string; the same "O" tile is CONTROL, CONFIGURATION, OPTIONS, SOUND,
  COLOR. Strings come from tables (OPTIONS at ROM 0x6C0E, letters stored as
  ASCII - 0x20, so 0x21 = 'A'). Tile replacement keys on the tile's
  pixels, so a replaced "O" changes every O. **Cannot be translated word by
  word with image replacement.**
- **8x16 game font** (TRAINING zone names, PLAYER SELECT header and the
  character names): 47 glyphs of two tiles each (ROM 0x2C4B20, Nemesis; hashes
  of all 94 tiles are in `inventory.json` > `fonts`), written by code from
  ASCII strings. Same problem.
- **Banners** (DATA LOAD, TRAINING, PLAY STYLE, PLAYER SELECT, PLAY,
  DELETE, EXIT, NO SAVE, NEW, DATA n): big letters 3-4 tiles tall, each word
  drawn as a block of tiles. They are not a one-tile-per-letter font, but
  tiles of identical letter runs are shared between banners: PLAY (DATA
  LOAD screen) and PLAY (TRAINING) are the same tiles and share 7 tiles with
  the PLAYER SELECT banner; DELETE shares 7 with PLAYER SELECT; DATA LOAD
  shares tiles with DATA n and TRAINING. A banner can be redrawn as a
  picture of the same tile area, but every banner sharing a tile changes
  with it, so all banners must be designed together (and some shared tiles
  may force a compromise).
- **SOUND TEST** labels: letters reused between labels; debug-like screen,
  low priority.

Ways around the font problem (none is image-only today): a ROM patch that
points the strings at new tiles (`docs/ROM_PATCHES.md` in the game repo),
or a new feature of the recompiled game's mod system, e.g. replacing a
whole screen region / name-table area or a string instead of a tile. This
needs a decision before phase 2.

## Heights available

| Graphic | Height (px) | Note |
| --- | --- | --- |
| HUD words (bank 13) | 14 (13 for -DEMO-) | width 16-48 |
| Results words (4A) | 15; zone names 23 | |
| Special stage words (4D) | 15 (shown scaled up) | |
| Title card zone name (40) | ~24 inside a 52 px picture; small lines ~7 | width 200 |
| CHALLENGE AGAIN!!, PUSH START, copyright | 8-10 | |
| Title tagline (in the logo) | ~6 per line, 3 lines | |
| LOCK ON, attraction CLEAR / LEVEL | 5-7 | needs a tiny pixel font or icons |
| Signs and blocks (lobby, bonus, goal) | 26-50 picture, letters ~12-20 | |
| MD 8x8 menu font | 8 (7 px glyphs) | |
| MD 8x16 font | 16 (15 px glyphs) | |
| MD banners | 24-32 | |

So: 14-16 px for most words (enough for a 12-14 px hand-tuned Chinese pixel
font, or 15-16 px glyphs filling the box), 23-24 px for zone names, and a
few 5-8 px spots where Chinese needs either a very small font, a larger
replacement growing down/right, or keeping the English.

## Blockers and constraints

1. Letter fonts on the Mega Drive layer (above): title menu, OPTIONS,
   TRAINING zone names, PLAYER SELECT names cannot be translated by tile
   replacement alone.
2. MD tile replacements are 8x8, indices 1-15 of the tile's palette line (0
   transparent), recognised by the tile's pixels wherever it is used, in
   whatever palette line it is drawn with. Each banner keeps its tile
   layout; text cannot grow beyond the tiles the game draws there.
3. 32X replacements cannot grow left or up, must stay within 127 px of the
   draw position, and use the palette as it is (no new colours).
4. Phrases made of word sprites keep the game's word positions (see above).
5. The tile hashes of MD items were found by matching dumped tiles against
   the Mega Drive layer screenshot; boxes may include a few background
   tiles. Confirm with DUMP GRAPHICS on the screen before drawing.

## Not reached

- **Ending and staff credits**: no stage-select entry; poking the game mode
  ($FFDFDE) from the title did not switch scenes (the handler sets it itself
  on exit). Needs a save near the end or a cheat-driven run
  (`FFE01B:06`, all Chaos Rings, is documented as leading to the ending).
- 2P mode screens, DATA LOAD with a used save (CLEAR / level marks), the
  DELETE confirmation, the TRAINING partner select after PLAYER SELECT.
- Where ATTACK, HURRY, UP, red SCORE and LEVEL (bank 13) and the yellow
  results messages (START THE CLOCK!, GO FOR GOAL!, ...) appear on screen:
  the graphics are inventoried from the banks, not seen in use.
- Level art of other acts (the export covered act 1 of each zone, Training,
  the intro, the lobby, the bonus and special stages); in-level signs in
  later acts could add a few items.

## How this was made

`chaotix_headless` from the game repo (Git Bash, `tools/env.sh`):
`--press` sequences for the menus, `--stage` for levels (place 0-7, 9 bonus,
10 special), the test recording `tests/recordings/finished_run.txt` for the
results screen, and at each scene `--shot` (full, `--layer md`, `--layer
32x`), `--dump-graphics` and `--export-sheets` (`tools/cap.sh NAME FRAME
ARGS`). The dumps are in `work/` (not committed). `tools/md_items.py`
matches dumped MD tiles against the MD-layer screenshots,
`tools/make_fonts.py` decodes the 8x16 font, and `tools/build_inventory.py`
writes `inventory.json` and `sheets/`. The helper scripts expect to be run
from the repository root (md_items.py, make_fonts.py from inside `work/`).
