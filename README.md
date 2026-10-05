# SloppyMods Rimout Power Suit

A RimWorld 1.6 mod: power suits you climb into, like the power armor in Fallout. A suit
stands on its own until a colonist climbs inside to work and fight in it, and climbs back
out when the job is done. Pilots can wield the heavy warcasket weapons from Vanilla
Factions Expanded - Pirates.

Requires [Harmony](https://github.com/pardeike/HarmonyRimWorld),
Vanilla Expanded Framework and
[Vanilla Factions Expanded - Pirates](https://github.com/Vanilla-Expanded/VanillaFactionsExpanded-Pirates).

## Suits

- **Bulwark** - the heavy tank: thick armour against everything, slow.
- **Bughunter** - built for insect hives: very hard to cut, bite or burn, hits harder up close,
  even slower.
- **Miner** - a light work suit that digs through rock much faster; drill arms and a drill
  booster pack make it faster still.

Fit weapon arms to a standing suit: right-click it with a colonist selected. Bulwark arms:
minigun, autocannon, laser, rocket pod, grenade launcher, arc projector, flamer, hammer,
chainsaw, tower shield. Bughunter arms: fuel-injected flamer, pneumatic power hammer.

Suits run on power cells: they drain while piloted and recharge next to a suit charging rack.
Backpacks hold three cells: the Bulwark's shield generator (a shield bubble while it stands
still) and the Bughunter's jump pack. The Bughunter also fires nets that pin insects.

## Planned

- The flamer and rocket arms as targeted buttons with an auto mode; the suit's back opening
  while a pilot climbs in or out.
- Suit pieces that are damaged and knocked off one at a time.
- More suits: builder, medic, harvester and more.
- Wrecked suits that trap their pilot until another colonist cuts them out.

## Building

`bash .github/release.sh --no-release` compiles `Assemblies/RimoutPowerSuit.dll` from
`Source/` and packages the mod zip in `dist/`. See `CLAUDE.md` for how builds are released.
