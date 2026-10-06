# Art style guide

## Base: the approved painted set

The suit art is the painted modular set approved in review (Nano Banana Pro paintings, cleaned up and
assembled by `Source/Art/build_parts_prototype.py` and `Source/Art/bulwark_hang.py`):
`Source/Art/nano/modular/` - six chassis, seven helmets, the arm pieces and the hanging weapons in
`weapons/`. Bulwark picks: plated chest (plated 2), eye-plate helmet with lamps on top, shielded arm plates
with weapons hanging straight down. Bughunter picks: chevron chassis, lamps-on-top helmet, flamer and
outward-swung hammer arms.

Rules for new and changed parts (from CLAUDE.md, still in force):
- No arms or legs; helmet + torso + pauldrons/arm pieces + hip plates.
- Readable at the game's ~40-64 px: big smooth plates, a very thick silhouette outline, one accent
  colour, no small details. Check every candidate with `Source/Art/check_scale.py`.
- Grey plates take the suit's colour through the CutoutComplex mask (red = painted).
- New parts are generated from an existing approved part as the reference image (so they keep the same
  painting style), then cut out and fitted with `parts_lib.py`.

## Still-valid lessons from the restyle attempts

The VFE-style redraws were tried and dropped by the owner (archived in
`Source/Art/archive/restyle_attempts/`). What carries over:
- **In game the helmet draws at the head position**, 0.34 of the 1.5-unit mesh above the body = 58 px up on
  a 256 canvas. Preview assembled suits that way, or the helmet looks too low.
- **Scale:** with its helmet the suit should be only slightly bigger than vanilla cataphract armour with
  its helmet.
- **Originality:** check generated parts side by side against VFE Pirates warcaskets and vanilla armour
  before keeping them; never give a generator VFE's or another game's art (Fallout included). Known no-gos:
  the T-shaped visor, twin back exhaust stacks, a round grille snout with hoses.

## Bulwark assembly (current)

`Source/Art/bulwark_assemble.py` (run with `PR=88 PT=70 OUT=14 TOP=86`): shoulder plates nested into the
chest's shoulder wedge with a thin (1 px) outline all round; the chest armour drawn in front of each plate's
dark inner wall, so the chest sits inside the curl of the hook; weapons at the outer edges; a ribbed square
swivel joint (three horizontal ribs) where each weapon meets its plate. Inner black detail lines stay
(removing them by filling looked like a poor eraser job; `SOFT=1` keeps that experiment).

## Bulwark size (agreed)

The assembled suit is drawn at **1.45x** the 256 body canvas so a pawn believably fits inside (checked
with a pawn ghosted in, eyes on the helmet's eye slits: `Source/Art/bulwark_fit_check.py`). The helmet is
scaled up 1.3x on top of that (`HSCALE`, default 1.3) so the pawn's head fits inside it. Leg stubs: knee and foot
only, under the hip armour. This replaces the earlier "only slightly bigger than cataphract" rule.

## Suit kit (game textures for any suit)

`Source/Art/suit_kit.py SRC OUT` turns a suit's parts into one texture + paint mask per piece and facing
(Body, Legs, ArmL, ArmR, Helmet x south/east/north) on a shared 768 canvas, plus `OUT/preview.png`
(stacked as the game draws them, unpainted and in two paints). drawSize 3.26 in game; the helmet texture is
stored 80 px lower because the game draws it at the head position. Each piece is its own texture so it can
later be its own apparel / module and be damaged and lost on its own.
- South layers come from the front-view assembly (`bulwark_assemble.py` with `EXPORT=1` writes
  `kit_src/south_*.png` incl. an arm layer per weapon, with the hole where the chest nests into the plate).
- East = ONE whole side painting of the suit (made from the finished front view, so it keeps the bulk), cut
  into pieces by outlines (`full_east` in the spec). The body, helmet and legs come from a second copy painted
  with the arm removed (`body_image`), so the body under the arm is real (also the arm-destroyed look). The arm
  is moved so its shoulder armour starts at the front view's height. Gun aimed forward.
- The suit's tall backpack (from the side painting) is used in all views: the back painting shows it, the front
  view shows its top peeking out behind the helmet, and from behind it hides the helmet's lower part.
- Check heights across views with `kit/out_bulwark/guides.png` (helmet top, body top, shoulder armour top and
  bottom, weapon bottom, feet must line up).
- North = back painting; the shoulder plates are the front-view plates mirrored and swapped at the same
  height (so they cover the shoulders), each weapon is its own rear view (no muzzles), with the ribbed joint;
  a collar band is drawn over the helmet base.
- East: the near shoulder plate is drawn OVER the helmet (in game the arm's render node goes above the head
  when facing east/west).
- A new suit = a new spec function (like `bulwark_spec`) pointing at its parts. Weapon side views and the
  leg stubs are shared between suits.
Bulwark sources: `Source/Art/kit/bulwark_src/`; output: `Source/Art/kit/out_bulwark/`
(choose weapons with WEAPON_L / WEAPON_R).

## Bulwark view consistency (owner notes)

- Weapons point FORWARD in every view, as they do when firing: front view = end-on art pointing at the viewer
  (`weap_fwd/<w>_south.png`), back view = end-on rear (`weap_fwd/<w>_north.png`), side view = level, muzzle forward.
  Done for minigun and rocket pod; the other eight weapons still need their two end-on paintings.
- Back-view shoulder plates = the front plates mirrored, with the hook interior painted over as solid back
  armour, at the same height as the front and side views.
- Weapons in every view: front = end-on art pointing at the viewer (`weap_fwd/<w>_south`), side = level and
  forward from the elbow (`weap_east`, swapped per loadout onto the painted shoulder), back = rear end at the
  cuff with the weapon running away and down (`weap_back2`). Each hangs from the shoulder plate's own ribbed
  cuff (no extra joint).
- The tower shield is a hand shield, sized from the shoulder to the feet and 1.35x wider than its painting
  (`shield_part`), drawn the VEF way: in front of the body facing south, in
  front of the chest side-on facing east/west, and behind the body facing north (only the edge past the body
  shows). Listed in the spec's `shields`.
- A shield arm draws above the head facing south (listed in `above_head.txt`; in game its render node goes
  above the head for that facing). Facing north the shield's back (front shape mirrored, plain, in shadow) sits
  behind the body. In the side view the far arm is drawn behind everything, a little higher and in shadow, so
  only what sticks out past the body shows (a shield's edge, a barrel's end).

## Bughunter (from the kit)

A Bulwark variant built with almost no new art: `SPEC=bughunter python3 suit_kit.py kit/bughunter_src
kit/out_bughunter`. Its own: the front layers (chevron chest, lamps-on-top helmet) exported by
`bulwark_assemble.py` with `CHAS=chassis_bughunter_v2.png HELM=helmet_bughunter_lamps1.png
KITSRC=.../kit_src EXPORT=1`, and the helmet's side and back paintings (`kit/bughunter_src/own/`, 2 requests).
Current Bughunter export (light plates, smaller helmet, weapons higher):
`PR=88 PT=64 OUT=14 TOP=86 CHAS=chassis_bughunter_v2.png HELM=helmet_bughunter_lamps1.png HSCALE=1.017
WL=flamer WR=hammer PLATE_BASE=arm_light PH=124 PSQ=0.8 NEST=0 PLATES=hammer:arm_pneumatic_lc,flamer:arm_fuel_lc
KITSRC=.../kit_src EXPORT=1`. Where these come from:
- **Helmet:** `HSCALE=1.017` makes it the Bulwark helmet's height (it was 28% taller).
- **Plates:**
  - `PLATE_BASE` is the suit's plain plate, painted as a light open frame from the Bulwark plate.
  - The `PLATES` repaints are that plate with the weapon hardware moved on in code. The hardware was
    cut from heavy-plate repaints by pixel difference (`nano/modular/arm_*_heavy_src.png`).
  - `PSQ` squashes the plate shorter.
  - `NEST=0` keeps the light frame in front of the chest.
  - The export also writes `south_plate{L,R}base`, the plain plate. The kit uses it to place the cuff,
    so hoses don't push the weapon down, and to draw the plate in the back view.
  - In the side view, `east_plates` maps each weapon to the suit's own side-view pauldron painting
    (`own/plate_east_fuel.png`, `own/plate_east_pneumatic.png`), drawn in the painted heavy arm's box.
    Both are repaints of the Bulwark's painted side arm: an open frame with a solid top cap, then the
    hardware swapped. Giving the generator a front-view plate as a reference only gets front views back.
- **Jump pack:** `own/chassis_north_jump.png` (three cells, thrusters) and `own/full_east_noarm_jump.png`.
  `JUMP=0` builds the plain backpack.
Shared with the Bulwark (symlinked): side and back body, legs, shoulder plates, all weapon views.

## Backpacks and the open back (kit)

- **Backpacks are repaints of the plain tall pack** in the back and side paintings:
  - Bughunter jump pack with net launcher: `own/chassis_north_jumpnet.png`, `own/full_east_noarm_jumpnet.png`.
  - Bulwark shield pack (`PACK=shield`): `own/chassis_north_shield.png`, `own/full_east_noarm_shield.png`.
  - `north_ref` and `body_ref` point at the plain pack, so the suit keeps its scale when a launcher or
    pylon sticks up.
  - `over_from` draws what a side-view repaint added near the top (the net launcher) over the helmet.
- **The open back is a gullwing:**
  - The pack swings up on a hinge at the top of the opening, toward the viewer, so we see its inside.
    The inside is drawn in code on the plain pack's outline, flipped and squashed to half height: a lilac
    rim (the paint), a recessed dark face, and harness straps with buckles. The colours are taken from the
    old swing door.
  - Hardware on the pack's outside (thrusters, launcher, pylons) peeks past the lid's edges in shadow.
  - Two hinge knuckles sit where the lid meets the collar.
  - It sits over one doorless cavity painting, `views/chassis_north_cavity.png`, made in code from
    `chassis_north_open4` by mirroring its right half. So any pack opens without new art.
  - The pack is the plain pack's column (`pack_box`) plus whatever the repaint added over
    `pack_base`.
  - Output: `Body_northopen`.

## SVG masters (owner's rule)

Art drawn in code is produced as SVG and converted to PNG; both are committed (`Source/Art/frame/svg/`,
`Source/Art/frame/station/`). `frame_svg.py` records the same drawing calls as vector shapes (Pillow-matching:
outlines sit inside shapes). SVGs that would embed vanilla art (the pawn) stay out of git.

## Power armour station (test, 3x2)

`Source/Art/frame/station.py` (south) and `station_views.py` (north, east): a yellow gantry over a steel deck,
chain hoist with hooks on the frame's shoulders, two clamp arms on its sides, boot clamps, work lamps, a
3-cell charging dock, monitor and tool cabinet. Posts at the station's front corners; the pilot enters from the
open back. East is a side elevation: the near post hides the far one, the beam is end-on on top, the far
clamp arm and the far chain sit a little higher than the near ones. Drawn at the suit's scale (117.8 px per tile); the gantry
rises above the footprint (needs a taller drawSize).

## Armour piece styles (vector sheet, first pass)

`Source/Art/frame/armor_sheet.py` -> `Source/Art/frame/armor/armor_pieces.svg` (+ PNG): five styles drawn to fit the
frame - Heavy (Bulwark: layered slabs, visor slit), Light (Bughunter: slim plates with open cut-outs, bug-eye
lenses), Industrial (Miner: rounded plates, hazard bands, headlamp, radiator pack), Builder (hard hat, tool
loops, cable spool), Medic (glass dome, crosses, diagnostic screens, medicine case) - one piece per slot
(helmet, chest, arms, legs, pack) and each assembled on the frame. Sheet colours only tell the styles apart;
in game the plates take the suit's tint.

### Detailed pass (Heavy first)

`armor_detail.py` writes SVG directly for richer pieces: gradient bodies (lit top, dark bottom), cast shadows
under overlapping plates, inner bevels (lit top-left edge, shaded bottom-right), layered lames, recessed vents
and grilles, bolts with highlights, pistons at elbows and knees, stencils and hazard decals, scratches and edge
wear, soft glow on visors, lights and cell rings. Checked at game size (320 px canvas): it reads at 320 and 160.
Heavy (Bulwark) is done south and north (`armor/armor_heavy_*`); the other four styles still follow.

### Warcasket-like Heavy set (resemble, not copy)

`armor_ws2.py` (renderer `armor_vfe.py`): our own Heavy pieces in the warcasket design language - top-heavy
silhouette, small helmet sunk into a high collar, big rounded dome pauldrons with a rim lip, barrel chest over
banded abdomen, flared hip skirt, thick strong forearms (a broad cuff bulging toward the elbow, an elbow plate over it, a heavy wrist lip), big
round knee guards, short flared greaves; pectorals faded into the main chest plate (a soft light above, a soft blurred shadow under the lower curve,
and a gentle thin line - dark with a faint light line under it - along the lower curve and sternum edge); big smooth
rounded plates; light grey (takes the tint). The recorded no-gos stay out (T visor, twin back exhausts, round
grille snout with hoses). Owner's rule: resemble the design elements, never copy a warcasket.

**Line weight (owner):** RimWorld uses lighter lines than our first passes - a light silhouette outline (3.4 at
the 320 canvas, `SIL_W`), no dark line between plates, and shading without lines to suggest dimension (soft cast
shadows, lit/shaded chamfer faces, form gradients); seams faint.

### Variant: warcasket-like + T-51b influences

`armor_t51.py` -> `armor/armor_heavy_t51_*`: the warcasket-like Heavy set blended with T-51b-inspired elements -
retro rounded forms, raised horizontal strakes (light top edge, soft dark line under) on the pauldrons, forearms,
knees and greaves, rivet rows (brow, collar, pauldron rims, thighs, pack), a ribbed accordion abdomen, a straight
square-ended centre ridge (a narrow tapered keel with rivets read as a necktie - avoid), a heavy brow ridge, and a ribbed respirator with filter canisters that juts in front of the collar.
Influences only: the T-51b helmet face (twin round eye lenses) is not used; our recessed slit visor stays.
