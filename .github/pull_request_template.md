## Description
<!-- Provide a brief description of the changes -->

## Type of Change
- [ ] 💥 Breaking change (removes characters/cards, or changes field structure in a way that requires an app update)
- [ ] ✨ New character or card (adds new characters, upgrades, or campaign cards)
- [ ] 🐛 Data fix (corrects errors in existing character/card data)
- [ ] 🖼️ Image update (adds or replaces character portrait images)
- [ ] 🧹 Chore (workflow, scripts, formatting — no data release needed)

## Checklist
- [ ] I have verified the affected JSON files are valid and parse correctly
- [ ] Character `id` values are unique and match the expected numeric format
- [ ] Any new characters include all required fields: `id`, `name`, `factions`, `health`
- [ ] Any new portrait images are named to match the character's `imageName` field
- [ ] Dual-faction characters are placed in `characters/dual-faction/`
- [ ] I have performed a self-review of my changes
