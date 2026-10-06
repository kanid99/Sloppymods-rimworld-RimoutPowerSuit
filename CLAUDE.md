# Working on this repo

## The default branch is the release

The owner installs and updates the SloppyMods mods straight from GitHub: RimSort
clones this repository's default branch (`main`) into RimWorld's Mods
folder and pulls it in place. There is no separate release step, so **every
commit pushed to `main` is what the game loads next**.

- Push finished work to `main`. Nothing half-done: each commit must load
  and play as-is.
- **Snapshot every build on its own branch.** Every commit carries a build
  number (`0.9.<commit count>`, stamped below). Push the same commit to
  `main` AND to a branch named after that build, so any build can be
  restored:

      git push origin HEAD:main HEAD:refs/heads/build/0.9.N

  Build branches are restore points: never move or delete one. To roll back,
  reset `main` to an earlier `build/...` branch - only when the owner asks.
  The release workflow only runs on `main`, so build branches publish nothing.
- **Every update carries its change notes** as BBCode (the Steam Workshop
  change-notes format), in `Changelog/<build>.bbcode` - e.g.
  `Changelog/0.9.N.bbcode` - committed in the same commit as the change, so
  each `build/` branch carries its own notes. Write them for players: what was
  added, changed and fixed, not how. Format:

      [h2]Build 0.9.N[/h2]
      [h3]Added[/h3]
      [list]
      [*]...
      [/list]

  Use only the sections that apply (Added, Changed, Fixed, Removed).
- **Commit the compiled assemblies.** RimWorld loads the DLL, not the source,
  and a clone gets only what is in git. This mod needs:
  - `Assemblies/RimoutPowerSuit.dll`
  - `Mods/Exosuit/Assemblies/RimoutPowerSuit.Exosuit.dll`
  `.gitignore` must not exclude them (a bare `Assemblies/` rule does, at any
  depth - un-ignore those paths). Rebuild and commit the DLLs in the same
  commit as any C# change; a stale DLL is what players get.
- **Stamp the build number before every commit** so the mod list and RimSort
  show which build is installed: `<modVersion>` in `About/About.xml`, and a
  `Build x.y` line at the top of its description, set to
  `series.<commit count after this commit>` (series 0.9). Never leave a
  placeholder like `0.9.0-dev`.
- Keep `packageId` (`sloppymod.rimoutpowersuit`) unchanged: saves and RimSort
  key on it. The display `<name>` is "SloppyMods Rimout Power Suit".
- Everything in the repository root lands in the Mods folder, so keep
  anything RimWorld might try to load (Defs, Patches, Textures, LoadFolders)
  deliberate; `Source/`, docs and images are ignored by the game.
- **Every push to the default branch publishes a GitHub Release**,
  `v<build>`, with the mod zip attached (`.github/workflows/release.yml`,
  which runs `.github/release.sh`). RimSort's GitHub Mods panel reads "Latest
  Version" from the newest release and installs its zip, so this is what
  RimSort users get. The script compiles the assemblies from source with mcs
  against Krafs' reference assemblies, so the zip always matches the commit;
  if the build changes (a new assembly, a new reference), update `build()` at
  the top of `release.sh`, and check it with
  `bash .github/release.sh --no-release` (zip in `dist/`). mcs is stricter
  than Roslyn in places (e.g. two `out var` of the same name in one method),
  so keep the source compiling under it.
- Harmony is provided at runtime by the Harmony mod: compile against it, never
  ship 0Harmony.dll.

## This mod

- Requires Vanilla Factions Expanded - Pirates (and so Vanilla Expanded
  Framework). The C# does not reference either assembly: warcasket weapons
  accept the suit because VEF's heavy-weapon check lets anyone wear torso
  armour whose `tradeTags` include `Warcasket`. Keep that tag on the suit.
- Do not reuse VFE Pirates' `Apparel_Warcasket` / `WarcasketDef` types: their
  patches block unlocking, stripping and spawning them on the ground, which
  is the opposite of a suit you climb in and out of.
- The suit design is ORIGINAL (a diving-helmet industrial suit: a round dive helmet
  with a straight amber visor band, a chin grille and a miner's lamp, big round
  shoulder plates, twin cells and a release wheel on the back). Never give an image generator another game's armour - Fallout's
  power armour included - as a reference: copies are a copyright risk. Only "inspired
  by" ideas (a walking suit, a release wheel) are fine.
- Art must read at the size the game shows a pawn (~40-64px): a helmet about half
  the sprite's width, a few large smooth plates, a very thick silhouette outline, one
  accent colour, no small details (rivets, stencils, stripes, vents). Judge every
  candidate with `python3 Source/Art/check_scale.py OUT.png candidate.png ...`, which
  shows it processed and painted at in-game sizes, before choosing it.
- Suit art is painted with Nano Banana Pro (`Source/Art/nano.py`, which reads the
  key from `GEMINI_API_KEY` - never commit a key), in the format and style of VFE
  Pirates' warcaskets: no arms, no legs, helmet + torso +
  pauldrons + hip plates. The paintings live in `Source/Art/nano/`;
  `python3 Source/Art/process_nano.py` turns them into the textures: cut-out, scaled
  to the 256px body canvas, one texture per direction for every body type (VEF
  `isUnifiedApparel`), plus CutoutComplex masks (`_southm`/`_eastm`/`_northm`, `_m`
  for the standing suit) whose red marks the plates that take the suit's colour.
- The suit is apparel locked onto its pilot; only the exit job unlocks it
  (`PowerSuitUtility.AllowUnlock`).

## Two modes

- **Lite mode** (no Exosuit Framework): everything in the root - the suit is our own
  `Apparel_PowerSuit`, climbed into where it stands. Keep it light: no modules, no bays.
- **Exosuit mode** (Exosuit Framework, `Aoba.Exosuit.Framework`, active):
  `LoadFolders.xml` adds `Mods/Exosuit` - the suit as a framework core
  (`RPS_PowerSuitCoreItem` / `RPS_PowerSuitCore`), a patch that stops the lite suit
  being craftable, and `RimoutPowerSuit.Exosuit.dll` (`Source/RimoutPowerSuit.Exosuit`).
  That assembly is the only code that references the framework; the root assembly must
  never reference `Exosuit` types, or lite mode breaks.
- We depend on the framework, we do not copy it: it has no licence. Extend it by
  subclassing its virtual members (bays, `Exosuit_Core`, `ExosuitExt.wreckageOverride`),
  and patch its internals only as a last resort. It is compiled against a pinned
  commit (`EXOSUIT_COMMIT` in `.github/release.sh`); bump it deliberately and re-test.
- Free-standing suits in Exosuit mode: `Building_SuitStand` is a one-tile bay that
  appears when a pilot uses "Climb out here" or a suit is "Set up here", and destroys
  itself once it holds no core.

## Standing preferences

- Licence is MIT for this mod (the owner's choice; other SloppyMods are CC0).
- Replies to the owner: concise summaries; attach a build zip when they will
  test in game.
- For art changes, show the owner before/after comparisons - but they ship to
  the default branch like any other change; the build branch is the way back.
- **Code-drawn art is made as SVG first, and the SVG is always committed** next to the
  PNGs made from it (the SVG is the editable reference; the game still loads PNGs).
  The drawing scripts write SVG through `Source/Art/frame/frame_svg.py`; PNGs are
  rendered from the SVG with the preinstalled Chromium. Never commit an SVG that
  embeds vanilla game art (e.g. the `_pilot` previews with the vanilla pawn).
