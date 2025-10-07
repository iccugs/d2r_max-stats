#!/usr/bin/env python3
# set_stats_and_hpmp.py
# Minimal: set STR/ENE/DEX/VIT to <stat_val> (default 999) and optionally set HP/Mana display values.
# Recomputes .d2s checksum and writes <orig>_modified.d2s (backups original to .bak).
import sys
from pathlib import Path

ATTRIBUTES_OFFSET = 0x2FD
CHK_OFFSET = 0x0C
SECTION_HEADER = bytes([0x67, 0x66])
SECTION_TRAILER = 0x1FF

# bitlengths per STAT_KEY (index 0..3 are STR/ENE/DEX/VIT; 6..9 are HP/MaxHP/Mana/MaxMana)
STAT_BITLENGTH = [10,10,10,10,10,8,21,21,21,21,21,21,7,32,25,25]
IDX_STR, IDX_ENE, IDX_DEX, IDX_VIT = 0,1,2,3
IDX_HP, IDX_MAXHP, IDX_MANA, IDX_MAXMANA = 6,7,8,9
MAX_21BIT = (1 << 21) - 1

def read_bits(arr, pos, n):
    v = 0
    for i in range(n):
        if pos['byte'] >= len(arr):
            raise EOFError("read past EOF")
        b = arr[pos['byte']]
        bit = (b >> pos['bit']) & 1
        v |= (bit << i)
        pos['bit'] += 1
        if pos['bit'] == 8:
            pos['bit'] = 0
            pos['byte'] += 1
    return v

def write_bits(arr, pos, n, value):
    for i in range(n):
        if pos['byte'] >= len(arr):
            raise EOFError("write past EOF")
        bit = (value >> i) & 1
        b = arr[pos['byte']]
        b &= ~(1 << pos['bit'])
        b |= (bit << pos['bit'])
        arr[pos['byte']] = b
        pos['bit'] += 1
        if pos['bit'] == 8:
            pos['bit'] = 0
            pos['byte'] += 1

def compute_checksum(barr, chk_off=CHK_OFFSET):
    arr = bytearray(barr)
    arr[chk_off:chk_off+4] = b'\x00\x00\x00\x00'
    s = 0
    for byte in arr:
        s = ((s << 1) | (s >> 31)) & 0xFFFFFFFF
        s = (s + byte) & 0xFFFFFFFF
    return s

def set_stats_and_hpmp(path, stat_val=999, hp_display=None, mana_display=None):
    p = Path(path)
    if not p.exists():
        print("file not found:", p); return 1

    data = bytearray(p.read_bytes())
    # backup (always write)
    bak = p.with_suffix(p.suffix + ".bak")
    bak.write_bytes(data)

    if len(data) <= ATTRIBUTES_OFFSET:
        print("file too small / missing attributes offset"); return 1

    attr = bytearray(data[ATTRIBUTES_OFFSET:])  # mutable slice
    if len(attr) < 2 or attr[0:2] != SECTION_HEADER:
        print("attributes header missing at expected offset"); return 1

    # clamp stat_val to bitfield max for 10-bit stats
    stat_bitlen = STAT_BITLENGTH[IDX_STR]  # 10
    stat_bitmax = (1 << stat_bitlen) - 1
    stat_write = min(stat_val, stat_bitmax)
    if stat_write < 0:
        stat_write = 0

    # prepare stored HP/Mana values (fixed-point *256) if provided
    stored_hp = None
    stored_mana = None
    if hp_display is not None:
        stored_hp = int(float(hp_display) * 256)
        if stored_hp < 0: stored_hp = 0
        if stored_hp > MAX_21BIT: stored_hp = MAX_21BIT
    if mana_display is not None:
        stored_mana = int(float(mana_display) * 256)
        if stored_mana < 0: stored_mana = 0
        if stored_mana > MAX_21BIT: stored_mana = MAX_21BIT

    # Walk attributes: write stats and hp/mana where encountered
    pos = {'byte': 2, 'bit': 0}
    for _ in range(len(STAT_BITLENGTH) + 20):
        header = read_bits(attr, pos, 9)
        if header == SECTION_TRAILER:
            break
        if header >= len(STAT_BITLENGTH):
            break
        bl = STAT_BITLENGTH[header]
        if header in (IDX_STR, IDX_ENE, IDX_DEX, IDX_VIT):
            # write stat_write (clamped)
            write_bits(attr, pos, bl, stat_write)
        elif header in (IDX_HP, IDX_MAXHP) and stored_hp is not None:
            write_bits(attr, pos, bl, stored_hp)
        elif header in (IDX_MANA, IDX_MAXMANA) and stored_mana is not None:
            write_bits(attr, pos, bl, stored_mana)
        else:
            # skip
            _ = read_bits(attr, pos, bl)

    # assemble final buffer
    outbuf = bytearray(data)
    outbuf[ATTRIBUTES_OFFSET:ATTRIBUTES_OFFSET+len(attr)] = attr

    # recompute checksum and write
    chk = compute_checksum(outbuf, CHK_OFFSET)
    outbuf[CHK_OFFSET:CHK_OFFSET+4] = chk.to_bytes(4, "little")

    outpath = p.with_name(p.stem + "_modified" + p.suffix)
    outpath.write_bytes(outbuf)

    # minimal report
    print("Wrote:", outpath)
    print("Backup:", bak)
    return 0

def usage():
    print("usage: set_stats_and_hpmp.py <file.d2s> [stat_val] [hp_display] [mana_display]")
    print("  stat_val default: 999")
    print("  hp_display/mana_display are display numbers (e.g. 5000) converted to stored value *256 and clamped")
    print("examples:")
    print("  python3 set_stats_and_hpmp.py /path/to/char.d2s")
    print("  python3 set_stats_and_hpmp.py /path/to/char.d2s 999 5000 5000")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage(); sys.exit(1)
    filep = sys.argv[1]
    statv = int(sys.argv[2]) if len(sys.argv) >= 3 else 999
    hpv = float(sys.argv[3]) if len(sys.argv) >= 4 else None
    mpv = float(sys.argv[4]) if len(sys.argv) >= 5 else None
    sys.exit(set_stats_and_hpmp(filep, statv, hpv, mpv))
