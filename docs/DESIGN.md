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

## Miner (work suit)

- Light armour; servos dig rock much faster (mining speed, a little more yield) and carry more.
- Generic light open-frame plates (the Bughunter's plain plate), shared by every work suit.
- **Drill arm**: faster mining per drill (two stack), and a boring melee strike.
- **Drill booster pack** (Miner only, three cells): powers the drills for much faster digging, only
  with a drill arm fitted; drains the cells fast while mining.
- Art: own chest, helmet, side painting, drill (5 views edited from the hammer's) and booster pack
  (`kit/miner_src/own/`); everything else shared with the Bulwark.

## Builder (work suit)

- Light armour; servos build and smooth much faster and carry more.
- **Construction drill arm**: a construction drill with a nail gun alongside. Faster building per arm (two stack);
  the nail gun is the pilot's short-range rapid-fire weapon (twin with two arms).
- No special pack yet (plain tall pack).
- Art: own chest, helmet, side painting and combo tool (5 views edited from the Miner's drill), `kit/builder_src/own/`.
  `work_spec()` in `suit_kit.py` builds any work suit from its chest, helmet and tool art.

## Medic (work suit) - designed, art pending

- Light armour; servos speed up tending.
- **Suture arm**: a "Stitch wounds" button - closes every bleeding wound on an adjacent pawn (or the pilot)
  at once, but as a rough low-quality tend: the bleeding stops, the infection risk stays. Costs a little power.
- **Medic pack** (Medic only, three cells): on-the-go scans and diagnostics raise tend quality, tend speed and
  surgery success while fitted. Holds up to 10 doses of medicine, loaded at the standing suit from any medicine;
  with medicine in it, each stitch uses a dose and tends at that medicine's quality (much less infection).
- Art needed (~10 credits): suture tool (5 views, from the drill's), side chest, helmet side and back, pack back
  (and side). Front chest and helmet exist (approved painted set).

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

### Per-piece damage - superseded by "The frame and the suit damage model" below

### Entry: the back opens (superseded by "The frame" below)

_Update:_ the pack opens **gullwing style**. It is hinged at its top edge and swings up over the head, so every
backpack variant reuses the same open cavity. The **net launcher** sits on the Bughunter's pack, at the top right
shoulder, and points forward.

The suit is entered from behind: the whole back panel (power-cell caps and release wheel on it) is hinged on
one side and swings open like a door, showing an upright padded cavity for a standing pilot (who faces away from the viewer: no seat) with arm holes in the side walls, leg holes in the floor and the neck hole at the top; the harness straps are on the inside of the door and close around the pilot's back
(`chassis_bulwark_north_open.png`). Used for the empty/parked suit and as a frame of the climb-in animation
(turn the release wheel, back swings open, pilot climbs in, back closes).

## The frame (v5, agreed with the owner)

Every suit is built on one **power armour frame**: a bulky, solid, human-shaped exoskeleton (bone-coloured
shells over dark metal, exposed drive bellows and red cable bundles at the waist), about 1.6x the pawn's
height on the existing 320 px / drawSize 2.717 canvas. Original design, inspired by open-back power-armour
frames. Concept art and game-ready layers: `Source/Art/frame/` (scripts) and `Source/Art/frame/kit/`
(layers, hatch stages, GUIDE.png, README.txt with the draw order, fit checks).

- **Proportions win (option A):** every plate, arm weapon and tool is redrawn to fit the frame (longer arms
  and legs, collar at the pilot's chin). The current suit art does not fit it (`kit/fit_<Suit>.png`).
- **The pilot** is the game's own pawn, drawn 26 px higher than normal so the head clears the collar.
- **The back hatch** is one solid armoured shell (30 px deep), hinged along the top of its humps (hinge
  barrels on the frame), closing onto a rim of the same shape round the opening. Inside: quilted padding.
  The pack rides on the hatch and swings up with it.
- **The neck hole** is a collar ring in the frame itself. Without a helmet the head shows through it.
- **Auxiliary tank** across the lower back: holds the spare cell used if the pack is damaged or destroyed.
- **Climb-in:** the hatch swings up (6 stages, 0 = shut .. 5 = 135 degrees open); the pilot walks up from
  behind, under the raised hatch, steps up into the frame; the head goes into the collar (north: covered by
  the raised hatch, revealed as it closes; south: rises up through the collar); the hatch closes. The legs
  do not open. Hinge barrels are hidden by the hatch while it moves.

### Pilot's clothes

Clothes stay visible while the pilot climbs in. When the hatch closes, everything the pilot wears (hats
included) is taken off and kept in the suit (a container on the suit, saved with it - not the pilot's
inventory). They go back on when the pilot climbs out; anything that cannot be worn again is dropped.
Open points: Ideology/Royalty apparel requirements while suited (exempt the suit, or accept the mood
penalty); quest-locked apparel (refuse entry, or keep it on).

### Helmet

Optional. A frame runs without one: the pilot's head shows out of the collar, head hits reach the pilot,
and the helmet's bonuses are missing. With a helmet: a real headgear item put on when the hatch closes,
using the game's render skip flags (Head, Hair, Beard, Eyes, Tattoos) to hide the head; head armour, and
the suit's sensor bonuses. Broken helmet = no helmet. Suggested bonuses (tunable):
Bulwark aim + melee hit chance; Bughunter aiming delay + accuracy; Miner mining yield; Builder construction
success and speed; Medic tend quality and surgery success.

### Parts and slots

Seven slots: helmet, chest, left arm, right arm, left leg, right leg, pack. Every fitted part can modify the
suit (stat offsets/factors, armour, hit points, power drain, abilities, an arm module) while fitted and not
broken. Suit-specific parts fit only their suit; generic parts fit all. The chest and leg plates that are
part of each suit today become separate parts; each suit comes with its standard set.

### The suit damage model

The pilot stays the real pawn wearing the suit (apparel), so skills, jobs, abilities and mods keep working.
Three layers, outside in:
1. **Plates** (the fitted parts) - own armour and hit points.
2. **Frame systems**, hit once the plate over them is gone or broken:
   leg actuators L/R (move speed, carrying; one gone = limping, both = cannot walk), arm actuators L/R
   (work speed, melee; gone = limp arm, its module offline), drive system - the exposed waist (everything
   slower; gone = frame locks up, pilot trapped), power system - pack mount and auxiliary tank (charge leaks,
   capacity drops; gone = unpowered; a hit tank can rupture), hatch (jammed = pilot cannot get out).
3. **The pilot**, hit when the system there is gone, through gaps, or by very big hits (a share of
   explosions and heavy hits passes through every layer; threshold to tune, e.g. 40% of a part's max HP).
Hits are mapped from the pilot's body part the game picks to the suit part covering it. Severe damage can
kill the pilot. Suggested: legs tracked left and right.
Seen in game: missing plates show the frame; damaged systems spark, smoke, hiss; a status panel with a bar
per plate and system. Repair per part: plates with steel/plasteel, systems at the charging rack with steel
and components (an advanced component for a destroyed system).

### Wreck and dead pilot

The suit at zero (body/drive destroyed): the pilot's clothes are put back on and the suit becomes a
**wreck** holding the pilot, like a cryptosleep casket (a Building_Casket-style container). Suggested: needs
paused inside; another colonist pries it open; a conscious pilot can force their way out slowly. The wreck
can be repaired back into a frame or deconstructed. If the pilot dies inside, the suit loses its identity
and is just a container holding the body until emptied.
Not chosen: making the suit its own pawn that inherits the pilot's skills (vehicle-mod style) - far more
work and fragile; the apparel model gives the same play.
