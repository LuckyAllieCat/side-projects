"""Wordle desktop app: opens the bundled game in a native window."""
import os
import sys
import webview


def resource_path(name: str) -> str:
    # PyInstaller unpacks bundled data into sys._MEIPASS at runtime.
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def main() -> None:
    with open(resource_path("wordle.html"), encoding="utf-8") as f:
        html = f.read()
    webview.create_window(
        "Wordle",
        html=html,
        width=520,
        height=760,
        min_size=(400, 600),
        background_color="#121213",
    )
    webview.start(storage_path=os.path.join(os.path.expanduser("~"), ".wordle"), private_mode=False)


if __name__ == "__main__":
    main()
