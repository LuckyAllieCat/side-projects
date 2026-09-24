import sys, glob
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(f"{d}/out/*.png"))
ims = []
for f in fs:
    i = Image.open(f).convert("RGBA"); ims.append(i)
    print(f, i.size, [i.getpixel(c)[3] for c in [(0, 0), (i.width-1, 0), (0, i.height-1), (i.width-1, i.height-1)]])
S = 180
sheet = Image.new("RGBA", ((S+16)*len(ims)+16, S+32), (214, 160, 240, 255))
for k, i in enumerate(ims):
    i = i.crop(i.getbbox()); side = round(max(i.size)/0.88)
    sq = Image.new("RGBA", (side, side)); sq.paste(i, ((side-i.width)//2, (side-i.height)//2))
    sheet.alpha_composite(sq.resize((S, S), Image.LANCZOS), (16+k*(S+16), 16))
sheet.save(f"{d}/preview.png")
