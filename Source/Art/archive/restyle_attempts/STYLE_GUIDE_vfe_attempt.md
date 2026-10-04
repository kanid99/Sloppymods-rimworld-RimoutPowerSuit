# Art style guide

Target look: the Vanilla Factions Expanded - Pirates warcaskets. Their style, not their shapes - every
design must stay original (see "Originality" below). The numbers here were measured from the 14 VFE
warcasket textures (south view) with `Source/Art/style/measure_vfe.py`.

## Format

- Three layers, each its own 256x256 texture per facing (`_south`, `_east`, `_north`), exactly like a
  warcasket: **Body** (torso + hip armour), **Shoulders** (pauldrons, drawn over the body), **Helmet**
  (drawn over both). The modular slots map onto these: chassis = Body, arm pieces = Shoulders (left and
  right halves), helmet = Helmet.
- No arms, no legs, no hands. Weapons are not part of the suit art: the pawn holds the equipped weapon
  (VFE Pirates' warcasket guns or ours) and the game draws it, as for any pawn.
- Pure greyscale (measured saturation 0). The game multiplies the whole texture by the suit's colour,
  so white = full colour, grey = shaded colour. No coloured paint, glows or lenses in these textures; a
  coloured accent would need its own overlay layer.

## Proportions (fraction of the 256 canvas, south view)

| Layer     | Width        | Height       | Notes                                                    |
|-----------|--------------|--------------|----------------------------------------------------------|
| Body      | 0.70 - 0.80  | 0.86 - 0.98  | a bulky rounded block; mostly hidden behind the helmet    |
| Shoulders | 0.95 - 1.00  | 0.38 - 0.55  | the widest layer: the silhouette is set by the shoulders |
| Helmet    | 0.45 - 0.53  | 0.47 - 0.55  | big: half the sprite's width, sitting low over the collar |

Placement on the canvas (median bounding box, pixels x0,y0 - x1,y1; the game stacks the three layers on
the same 256 canvas, so these positions are what line them up):

| Layer     | Box (median)        | Range of tops / bottoms |
|-----------|---------------------|-------------------------|
| Body      | 35,19 - 220,253     | top 1 - 19, bottom to 255 |
| Shoulders | 0,54 - 255,157      | top 7 - 54, bottom to 195 |
| Helmet    | 67,65 - 188,197     | top 57 - 65, bottom to 214 |

In game the helmet is NOT drawn where its texture places it: RimWorld draws it at the head position,
0.34 of the 1.5-unit pawn mesh above the body = **58 px up** on the 256 canvas (checked against an in-game
screenshot of the Cataphract warcasket). So the helmet covers the collar opening and the top of the chest;
what shows of the body is the band below the helmet (about y 150 - 255) - put the body's visible feature
there. Always preview layers stacked this way (`Source/Art/style/preview.py`), never all at the same spot.

The assembled sprite is a compact, nearly square mass, wider than it is tall: helmet in front of the
upper torso, pauldrons out to the canvas edges, hip plates at the bottom. Not a human torso shape.

## Line

- Every plate has a solid black outline. Body and shoulders: **4 px** at 256. Helmet: **8 px** (it is the
  focal part).
- Plates overlap, and each overlapping plate's outline makes the inner lines; extra inner lines are rare
  and **2 - 4 px**. No hairlines, no grey lines.

## Tone (greyscale values, 0-255)

| Use                               | Value       |
|-----------------------------------|-------------|
| Top / facing planes               | 245 - 255   |
| Gentle gradient on big planes     | top 255 -> bottom ~225 (vertical, linear) |
| Side and bevel planes             | 200 - 215   |
| Underside / recessed plates       | 160 - 185   |
| Openings, visor, vents, sockets   | 70 - 100    |
| Outline                           | 0 - 20      |

Median tone of a VFE body is about 205 and of a helmet about 200: the art is **mostly white**. Dimension
comes from hard steps between flat planes (faceting) plus the one gentle vertical gradient - not from
soft airbrushed shading, rim lights, highlights or cast shadows.

## Form

- Build from big rounded masses: a domed helmet, domed pauldrons, a barrel chest. Avoid flat boxes.
- Rounded parts get a lit cap (a brighter, unstroked patch toward the top-left) and a shaded underside or side.
- A face reads through a heavy brow over deep-set eye recesses, a centre ridge on the faceplate and a jaw
  piece that stands out (lit top face, darker front).

## Detail

- Large shapes only. Per layer, at most a handful of small marks: a pair of vent slots, a round
  socket, one seam, two to four round bolt bumps. No rivets, bolts, grilles, texture, scratches, text or decals.
- The visor/eyes are dark-grey shapes (70 - 100), not glowing colour, drawn as recesses: a thin line
  (1.5 - 2 px, not the 4 px plate outline), a lighter strip (~130) along the inside bottom edge where the far
  wall catches light, and a soft bevel rim (~210) around the opening. That is what gives them depth.
- Lamps, sensors and similar fittings are set into the shell as recessed windows (bevel rim, thin-lined
  recess, a bright lens), not separate bulbs stuck on top.
- Prefer smooth curves for big face plates (a brow is one arch across the face, not a jagged band).
- Keep features apart: leave clear plate between eyes, mouth and other openings so their lines never run
  into each other.

## Originality

- Before a design is kept, put it next to every VFE warcasket (helmet and body) and the vanilla armours
  and reject anything that matches one. Never give an image generator VFE or another game's art.
- Inspiration from Fallout-style power armour is limited to principles (rounded masses, deep-set eyes, faceplate
  ridge, protruding jaw). Never its round grille snout with hoses, its eye shape or its decals.
- Known no-gos: the T-shaped visor (VFE Marine, Fallout), twin vertical exhaust stacks on the back
  (VFE Cataphract/Siegebreaker), the round-faced helmet with a hex jaw (VFE Brute).

## Checks for every texture

1. Measure it with `Source/Art/style/measure_layer.py` against the table above.
2. View it assembled next to two VFE warcaskets at 256 and at in-game size (64 px), on a ground colour.

## Tools

- `Source/Art/style/rw_style.py`: draws a layer at 4x (1024) and outputs 256. `plate(mask, top, bottom,
  stroke)` = a flat plane with an optional vertical gradient and a black stroke; later plates overlap
  earlier ones, so their strokes become the inner lines. `mark()` = a small dark slot.
- `Source/Art/style/measure_layer.py`: box, fill, outline width, median tone and saturation of a layer.
- Art v2 lives in `Source/Art/v2/` (one script per suit, three layer textures per facing).
