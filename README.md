# moonstone-companion-data

This is the temporary data repository for character json data that is loaded into [moonstone-companion application](https://github.com/Garemat/moonstone-companion)

This repository will be made redudant once an API layer is introduced, but currently it is used to bundle and produce the compedium releases. 

The data releases are seperated into different aggregated json objects to make maintence easier in the repo, and management easier in the app.

Character image files are also bundled as a seperate artifact as an optional additional download through the app
TODO: Add the remaining images for characters

When updating files ensuring you're testing before raising a PR (As the pipeline will not allow merges)

```
python3 scripts/aggregate.py
python3 scripts/lint_data.py
```

For testing data with a local app setup, I'd reccomend symlinking the build folder with ${location_of_app_repo}/app/src/main/assets/
The app requires all three files in order to skip auto pulling the latest release at build

## Campaign JSON
Each Campign card follows a pretty simple json

```json
{
  "id": 1,
  "name": "Card Name",
  "version": 2,
  "factions": ["COMMONWEALTH"],
  "tags": [],
  "timing": "Play during the Activation Step, before or after any action.",
  "description": "For the remainder of the game, the first time a friendly *Noble* would suffer Dmg each turn, you may have a friendly Non-*Noble* within 4\" suffer that Dmg instead.",
  "shareCode": "AAB",
  "imageName": "card_name"
}
```
## Upgrade JSON

```json
{
  "id": 1,
  "name": "A Pirate's life for me!",
  "version": 1,
  "factions": ["COMMONWEALTH"],
  "allowedKeywords": [],
  "restrictedKeywords": [],
  "extraDescription": "This character gains the Pirate keyword.",
  "abilities": [],
  "shareCode": "AAB",
  "imageName": "apirateslifeforme"
}

```

## Character JSON Template

Each character lives in `characters/{faction}/{id}_{name}.json`. Use the template below when adding a new character. All fields are required unless noted.

```json
{
  "id": 0,
  "name": "Character Name",
  "version": 1,
  "factions": ["COMMONWEALTH"],
  "health": 8,
  "energyTrack": [1, 3, 6],
  "keywords": ["Human"],
  "melee": 3,
  "meleeRange": 1,
  "arcane": 3,
  "evade": 0,
  "baseSize": "30mm",
  "imageName": "character_name",
  "shareCode": "AAB",
  "slicingDamageBuff": 0,
  "piercingDamageBuff": 0,
  "impactDamageBuff": 0,
  "dealsMagicalDamage": false,
  "allDamageMitigation": 0,
  "piercingDamageMitigation": 0,
  "impactDamageMitigation": 0,
  "slicingDamageMitigation": 0,
  "magicalDamageMitigation": 0,
  "summonsCharacterIds": [],
  "isUnselectableInTroupe": false,
  "signatureMove": {
    "name": "Sig Move Name",
    "upgradeFor": "High Guard",
    "possibleDamageTypes": ["Slicing"],
    "highGuard":    {"deal": "2", "isFollowUp": false},
    "fallingSwing": {"deal": "1", "isFollowUp": false},
    "thrust":       {"deal": "2", "isFollowUp": false},
    "sweepingCut":  {"deal": "Null", "isFollowUp": false},
    "risingAttack": {"deal": "1", "isFollowUp": true},
    "lowGuard":     {"deal": "Null", "isFollowUp": false},
    "extraText": "Any rules text that applies during the melee round (not at End Step).",
    "endStepEffect": "Any End Step Effect text, or empty string if none."
  },
  "abilities": [
    {
      "name": "Passive Ability Name",
      "description": "Full rules text.",
      "abilityType": "Passive",
      "oncePerTurn": false,
      "oncePerGame": false,
      "arcaneOutcomes": []
    },
    {
      "name": "Active Ability Name",
      "description": "Full rules text.",
      "abilityType": "Active",
      "energyCost": 2,
      "range": "6\"",
      "pulse": false,
      "oncePerTurn": false,
      "oncePerGame": false,
      "arcaneOutcomes": []
    },
    {
      "name": "Arcane Ability Name",
      "description": "Any general rules text not tied to a specific card outcome (or empty string).",
      "abilityType": "Arcane",
      "energyCost": 2,
      "range": "8\"",
      "pulse": false,
      "oncePerTurn": false,
      "oncePerGame": false,
      "arcaneOutcomes": [
        {
          "text": "Effect when a matching card is flipped.",
          "validCards": [{"colour": "Pink", "value": "X"}]
        },
        {
          "text": "Effect for a fixed-value outcome.",
          "validCards": [{"colour": "Green", "value": "2"}, {"colour": "Blue", "value": "2"}, {"colour": "Pink", "value": "2"}]
        },
        {
          "text": "This character suffers 3 Wds.",
          "validCards": [{"colour": "Catastrophe", "value": "X"}]
        }
      ]
    }
  ]
}
```

### Notes

| Field | Notes |
|-------|-------|
| `factions` | `"COMMONWEALTH"`, `"DOMINION"`, `"LESHAVULT"`, `"SHADES"`. Multiple for dual-faction. |
| `energyTrack` | Starting energy positions, e.g. `[1, 3, 6]`. Use `[999]` for characters that can never gain energy (Thralls, Echo). |
| `meleeRange` | Numeric inches only, e.g. `1` for 1", `2` for 2". |
| `imageName` | Snake_case name without ID prefix or extension, e.g. `"old_polly"`. |
| `slicingDamageBuff` | Net passive bonus to Slicing melee damage output. `null` for null values.  |
| `dealsMagicalDamage` | `true` only if base melee attacks are Magical |
| `allDamageMitigation` | Use when a passive reduces ALL damage types. Individual fields cover specific types. |
| `summonsCharacterIds` | IDs of characters this model can place/summon via abilities. |
| `isUnselectableInTroupe` | `true` for Thralls and summoned-only characters. |
| `signatureMove` | `null` for characters with no signature move (Thralls, summoned creatures). |
| `deal` | `"Null"` (string) = Ø, `"0"` = zero damage, `"1"`–`"4"` = damage value. |
| `isFollowUp` | `true` = amber circle in PDF table (follow-up hit). |
| `possibleDamageTypes` | `[]` if sig deals no damage or damage type is unspecified. Multiple entries allowed e.g. `["Slicing", "Magical"]`. |
| `abilityType` | `"Passive"`, `"Active"`, or `"Arcane"`. Active and Arcane both require `energyCost`, `range`, `pulse`. |
| `validCards` colours | `"Green"`, `"Blue"`, `"Pink"`, `"Catastrophe"`. |
| `validCards` value | `"X"` for variable-value outcomes; `"1"`, `"2"`, `"3"` etc. for fixed-value outcomes (any colour at that value). |
| `transformsInto` ID | This is a unqiue field currently for anya, which allows her to transform between states. |

# License & Attribution
This project uses assets from Goblin King Games’ publicly available store and website. These assets are provided for non-commercial use only and must remain free to use. Please credit Goblin King Games when using these assets.
