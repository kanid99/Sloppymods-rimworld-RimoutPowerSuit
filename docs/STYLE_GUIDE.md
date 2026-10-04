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

`Source/Art/bulwark_assemble.py` (run with `SOFT=1 PR=88 PT=70 OUT=14 TOP=86`): shoulder plates nested into
the chest's shoulder wedge, a thin (1 px) outline all round them, weapons hung at the outer edges, a ball
joint where each weapon meets its plate, and the chest/helmet inner black lines replaced by shading
(thin dark lines filled from the surrounding paint, leaving a soft crease; openings and the outer
silhouette keep their black).
