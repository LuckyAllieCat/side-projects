# Wordle

A self-contained Wordle clone.

- `docs/` – the web app, served by GitHub Pages. Open it in Safari on an iPhone and choose **Add to Home Screen** to install it; it works offline afterwards.
- `dist/Wordle` – standalone Linux desktop app (built with `./build.sh`, not committed).
- `template.html` + `build.py` – the game source and word lists. Run `python3 build.py` to regenerate both `wordle.html` and `docs/index.html`.
- `make_icons.py` – regenerates the PNG icons in `docs/`.
