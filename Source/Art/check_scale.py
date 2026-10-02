"""Shows candidate paintings the way the game will: processed, painted, and shrunk to the
sizes a pawn takes on screen, beside a reference sprite.

    python3 Source/Art/check_scale.py OUT.png candidate.png [...] [--ref reference.png]

Each row: the processed sprite at full size, then at ~96px (zoomed in), ~64px (default
zoom) and ~40px (zoomed out), then its values alone. A design that turns to noise at 64px
or 40px will look like noise in play, however good it is close up.
"""
import sys

from PIL import Image, ImageDraw

from process_nano import fit, tint, OLIVE

FLOOR = (92, 84, 70, 255)
SIZES = (96, 64, 40)


def row(sprite):
    w = 256 + sum(s + 12 for s in SIZES) + 140
    img = Image.new("RGBA", (w, 256), FLOOR)
    img.alpha_composite(sprite, (0, 0))
    x = 268
    for s in SIZES:
        img.alpha_composite(sprite.resize((s, s), Image.LANCZOS), (x, 128 - s // 2))
        x += s + 12
    grey = sprite.convert("LA").convert("RGBA").resize((128, 128), Image.LANCZOS)
    img.alpha_composite(grey, (x, 64))
    return img


def main(args):
    ref = None
    if "--ref" in args:
        i = args.index("--ref")
        ref = args[i + 1]
        del args[i:i + 2]
    out, cands = args[0], args[1:]
    rows = []
    for c in cands:
        tex, mask = fit(None, c)
        rows.append((c.rsplit("/", 1)[-1], row(tint(tex, mask, OLIVE))))
    if ref:
        rows.append(("reference", row(Image.open(ref).convert("RGBA").resize((256, 256)))))
    sheet = Image.new("RGBA", (rows[0][1].width, 270 * len(rows)), FLOOR)
    d = ImageDraw.Draw(sheet)
    for i, (label, r) in enumerate(rows):
        sheet.alpha_composite(r, (0, i * 270 + 14))
        d.text((4, i * 270), label, fill=(255, 255, 255, 255))
    sheet.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])
