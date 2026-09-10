"""Render the Wordle tile icon as PNGs at the sizes iOS and Android want."""
import glob
from PIL import Image, ImageDraw, ImageFont

GREEN, YELLOW, GREY, BG = "#538d4e", "#b59f3b", "#3a3a3c", "#121213"
LETTERS = [("W", GREEN), ("O", GREY), ("R", YELLOW), ("D", YELLOW), ("L", GREEN), ("E", GREEN), ("", GREEN), ("", GREEN), ("", GREEN)]

def font(size):
    for pat in ["/usr/share/fonts/**/DejaVuSans-Bold.ttf", "/usr/share/fonts/**/LiberationSans-Bold.ttf", "/usr/share/fonts/**/*Bold.ttf"]:
        hits = glob.glob(pat, recursive=True)
        if hits:
            return ImageFont.truetype(hits[0], size)
    return ImageFont.load_default(size=size)

def render(size, maskable=False):
    s = 1024  # draw large, downsample for crisp edges
    img = Image.new("RGB", (s, s), BG)
    d = ImageDraw.Draw(img)
    pad = 176 if maskable else 96   # maskable icons keep content inside the safe zone
    gap = 32
    tile = (s - 2 * pad - 2 * gap) // 3
    f = font(int(tile * 0.62))
    for i, (ch, color) in enumerate(LETTERS):
        r, c = divmod(i, 3)
        x = pad + c * (tile + gap); y = pad + r * (tile + gap)
        d.rounded_rectangle([x, y, x + tile, y + tile], radius=tile // 10, fill=color)
        if ch:
            d.text((x + tile / 2, y + tile / 2), ch, font=f, fill="white", anchor="mm")
    return img.resize((size, size), Image.LANCZOS)

render(180).save("docs/apple-touch-icon.png")
render(192).save("docs/icon-192.png")
render(512).save("docs/icon-512.png")
render(512, maskable=True).save("docs/icon-512-maskable.png")
render(32).save("docs/favicon.png")
print("icons written")
