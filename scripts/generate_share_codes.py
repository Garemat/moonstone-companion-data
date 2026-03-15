#!/usr/bin/env python3
"""
Generate and write correct 5-character share codes into all compendium JSON files.

Share code format:
  [0] Type:    A=Character, B=Campaign, C=Upgrade
  [1] Faction: A=Commonwealth, B=Dominion, C=Leshavult, D=Shades,
               E=Commonwealth+Dominion, F=Commonwealth+Leshavult,
               G=Commonwealth+Shades, H=Dominion+Leshavult,
               I=Dominion+Shades, J=Leshavult+Shades,
               K=All four factions
  [2-4] ID:    3-digit decimal ID, each digit replaced A=0 … J=9
"""

import json
import glob
import re
import sys

FACTION_MAP = {
    frozenset(["COMMONWEALTH"]):                                          "A",
    frozenset(["DOMINION"]):                                             "B",
    frozenset(["LESHAVULT"]):                                            "C",
    frozenset(["SHADES"]):                                               "D",
    frozenset(["COMMONWEALTH", "DOMINION"]):                             "E",
    frozenset(["COMMONWEALTH", "LESHAVULT"]):                            "F",
    frozenset(["COMMONWEALTH", "SHADES"]):                               "G",
    frozenset(["DOMINION", "LESHAVULT"]):                                "H",
    frozenset(["DOMINION", "SHADES"]):                                   "I",
    frozenset(["LESHAVULT", "SHADES"]):                                  "J",
    frozenset(["COMMONWEALTH", "DOMINION", "LESHAVULT", "SHADES"]):     "K",
}

DIGIT_MAP = {str(i): chr(ord("A") + i) for i in range(10)}


def encode_id(item_id: int) -> str:
    padded = str(item_id).zfill(3)
    if len(padded) > 3:
        raise ValueError(f"ID {item_id} exceeds 3 digits — extend the encoding scheme")
    return "".join(DIGIT_MAP[d] for d in padded)


def make_share_code(type_letter: str, factions: list, item_id: int) -> str:
    key = frozenset(factions)
    faction_letter = FACTION_MAP.get(key)
    if faction_letter is None:
        raise ValueError(f"Unknown faction combination: {sorted(factions)}")
    return type_letter + faction_letter + encode_id(item_id)


errors = []
updated = 0

for glob_pattern, type_letter, kind in [
    ("characters/**/*.json", "A", "character"),
    ("campaign/*.json",      "B", "campaign"),
    ("upgrades/*.json",      "C", "upgrade"),
]:
    for path in sorted(glob.glob(glob_pattern, recursive=True)):
        with open(path) as f:
            data = json.load(f)

        item_id = data.get("id")
        factions = data.get("factions", [])

        if item_id is None:
            errors.append(f"{path}: missing 'id'")
            continue
        if not factions:
            errors.append(f"{path}: empty 'factions' — cannot compute share code")
            continue

        try:
            code = make_share_code(type_letter, factions, item_id)
        except ValueError as e:
            errors.append(f"{path}: {e}")
            continue

        if data.get("shareCode") != code:
            content = open(path).read()
            new_content = re.sub(
                r'"shareCode"\s*:\s*"[^"]*"',
                f'"shareCode": "{code}"',
                content
            )
            with open(path, "w") as f:
                f.write(new_content)
            updated += 1

if errors:
    print(f"\n{len(errors)} error(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)

print(f"Done. {updated} file(s) updated.")
