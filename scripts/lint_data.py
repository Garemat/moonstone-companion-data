#!/usr/bin/env python3
"""
Lint the aggregated compendium.json produced by the build step.
Reads build/compendium.json and exits with code 1 if any errors are found.
"""

import json
import sys

VALID_FACTIONS = {"COMMONWEALTH", "DOMINION", "LESHAVULT", "SHADES"}
VALID_ABILITY_TYPES = {"Passive", "Active", "Arcane"}

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

    check_id(p, c.get("id"), seen_char_ids)
    check_factions(p, c.get("factions", []))
    check_abilities(p, c.get("abilities", []))

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
    check_id(p, u.get("id"), seen_upgrade_ids)
    check_factions(p, u.get("factions", []))

print(f"upgrades         : {len(upgrades)} entries")

# ── campaign ───────────────────────────────────────────────────────────────────

seen_campaign_ids: dict = {}
for i, card in enumerate(campaign):
    p = f"campaign[{i}] id={card.get('id', '?')} name={card.get('name', '?')!r}"
    for field in ("id", "name", "factions"):
        if field not in card:
            error(p, f"missing required field '{field}'")
    check_id(p, card.get("id"), seen_campaign_ids)
    check_factions(p, card.get("factions", []))

print(f"campaign         : {len(campaign)} entries")

# ── Report ─────────────────────────────────────────────────────────────────────

if errors:
    print(f"\n{len(errors)} lint error(s) found:")
    for e in errors:
        print(e)
    sys.exit(1)

print("\nAll lint checks passed.")
