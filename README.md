# SloppyMods Rimout Power Suit

A RimWorld 1.6 mod: power suits you climb into, like the power armor in Fallout. A suit
stands on its own until a colonist climbs inside to work and fight in it, and climbs back
out when the job is done. Pilots can wield the heavy warcasket weapons from Vanilla
Factions Expanded - Pirates.

Requires [Harmony](https://github.com/pardeike/HarmonyRimWorld),
Vanilla Expanded Framework and
[Vanilla Factions Expanded - Pirates](https://github.com/Vanilla-Expanded/VanillaFactionsExpanded-Pirates).

## Planned

- Power cells: removable batteries that drain while the suit works, recharged on a powered
  charging rack.
- One suit frame with swappable plating, arm and system modules - heavy tank plating, a field
  medical system, built-in melee arms for fighting insects.
- Wrecked suits that trap their pilot until another colonist cuts them out.

## Building

`bash .github/release.sh --no-release` compiles `Assemblies/RimoutPowerSuit.dll` from
`Source/` and packages the mod zip in `dist/`. See `CLAUDE.md` for how builds are released.
