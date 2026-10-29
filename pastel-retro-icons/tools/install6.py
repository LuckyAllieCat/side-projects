"""Add app icons (icons6*) to the Pastel-Retro theme (never deletes) and rebuild index.theme."""
import os
import shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.expanduser("~/.local/share/icons/Pastel-Retro")
SIZES = [16, 22, 24, 32, 48, 64, 96, 128, 256, 512]
# source file -> [(context, icon name), ...]
import glob
# each icons6*/out/<icon-name>.png becomes that app icon
MAP = {os.path.relpath(p, HERE): [("apps", os.path.basename(p)[:-4])]
       for p in sorted(glob.glob(os.path.join(HERE, "icons6*/out/*.png")))}
CONTEXTS = {"places": "Places", "apps": "Applications", "status": "Status", "mimetypes": "MimeTypes",
            "devices": "Devices"}

os.makedirs(os.path.join(THEME, "source"), exist_ok=True)
for src, targets in MAP.items():
    path = os.path.join(HERE, src)
    shutil.copy(path, os.path.join(THEME, "source"))
    im = Image.open(path).convert("RGBA")
    # re-pad to a uniform 6% margin so siblings share the same visual size
    im = im.crop(im.getbbox())
    side = round(max(im.size) / 0.88)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    im = sq
    for size in SIZES:
        small = im.resize((size, size), Image.LANCZOS)
        for ctx, name in targets:
            d = os.path.join(THEME, f"{size}x{size}", ctx)
            os.makedirs(d, exist_ok=True)
            small.save(os.path.join(d, name + ".png"))

dirs = sorted(f"{s}/{c}" for s in os.listdir(THEME) if s[0].isdigit()
              for c in os.listdir(os.path.join(THEME, s)))
with open(os.path.join(THEME, "index.theme"), "w") as f:
    f.write("[Icon Theme]\nName=Pastel-Retro\nComment=Pastel retro icons (Codex) over Yaru-magenta\n"
            "Inherits=Yaru-magenta,Yaru,Humanity,hicolor\nExample=folder\n")
    f.write("Directories=" + ",".join(dirs) + "\n")
    for d in dirs:
        size, ctx = d.split("/")
        f.write(f"\n[{d}]\nContext={CONTEXTS[ctx]}\nSize={size.split('x')[0]}\nType=Fixed\n")
print("installed", len(MAP), "icons,", len(dirs), "dirs")
