#!/usr/bin/env python3
"""
Migrate character JSON files from old model to new unified model.

Changes applied:
  - 'tags' -> 'keywords'
  - 'passiveAbilities' + 'activeAbilities' + 'arcaneAbilities'
    -> single 'abilities' array with 'abilityType' field
  - 'cost' -> 'energyCost'
  - Extract 'Pulse' suffix from range string into separate 'pulse: true'
  - 'signatureMove.passiveEffect' -> 'signatureMove.extraText'
  - Add empty 'arcaneOutcomes: []' on each ability (filled manually from PDFs)
"""

import json
import glob
import os


def extract_range_pulse(range_val):
    """Split 'Pulse' flag out of range string. Returns (range_str, pulse_bool)."""
    if not range_val:
        return "", False
    s = str(range_val).strip()
    if "Pulse" in s:
        clean = s.replace(" Pulse", "").replace("Pulse", "").strip()
        return clean, True
    return s, False


def migrate_ability_base(ab):
    return {
        "name": ab.get("name", ""),
        "description": ab.get("description", ""),
        "oncePerTurn": ab.get("oncePerTurn", False),
        "oncePerGame": ab.get("oncePerGame", False),
        "arcaneOutcomes": [],
    }


def migrate_character(data):
    # tags -> keywords
    if "tags" in data:
        data["keywords"] = data.pop("tags")

    # Build unified abilities list (preserve insertion order: passive, active, arcane)
    abilities = []

    for ab in data.pop("passiveAbilities", []):
        entry = migrate_ability_base(ab)
        entry["abilityType"] = "Passive"
        abilities.append(entry)

    for ab in data.pop("activeAbilities", []):
        entry = migrate_ability_base(ab)
        entry["abilityType"] = "Active"
        entry["energyCost"] = ab.get("cost")
        range_str, pulse = extract_range_pulse(ab.get("range"))
        entry["range"] = range_str
        entry["pulse"] = pulse
        abilities.append(entry)

    for ab in data.pop("arcaneAbilities", []):
        entry = migrate_ability_base(ab)
        entry["abilityType"] = "Arcane"
        entry["energyCost"] = ab.get("cost")
        range_str, pulse = extract_range_pulse(ab.get("range"))
        entry["range"] = range_str
        entry["pulse"] = pulse
        if ab.get("reloadable"):
            entry["reloadable"] = True
        abilities.append(entry)

    data["abilities"] = abilities

    # signatureMove.passiveEffect -> extraText
    sig = data.get("signatureMove")
    if sig and "passiveEffect" in sig:
        sig["extraText"] = sig.pop("passiveEffect")
        data["signatureMove"] = sig

    return data


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    pattern = os.path.join(repo_root, "characters", "**", "*.json")
    paths = sorted(glob.glob(pattern, recursive=True))

    count = 0
    skipped = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        needs_migration = any(
            k in data for k in ("tags", "passiveAbilities", "activeAbilities", "arcaneAbilities")
        )
        if not needs_migration:
            skipped += 1
            continue

        data = migrate_character(data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Migrated: {os.path.relpath(path, repo_root)}")
        count += 1

    print(f"\nDone: {count} migrated, {skipped} already up to date.")


if __name__ == "__main__":
    main()
