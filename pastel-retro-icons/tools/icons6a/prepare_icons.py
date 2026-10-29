from collections import deque
from pathlib import Path

from PIL import Image


SOURCES = {
    "slack.png": Path("/home/luckyalliecat/.codex/generated_images/01a0d2ad-558f-7081-9edf-54ece403f595/exec-a5d2e507-b926-4878-9dfd-1ec9845bad7b.png"),
    "whatsapp.png": Path("/home/luckyalliecat/.codex/generated_images/01a0d2ad-558f-7081-9edf-54ece403f595/exec-7ff9aa8f-d77e-461e-99b8-a08a696a391c.png"),
    "yt-dlp-desktop.png": Path("/home/luckyalliecat/.codex/generated_images/01a0d2ad-558f-7081-9edf-54ece403f595/exec-e40028a4-6ead-4f23-8f50-c2c5db31073d.png"),
    "keyglance.png": Path("/home/luckyalliecat/.codex/generated_images/01a0d2ad-558f-7081-9edf-54ece403f595/exec-fff17e69-362f-4f4c-9239-890d840325bd.png"),
}


def remove_corner_background(image: Image.Image) -> Image.Image:
    """Flood-fill neutral generated backdrops from the canvas boundary."""
    rgba = image.convert("RGBA")
    px = rgba.load()
    width, height = rgba.size
    seen = bytearray(width * height)
    queue = deque()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(1, height - 1):
        queue.append((0, y))
        queue.append((width - 1, y))

    def is_backdrop(x: int, y: int) -> bool:
        r, g, b, _ = px[x, y]
        return max(r, g, b) - min(r, g, b) <= 40

    while queue:
        x, y = queue.popleft()
        offset = y * width + x
        if seen[offset] or not is_backdrop(x, y):
            continue
        seen[offset] = 1
        px[x, y] = (0, 0, 0, 0)
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))
    return rgba


def crop_and_square(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("background removal produced an empty image")
    cropped = image.crop(bbox)
    # A 6% margin on each side means content occupies 88% of the square.
    side = max(512, round(max(cropped.size) / 0.88))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    x = (side - cropped.width) // 2
    y = (side - cropped.height) // 2
    canvas.alpha_composite(cropped, (x, y))
    return canvas


def main() -> None:
    output_dir = Path("out")
    output_dir.mkdir(exist_ok=True)
    for filename, source in SOURCES.items():
        final = crop_and_square(remove_corner_background(Image.open(source)))
        destination = output_dir / filename
        final.save(destination, "PNG")
        corners = [
            final.getpixel((0, 0))[3],
            final.getpixel((final.width - 1, 0))[3],
            final.getpixel((0, final.height - 1))[3],
            final.getpixel((final.width - 1, final.height - 1))[3],
        ]
        if final.mode != "RGBA" or corners != [0, 0, 0, 0]:
            raise ValueError(f"invalid output: {destination}")
        print(f"{destination}: {final.size[0]}x{final.size[1]} {final.mode}")


if __name__ == "__main__":
    main()
