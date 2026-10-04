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
- The tower shield is a hand shield, drawn the VEF way: a big shield in front of the body facing south, in
  front of the chest side-on facing east/west, and behind the body facing north (only the edge past the body
  shows). Listed in the spec's `shields`.
