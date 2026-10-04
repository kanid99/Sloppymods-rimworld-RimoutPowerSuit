# Rimout Power Suit - design notes

Decisions agreed with the owner, to build from. Numbers are starting points for tuning.

## Modular suit

- Slots: **chassis** (chest + hips; defines the role and base stats), **helmet**, **left arm**,
  **right arm** (shoulder/arm armour - pawns have no arms; each arm drawn once, mirrored for the
  other side, so left and right can differ), **legs** (shown as hip/thigh plates), **back mount**.
- Lite mode: each slot is a separate worn piece, swapped anywhere. Exosuit mode: framework
  modules (core, head, mounts, attachment), swapped at bays.
- Non-combat chassis exist for hazards: vacuum, toxic gas, heat, cold. Low armour.
  Bulwark and Bughunter are the armoured ones.
- Every chassis shares one standard flat collar ring; arm pieces tuck behind it.
- Helmet lamps: a visual light cone each frame (no TPS cost), plus real light updated only when
  the pawn changes cell and only in the dark; settings: full / visual only / off.

## Role bonuses (conditional, via stat parts on the worn chassis)

- **Harvester**: plant work speed x1.5 and harvest yield +10% only when sowing, harvesting or
  cutting plants in soil - not in hydroponics basins or planters. (Optional x0.9 indoors.)
- Same pattern offered for others: Miner (mining rock), Builder (construction, not crafting),
  Medic (treating patients).

## Bughunter (insect killer)

- Focus: **heavy armour**. Bonuses to **blunt melee** (+35% blunt melee damage, any blunt
  weapon) and to **fire** (+25% flame damage dealt, any flamethrower or fire source).
- Built-in arm weapons (art: `arm_flamer`, `arm_hammer`):
  - **Hydraulic hammer arm**: a built-in heavy blunt melee attack, always available, even while
    the pilot holds a gun. Two hammer arms = more frequent hammer strikes. Drawn big and swung
    outward from its shoulder plate (which stays bolted to the chassis) so it reads at a glance.
  - **Flamethrower arm**: NOT a regular weapon - a **targeted ability button** on the pilot's
    command bar: pick a spot in range (~7 tiles), sprays a cone of fire there (reusing VFE
    Pirates' flame projectile). Cooldown; **draws its charge from the suit's power cells**
    and can't fire when they're too low. Two flamer arms = **two independent buttons**, one per
    arm, each with its own cooldown.
- **Net launcher** (chassis ability): a targeted button that fires a net over an area; insects
  caught in it are pinned (or heavily slowed) for a few seconds - other creatures are only
  slowed briefly. Sets up the hammer and flamer. Holds **3 nets max**; does not use suit
  power. The pilot reloads it from **cloth or other common textiles** (any fabric: cloth,
  hemp, synthread, devilstrand...; around 20 per net), like vanilla reloadable gear.
- Helmet: twin lamps on top (no horns, no side fire port). Chassis: a faint chevron along
  the lower chest edge - the only hint of teeth.
- Drawbacks: **slow** (large move-speed penalty) and **power hungry** (high drain).
- Compensation: holds **two power cells** instead of one.
- **Versus the Bulwark** (owner, 2026-10): the Bughunter is built to **take sharp damage**
  (high sharp armour - claws, bites, stings) and **deal blunt damage** (hammer). The Bulwark is
  the all-round tank. The Bughunter is also **heat resistant** (high heat armour, and its pieces
  are not damaged by its own flamer), so it can fight inside its own fire.
- **Shoulder plates:** the Bughunter has its own **light open-frame plates**. They are shorter
  and slimmer than the Bulwark's slabs, with cut-out slots. They add some armour, but their job is
  to boost the suit's weapons:
  - **Pneumatic pressure plate** (hammer arm): twin pressure cylinders, a gauge, and a braided hose
    down to the hammer. It turns the hammer into a **power hammer** (more blunt damage, plus stagger
    or knockback). Art: `nano/modular/arm_bughunter_pneumatic_south.png`.
  - **Fuel-injection plate** (flamer arm): a banded fuel canister, an injector pump with a valve wheel,
    and fuel lines down to the flamer. **More range and more fire damage.**
    Art: `nano/modular/arm_bughunter_fuel_south.png`.
- **Jump-pack backpack** (Bughunter only): holds **three power cells** (three round cell caps above
  the release wheel) and has two thrusters with a vent grille. It is an escape ability for when the
  suit is swarmed: a targeted jump a few tiles away, like the vanilla jump pack. **Each jump uses a
  big share of the suit's power**, and it has a long cooldown. Art: `kit/bughunter_src/own/`.

### Shoulder plates and backpacks are per suit
- **Shoulder plates fit one suit type.** Bulwark plates fit only the Bulwark, and Bughunter plates
  fit only the Bughunter.
  - **Bulwark plates:** heavy slabs that add **a lot to the overall armour rating**.
  - **Bughunter plates:** light frames with **some** extra armour, built around **attack boosts**
    (power hammer, fuel injection).
  - **Generic plates** (to make): a plain plate that fits every suit, for the other chassis and as a
    fallback.
- **Backpacks are unique to each suit type**, and an upgraded backpack needs **three cells**:
  - **Bughunter:** the jump pack (above).
  - **Bulwark:** an optional **shield-generator backpack**. It powers the standing-still shield
    system and needs three cells.

## Power cells

- Removable battery items carrying their own charge, charged on a powered charging rack.
- The suit drains them over time (more when drafted, moving, attacking); abilities such as the
  flamer spend charge directly. Most chassis take one cell; the Bughunter takes two.

## Bulwark (reviewed)

- Role: heavy tank. Takes a lot of varied damage, best when standing still; deals heavy damage of several kinds.
- Chassis: heavy bolted slab plates over the chest (no vents).
- Helmet: brow plate, two slanted eye plates, centre ridge, breather snout; two lamps on top of the crown.
- Arms: every arm carries a short rounded arm shield over the shoulder (not the old tall hooked plate); the weapon hangs beneath it.
  South view: weapons hang straight down, muzzle to the ground (warcasket style), so nothing sticks out sideways.
  Options: minigun, rocket pod, chainsaw, laser, flamer, hammer. Weapon art is separate
  (`Source/Art/nano/modular/weapons/`), composited under the shared plate (`Source/Art/bulwark_hang.py`).

### Bulwark mechanics

- **Siege shield.** After the pilot has stood still for ~1 second, the suit diverts power into a shield
  bubble. It absorbs incoming damage of every kind (bullets, blades, blunt, fire, explosions) up to its
  energy, drawn from the suit's power cells while it is up and while it recharges. The pilot can still fire
  out of it (unlike a vanilla shield belt). Taking a step drops it instantly; it starts back up after
  standing still again. No power left in the cells = no shield. A gizmo toggles it off to save power.
- **Ranged arms** (minigun, autocannon, laser): the arm *is* the suit's weapon. One gun arm = that gun;
  two gun arms fire together as one heavier burst. Works with VFE Pirates' warcasket weapons in place of
  a gun arm.
- **Ability arms** (rocket pod, flamer, grenade launcher, arc projector): each arm adds its own targeted
  button, powered from the suit (two such arms = two independent buttons, as for the Bughunter).
  Each button has an **Auto** toggle: when on, the arm fires by itself at hostiles in range when
  ready - rockets and grenades pick the biggest group, the flamer only fires when no friendly is in the
  cone. Off by default.
- **Melee arms** (chainsaw, hammer): built-in melee attacks that replace fists; chainsaw = cut + bleeding,
  hammer = blunt + stun.
- **Rocket ammo:** a few rockets loaded at a time, reloaded from steel and chemfuel (like the net launcher
  reloads from textiles).

### More Bulwark arm ideas

- Art for the four below is kitbashed from the generated weapons and chest (`Source/Art/kitbash.py`), with code-drawn fill-ins (`Source/Art/vdraw.py`).
- **Autocannon** - single heavy barrel, slow powerful shots; good against mechs and doors.
- **Grenade launcher** - ability arm: lobs over cover and walls (indirect fire).
- **Arc projector** - ability arm: chains EMP lightning between enemies; stuns and wrecks mechanoids and
  shields, harmless-ish to flesh.
- **Tower shield** - a non-weapon arm: a slab shield that adds armour from the front and doubles the
  siege shield's strength while standing still; pairs with any weapon on the other arm.

### Art style: VFE / vanilla RimWorld (tried, dropped - see docs/STYLE_GUIDE.md; files in Source/Art/archive/)

Matches VFE Pirates' warcaskets: light grey parts (the game tints them), soft form shading (rounded parts darken toward the rim, light from the upper left, plates cast soft shadows; crisp chamfer side faces, lit toward the upper left and clearly darker facing away; `fill_vfe(..., bevel=)`), two or three tones with a soft
top-down gradient, thin dark inner lines between big plates, a heavy black silhouette outline, and detail only
suggested (a seam, a couple of bolts, a slot). Tools: `Source/Art/vdraw.py` `fill_flat`, the parts in
`vfe_parts.py` / `vfe_helmet.py`, flat weapons in `vweap_vfe.py`, assembly in `vfe_build.py`; `vfe_style.py`
is an automatic filter that converts painted art toward this style (good on big plates, not on faces).
Parts: `Source/Art/nano/modular/vfe_style/`.

Scale: the suit with its helmet should be only slightly bigger than vanilla cataphract armour with its helmet
(about 1.3x our old 256px body canvas, so a larger canvas and render-node draw size in game).

Weapons are original designs that take their cues from vanilla ones (autocannon turret: twin drums and a
perforated jacket; minigun: barrel cluster and a yellow ammo box; rocket pod: a box pod with bands and a handle, two red-tipped rockets poking out of its base; charge
lance: tan spacer body and blue core; incendiary launcher: orange tank; zeus hammer: emitters in the head).
No vanilla pixels are used; the official art source is only a reference (owner's Dropbox, not in the repo).

### Gemini chat as a parts source

The owner generates concepts in Gemini chat (style prompt: light grey plates, thick outline, chamfered
side faces, suggested detail, no arms/legs). Results are inconsistent, so they are used as parts, not
finished suits: `Source/Art/gemini/` holds the originals, `gem_parts.py` cuts parts out,
`gem_kitbash.py` combines them with our kit parts (helmet, arm shields, weapons).
Kept so far: the chest/abdomen/hip body (siege suit), the box rocket pod with a tube grid (fire support,
replaces our rocket pod), the claw arm (breacher; Bughunter melee option), the long cannon (fire support).
- Non-combat concepts (`gemini/noncombat1.jpg`): miner (drill arm + pick-hammer), engineer (hand + block tool),
  hazard/vacuum (fishbowl visor, chest filter canisters, gripper claw). Gemini washed them out; 
  `Source/Art/gemini_restyle.py` restores dark lines, a heavy outline and stronger tones.
  Note: Gemini drew full mechanical arms; for RimWorld only the tool ends are kept as arm parts.
- Style target chosen by the owner (`gemini/noncombat_noattach.jpg`, "closer to RimWorld"): clean white
  plates, soft grey side faces, thin near-black inner lines, heavy black outline. `vdraw.use_soft_preset()`
  approximates it for our own drawing. Parts cut from it (`gemini/parts/`): Miner, Engineer and Hazard bodies,
  drill, pick-hammer and gripper claw; `nc_miner_kit.png` is a first Miner assembled from them.

### Originality check for generated art (VFE Pirates)

Gemini can reproduce VFE Pirates warcaskets. Before keeping any generated part, put it next to every VFE
warcasket helmet and body (south) and reject anything that matches one. From the "armor & helmet
spreadsheet" round:
- Rejected (VFE copies): the "Original" helmet and both "Original" bodies (VFE base/Aerial warcasket),
  the "Bulwark" helmet (VFE Marine helmet's T-visor, crest and flared cheeks). That image is not kept in the
  repo.
- Kept as starting points (`gemini/parts/sheet_*`): Miner helmet (forehead lamp, goggles), Medic helmet
  (clear dome visor, green crosses), Bughunter helmet (twin filter gas mask, four eye lenses), and the
  Miner / Medic / Bughunter bodies as references - they have legs and harness detail, so only the torso
  ideas are used (vest with pouches, medic chest cross and belt, bughunter canisters at the hips).

### Bughunter helmet (soft VFE style)

Redrawn from the kept Gemini idea: egg-shaped skull, cheek plates, a brow ridge with two small upper lenses,
two big teardrop lenses slanting up and out (insect-like), a narrow snout with a hexagonal port, twin filter
canisters hanging low, two crown lamps. `Source/Art/vfe_bughunter_helmet.py`.


### Current art base

The approved painted modular set (`Source/Art/nano/modular/`) is the base again. Rules: `docs/STYLE_GUIDE.md`.

### Per-piece damage (owner's idea, to design)

Each armour piece (helmet, chest, each shoulder/arm, legs) has its own condition and can be damaged and
destroyed independently of the frame. A destroyed piece falls off and its slot is exposed; when the
pieces covering a body part are gone, hits there reach the pilot inside the frame. Pieces are repaired
or replaced individually. The owner wants visible legs back so damage to them can be shown: short stubby leg pieces under the hip armour (`legs_bulwark_south.png`), not full legs.
Fits both modes: Exosuit mode already treats modules as separate items; lite mode would need the pieces
as separate apparel with their own hit points.

### Entry: the back opens

The suit is entered from behind: the whole back panel (power-cell caps and release wheel on it) is hinged on
one side and swings open like a door, showing an upright padded cavity for a standing pilot (who faces away from the viewer: no seat) with arm holes in the side walls, leg holes in the floor and the neck hole at the top; the harness straps are on the inside of the door and close around the pilot's back
(`chassis_bulwark_north_open.png`). Used for the empty/parked suit and as a frame of the climb-in animation
(turn the release wheel, back swings open, pilot climbs in, back closes).
