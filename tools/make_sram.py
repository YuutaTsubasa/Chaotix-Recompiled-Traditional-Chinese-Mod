"""Write cartridge saves with cleared zones, to reach the screens of a used
save slot (DATA LOAD's CLEAR / Lv. marks, the DELETE confirmation):

    python tools/make_sram.py     -> work/p4/t2.srm, work/p4/t7.srm

then `chaotix_headless --sram work/p4/t2.srm ...` (tools/cap_sprites.sh,
tools/render_preview.sh). Found by tracing the game's save code: 0x100
bytes, kept twice (SRAM 0x000 and 0x100), a long checksum first (see ck();
$8BE37C), each slot 32 bytes from offset 4, whose first word holds 3 bits
per zone (MSB first: 1-5 = Lv. n, 6-7 = CLEAR); the 24 six-byte records
from 0x30 are what the game writes into an empty save. Training's zone
list did not change with any of this (it kept to ISOLATED ISLAND 1-4).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ck(buf):
    d0 = 0x4B52
    for i in range(0xFB, -1, -1):
        lo = (d0 & 0xFF) + buf[4 + 0xFB - i]
        d0 = (d0 & 0xFF00) | (lo & 0xFF)
        d0 = (d0 + i + (lo >> 8)) & 0xFFFF
    return d0


def blank():
    b = bytearray(0x100)
    for k in range(24):
        b[0x30 + 6 * k:0x36 + 6 * k] = bytes.fromhex("9efb00000001")
    return b


def slot_word(zones):
    w = 0
    for v in zones:
        w = (w << 3) | v
    return (w << 1).to_bytes(2, "big")


def make(name, slots):
    b = blank()
    for off, zones in slots:
        b[off:off + 2] = slot_word(zones)
    b[0:4] = ck(b).to_bytes(4, "big")
    out = bytes(b) * 2 + b"\xff" * (0x8000 - 0x200)
    path = os.path.join(ROOT, "work", "p4", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(out)
    print(path)


if __name__ == "__main__":
    assert ck(blank()) == 0xCA6F  # the game's own empty save
    make("t2.srm", [(o, [7] * 5) for o in (4, 0x24, 0x44, 0x64)])
    make("t7.srm", [(4, [0, 1, 2, 3, 4]), (0x24, [5, 6, 7, 1, 2]), (0x44, [3] * 5)])
