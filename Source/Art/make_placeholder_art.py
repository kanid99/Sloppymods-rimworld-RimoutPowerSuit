"""Placeholder art for the power suit frame, drawn with Pillow.

    python3 Source/Art/make_placeholder_art.py

Writes the standing suit (Textures/Things/Item/PowerSuit), the worn suit for every adult
body type in three directions (Textures/Things/Pawn/PowerSuit; west mirrors east), the
"Climb out" command icon and About/Preview.png. Stand-in art until the real suits are drawn.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
S = 256                     # canvas
STEEL = (86, 92, 88, 255)
PLATE = (122, 118, 84, 255)  # olive plate
DARK = (38, 40, 40, 255)
EDGE = (24, 24, 24, 255)
VISOR = (255, 196, 70, 255)
LIGHT = (164, 160, 120, 255)
BODY_WIDTH = {"Male": 1.0, "Female": 0.94, "Thin": 0.9, "Fat": 1.12, "Hulk": 1.14}


def rect(d, box, fill, r=10):
    d.rounded_rectangle(box, r, fill=fill, outline=EDGE, width=4)


def suit(direction, w=1.0):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = S // 2

    def x(off):
        return cx + off * w

    if direction in ("south", "north"):
        # legs
        for side in (-1, 1):
            rect(d, (x(side * 30) - 20, 150, x(side * 30) + 20, 228), STEEL, 8)
            rect(d, (x(side * 30) - 24, 212, x(side * 30) + 24, 236), DARK, 6)
            rect(d, (x(side * 30) - 18, 168, x(side * 30) + 18, 192), PLATE, 6)
        # arms
        for side in (-1, 1):
            rect(d, (x(side * 74) - 20, 92, x(side * 74) + 20, 176), STEEL, 10)
            rect(d, (x(side * 74) - 22, 160, x(side * 74) + 22, 190), DARK, 8)
        # torso
        rect(d, (x(-54), 80, x(54), 166), PLATE, 16)
        rect(d, (x(-40), 120, x(40), 160), STEEL, 10)
        # shoulder pauldrons
        for side in (-1, 1):
            rect(d, (x(side * 76) - 30, 74, x(side * 76) + 30, 112), PLATE, 14)
        # helmet
        rect(d, (cx - 34, 30, cx + 34, 92), PLATE, 18)
        if direction == "south":
            rect(d, (cx - 24, 50, cx + 24, 66), DARK, 6)
            d.rectangle((cx - 20, 54, cx + 20, 62), fill=VISOR)
            d.rectangle((cx - 14, 72, cx + 14, 86), fill=DARK)
            d.ellipse((cx - 8, 128, cx + 8, 144), fill=VISOR, outline=EDGE, width=3)
        else:
            # backpack / power cell housing
            rect(d, (x(-36), 86, x(36), 150), STEEL, 10)
            rect(d, (cx - 16, 96, cx + 16, 138), DARK, 6)
            d.rectangle((cx - 10, 104, cx + 10, 130), fill=(90, 200, 255, 255))
    else:  # east; west is drawn mirrored by the game
        rect(d, (cx - 26, 150, cx + 2, 228), STEEL, 8)          # back leg
        rect(d, (cx + 2, 150, cx + 30, 228), STEEL, 8)          # front leg
        rect(d, (cx - 4, 212, cx + 44, 236), DARK, 6)           # boot
        rect(d, (cx - 66, 86, cx - 22, 152), STEEL, 10)         # backpack
        rect(d, (cx - 60, 98, cx - 40, 140), DARK, 6)
        d.rectangle((cx - 56, 104, cx - 44, 132), fill=(90, 200, 255, 255))
        rect(d, (cx - 36, 80, cx + 40, 166), PLATE, 16)         # torso
        rect(d, (cx - 18, 30, cx + 40, 92), PLATE, 18)          # helmet
        rect(d, (cx + 22, 50, cx + 46, 66), DARK, 6)
        d.rectangle((cx + 28, 54, cx + 46, 62), fill=VISOR)
        rect(d, (cx - 12, 92, cx + 22, 186), STEEL, 10)         # arm
        rect(d, (cx - 26, 74, cx + 30, 114), PLATE, 14)         # pauldron
        rect(d, (cx - 14, 168, cx + 24, 196), DARK, 8)          # fist
    # soft highlight so it reads as metal, not flat paper
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rectangle((0, 0, S, S // 3), fill=(255, 255, 255, 28))
    alpha = img.split()[3]
    img = Image.alpha_composite(img, Image.composite(hl, Image.new("RGBA", (S, S)), alpha))
    return img


def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    for body, w in BODY_WIDTH.items():
        for direction in ("south", "north", "east"):
            save(suit(direction, w), "Textures", "Things", "Pawn", "PowerSuit",
                 "PowerSuitFrame_%s_%s.png" % (body, direction))

    # The standing suit: the same frame from the front, with a ground shadow.
    standing = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((50, 214, 206, 246), fill=(0, 0, 0, 110))
    standing = Image.alpha_composite(standing, shadow.filter(ImageFilter.GaussianBlur(5)))
    standing = Image.alpha_composite(standing, suit("south"))
    save(standing, "Textures", "Things", "Item", "PowerSuit", "PowerSuitFrame.png")

    icon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    icon.alpha_composite(suit("south").resize((200, 200), Image.LANCZOS), (8, 28))
    d = ImageDraw.Draw(icon)
    d.polygon([(170, 120), (246, 120), (246, 96), (256, 128), (246, 160), (246, 136), (170, 136)],
              fill=(240, 240, 240, 255), outline=EDGE)
    save(icon.resize((128, 128), Image.LANCZOS), "Textures", "UI", "Commands", "RPS_ExitPowerSuit.png")

    preview = Image.new("RGBA", (640, 360), (44, 48, 46, 255))
    d = ImageDraw.Draw(preview)
    for i in range(0, 640, 32):
        d.line((i, 0, i, 360), fill=(52, 56, 54, 255))
    for i in range(0, 360, 32):
        d.line((0, i, 640, i), fill=(52, 56, 54, 255))
    big = standing.resize((340, 340), Image.LANCZOS)
    preview.alpha_composite(big, (150, 10))
    save(preview.convert("RGB"), "About", "Preview.png")


if __name__ == "__main__":
    main()
