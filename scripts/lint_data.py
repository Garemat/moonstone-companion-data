#!/usr/bin/env python3
"""
Lint the aggregated data JSON files produced by the build step.
Reads build/characters.json, build/upgrades.json, build/campaign.json.
Exits with code 1 if any errors are found.
"""

import json
import sys

VALID_FACTIONS = {"COMMONWEALTH", "DOMINION", "LESHAVULT", "SHADES"}

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


# ── characters.json ────────────────────────────────────────────────────────────

with open("build/characters.json") as f:
    characters = json.load(f)

seen_char_ids: dict = {}
for i, c in enumerate(characters):
    p = f"characters[{i}] id={c.get('id', '?')} name={c.get('name', '?')!r}"

    for field in ("id", "name", "factions", "health"):
        if field not in c:
            error(p, f"missing required field '{field}'")

    check_id(p, c.get("id"), seen_char_ids)

    check_factions(p, c.get("factions", []))

    health = c.get("health")
    if health is not None:
        h = coerce_id(health)
        if h is None or h <= 0:
            error(p, f"'health' must be a positive integer, got {health!r}")

    sig = c.get("signatureMove")
    if sig is not None and "name" not in sig:
        error(p, "signatureMove missing 'name'")

print(f"characters.json : {len(characters)} entries, {len(seen_char_ids)} unique ids")

# ── upgrades.json ──────────────────────────────────────────────────────────────

with open("build/upgrades.json") as f:
    upgrades = json.load(f)

seen_upgrade_ids: dict = {}
for i, u in enumerate(upgrades):
    p = f"upgrades[{i}] id={u.get('id', '?')} name={u.get('name', '?')!r}"
    for field in ("id", "name", "factions"):
        if field not in u:
            error(p, f"missing required field '{field}'")
    check_id(p, u.get("id"), seen_upgrade_ids)
    check_factions(p, u.get("factions", []))

print(f"upgrades.json   : {len(upgrades)} entries")

# ── campaign.json ──────────────────────────────────────────────────────────────

with open("build/campaign.json") as f:
    campaign = json.load(f)

seen_campaign_ids: dict = {}
for i, card in enumerate(campaign):
    p = f"campaign[{i}] id={card.get('id', '?')} name={card.get('name', '?')!r}"
    for field in ("id", "name", "factions"):
        if field not in card:
            error(p, f"missing required field '{field}'")
    check_id(p, card.get("id"), seen_campaign_ids)
    check_factions(p, card.get("factions", []))

print(f"campaign.json   : {len(campaign)} entries")

# ── Report ─────────────────────────────────────────────────────────────────────

if errors:
    print(f"\n{len(errors)} lint error(s) found:")
    for e in errors:
        print(e)
    sys.exit(1)

print("\nAll lint checks passed.")
