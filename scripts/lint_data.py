#!/usr/bin/env python3
"""
Lint the aggregated compendium.json produced by the build step.
Reads build/compendium.json and exits with code 1 if any errors are found.
"""

import json
import sys

VALID_FACTIONS = {"COMMONWEALTH", "DOMINION", "LESHAVULT", "SHADES"}
VALID_ABILITY_TYPES = {"Passive", "Active", "Arcane"}

FACTION_MAP = {
    frozenset(["COMMONWEALTH"]):                                      "A",
    frozenset(["DOMINION"]):                                         "B",
    frozenset(["LESHAVULT"]):                                        "C",
    frozenset(["SHADES"]):                                           "D",
    frozenset(["COMMONWEALTH", "DOMINION"]):                         "E",
    frozenset(["COMMONWEALTH", "LESHAVULT"]):                        "F",
    frozenset(["COMMONWEALTH", "SHADES"]):                           "G",
    frozenset(["DOMINION", "LESHAVULT"]):                            "H",
    frozenset(["DOMINION", "SHADES"]):                               "I",
    frozenset(["LESHAVULT", "SHADES"]):                              "J",
    frozenset(["COMMONWEALTH", "DOMINION", "LESHAVULT", "SHADES"]): "K",
}
DIGIT_MAP = {str(i): chr(ord("A") + i) for i in range(10)}


def expected_share_code(type_letter: str, factions: list, item_id: int) -> str | None:
    faction_letter = FACTION_MAP.get(frozenset(factions))
    if faction_letter is None:
        return None
    padded = str(item_id).zfill(3)
    id_code = "".join(DIGIT_MAP[d] for d in padded)
    return type_letter + faction_letter + id_code


def check_share_code(p: str, type_letter: str, factions: list, item_id: int, actual: str | None) -> None:
    if actual is None:
        error(p, "missing 'shareCode'")
        return
    if len(actual) != 5:
        error(p, f"'shareCode' must be 5 characters, got {actual!r}")
        return
    expected = expected_share_code(type_letter, factions, item_id)
    if expected is None:
        error(p, f"unknown faction combination {sorted(factions)} — cannot validate shareCode")
        return
    if actual != expected:
        error(p, f"'shareCode' {actual!r} does not match expected {expected!r}")

errors = []


def error(path: str, msg: str) -> None:
    errors.append(f"  [{path}] {msg}")


def coerce_id(raw) -> int | None:
    """Accept int or numeric string; return int, or None if invalid."""
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str):
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def check_id(p: str, raw, seen: dict, label: str = "id") -> int | None:
    if raw is None:
        return None
    cid = coerce_id(raw)
    if cid is None:
        error(p, f"'{label}' must be an integer or numeric string, got {raw!r}")
        return None
    if cid in seen:
        error(p, f"duplicate {label} {cid} (also at index {seen[cid]})")
        return None
    seen[cid] = p
    return cid


def check_factions(p: str, factions, required_non_empty: bool = True) -> None:
    if not isinstance(factions, list):
        error(p, "'factions' must be a list")
        return
    if required_non_empty and len(factions) == 0:
        error(p, "'factions' must be non-empty")
        return
    bad = [f for f in factions if f not in VALID_FACTIONS]
    if bad:
        error(p, f"unknown faction(s): {bad}")


def check_abilities(p: str, abilities) -> None:
    if not isinstance(abilities, list):
        error(p, "'abilities' must be a list")
        return
    for j, ab in enumerate(abilities):
        ap = f"{p} ability[{j}]"
        if "name" not in ab:
            error(ap, "missing required field 'name'")
        ability_type = ab.get("abilityType")
        if ability_type not in VALID_ABILITY_TYPES:
            error(ap, f"'abilityType' must be one of {VALID_ABILITY_TYPES}, got {ability_type!r}")
        if ability_type in ("Active", "Arcane"):
            for field in ("energyCost", "range"):
                if field not in ab:
                    error(ap, f"missing required field '{field}' for {ability_type} ability")
        if "arcaneOutcomes" in ab and not isinstance(ab["arcaneOutcomes"], list):
            error(ap, "'arcaneOutcomes' must be a list")


# ── compendium.json ─────────────────────────────────────────────────────────────

with open("build/compendium.json") as f:
    compendium = json.load(f)

if "version" not in compendium:
    errors.append("  [compendium] missing required field 'version'")
else:
    print(f"compendium version: {compendium['version']}")

characters = compendium.get("characters", [])
upgrades = compendium.get("upgrades", [])
campaign = compendium.get("campaign", [])

# ── characters ─────────────────────────────────────────────────────────────────

seen_char_ids: dict = {}
for i, c in enumerate(characters):
    p = f"characters[{i}] id={c.get('id', '?')} name={c.get('name', '?')!r}"

    for field in ("id", "name", "factions", "health", "abilities", "keywords"):
        if field not in c:
            error(p, f"missing required field '{field}'")

    cid = check_id(p, c.get("id"), seen_char_ids)
    check_factions(p, c.get("factions", []))
    check_abilities(p, c.get("abilities", []))
    if cid is not None:
        check_share_code(p, "A", c.get("factions", []), cid, c.get("shareCode"))

    health = c.get("health")
    if health is not None:
        h = coerce_id(health)
        if h is None or h <= 0:
            error(p, f"'health' must be a positive integer, got {health!r}")

    sig = c.get("signatureMove")
    if sig is not None and "name" not in sig:
        error(p, "signatureMove missing 'name'")

print(f"characters       : {len(characters)} entries, {len(seen_char_ids)} unique ids")

# ── upgrades ───────────────────────────────────────────────────────────────────

seen_upgrade_ids: dict = {}
for i, u in enumerate(upgrades):
    p = f"upgrades[{i}] id={u.get('id', '?')} name={u.get('name', '?')!r}"
    for field in ("id", "name", "factions"):
        if field not in u:
            error(p, f"missing required field '{field}'")
    uid = check_id(p, u.get("id"), seen_upgrade_ids)
    check_factions(p, u.get("factions", []))
    if uid is not None:
        check_share_code(p, "C", u.get("factions", []), uid, u.get("shareCode"))

print(f"upgrades         : {len(upgrades)} entries")

# ── campaign ───────────────────────────────────────────────────────────────────

seen_campaign_ids: dict = {}
for i, card in enumerate(campaign):
    p = f"campaign[{i}] id={card.get('id', '?')} name={card.get('name', '?')!r}"
    for field in ("id", "name", "factions"):
        if field not in card:
            error(p, f"missing required field '{field}'")
    cid = check_id(p, card.get("id"), seen_campaign_ids)
    check_factions(p, card.get("factions", []))
    if cid is not None:
        check_share_code(p, "B", card.get("factions", []), cid, card.get("shareCode"))

print(f"campaign         : {len(campaign)} entries")

# ── Report ─────────────────────────────────────────────────────────────────────

if errors:
    print(f"\n{len(errors)} lint error(s) found:")
    for e in errors:
        print(e)
    sys.exit(1)

print("\nAll lint checks passed.")
