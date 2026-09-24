#!/usr/bin/python3
"""Key Glance: a tiny always-on-top keyboard map for Spanish, Turkish Q and Russian ЙЦУКЕН.

The layout buttons switch the real GNOME keyboard layout; the bubble also follows
switches made elsewhere (Super+Space, Settings).

Runs on the system Python with GTK3 (python3-gi). Forces the X11 backend so
"keep above" works under GNOME Wayland (via XWayland).
"""
import json
import os
import sys

os.environ.setdefault("GDK_BACKEND", "x11")
os.environ.setdefault("NO_AT_BRIDGE", "1")

import gi  # noqa: E402
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("IBus", "1.0")
from gi.repository import Gdk, Gio, GLib, Gtk, IBus  # noqa: E402

CONFIG = os.path.expanduser("~/.config/keyglance.json")
U = 38          # key unit in px
GAP = 4
PAD = 8
HEADER = 30

# Physical ISO keyboard: (code, width in units). Enter is drawn separately.
ROWS = [
    [("Backquote", 1), ("Digit1", 1), ("Digit2", 1), ("Digit3", 1), ("Digit4", 1), ("Digit5", 1), ("Digit6", 1),
     ("Digit7", 1), ("Digit8", 1), ("Digit9", 1), ("Digit0", 1), ("Minus", 1), ("Equal", 1), ("Backspace", 2)],
    [("Tab", 1.5), ("KeyQ", 1), ("KeyW", 1), ("KeyE", 1), ("KeyR", 1), ("KeyT", 1), ("KeyY", 1), ("KeyU", 1),
     ("KeyI", 1), ("KeyO", 1), ("KeyP", 1), ("BracketLeft", 1), ("BracketRight", 1), ("Enter", 1.5)],
    [("CapsLock", 1.75), ("KeyA", 1), ("KeyS", 1), ("KeyD", 1), ("KeyF", 1), ("KeyG", 1), ("KeyH", 1), ("KeyJ", 1),
     ("KeyK", 1), ("KeyL", 1), ("Semicolon", 1), ("Quote", 1), ("Backslash", 1), ("Enter2", 1.25)],
    [("ShiftLeft", 1.25), ("IntlBackslash", 1), ("KeyZ", 1), ("KeyX", 1), ("KeyC", 1), ("KeyV", 1), ("KeyB", 1),
     ("KeyN", 1), ("KeyM", 1), ("Comma", 1), ("Period", 1), ("Slash", 1), ("ShiftRight", 2.75)],
]
MODS = {"Backspace": "⌫", "Tab": "⇥", "Enter": "⏎", "Enter2": "⏎", "CapsLock": "⇪", "ShiftLeft": "⇧", "ShiftRight": "⇧"}

# What is printed on the physical keys.
ENGRAVING = {
    "es": {"Backquote": "º", "Minus": "'", "Equal": "¡", "BracketLeft": "`", "BracketRight": "+", "Backslash": "ç",
           "Semicolon": "ñ", "Quote": "´", "IntlBackslash": "<", "Comma": ",", "Period": ".", "Slash": "-"},
    "us": {"Backquote": "`", "Minus": "-", "Equal": "=", "BracketLeft": "[", "BracketRight": "]", "Backslash": "\\",
           "Semicolon": ";", "Quote": "'", "IntlBackslash": "<", "Comma": ",", "Period": ".", "Slash": "/"},
}
for _e in ENGRAVING.values():
    for _i in range(10):
        _e[f"Digit{_i}"] = str(_i)
    for _c in "QWERTYUIOPASDFGHJKLZXCVBNM":
        _e[f"Key{_c}"] = _c

# (base, shift, altgr)
TR = {
    "Backquote": ('"', "é", "<"), "Digit1": ("1", "!", ">"), "Digit2": ("2", "'", "£"), "Digit3": ("3", "^", "#"),
    "Digit4": ("4", "+", "$"), "Digit5": ("5", "%", "½"), "Digit6": ("6", "&", "¾"), "Digit7": ("7", "/", "{"),
    "Digit8": ("8", "(", "["), "Digit9": ("9", ")", "]"), "Digit0": ("0", "=", "}"), "Minus": ("*", "?", "\\"),
    "Equal": ("-", "_", "|"),
    "KeyQ": ("q", "Q", "@"), "KeyW": ("w", "W", ""), "KeyE": ("e", "E", "€"), "KeyR": ("r", "R", ""),
    "KeyT": ("t", "T", "₺"), "KeyY": ("y", "Y", ""), "KeyU": ("u", "U", ""), "KeyI": ("ı", "I", ""),
    "KeyO": ("o", "O", ""), "KeyP": ("p", "P", ""), "BracketLeft": ("ğ", "Ğ", "¨"), "BracketRight": ("ü", "Ü", "~"),
    "Backslash": (",", ";", "`"),
    "KeyA": ("a", "A", "æ"), "KeyS": ("s", "S", "ß"), "KeyD": ("d", "D", ""), "KeyF": ("f", "F", ""),
    "KeyG": ("g", "G", ""), "KeyH": ("h", "H", ""), "KeyJ": ("j", "J", ""), "KeyK": ("k", "K", ""),
    "KeyL": ("l", "L", ""), "Semicolon": ("ş", "Ş", "´"), "Quote": ("i", "İ", ""),
    "IntlBackslash": ("<", ">", "|"), "KeyZ": ("z", "Z", ""), "KeyX": ("x", "X", ""), "KeyC": ("c", "C", ""),
    "KeyV": ("v", "V", ""), "KeyB": ("b", "B", ""), "KeyN": ("n", "N", ""), "KeyM": ("m", "M", ""),
    "Comma": ("ö", "Ö", ""), "Period": ("ç", "Ç", ""), "Slash": (".", ":", ""),
}
RU = {
    "Backquote": ("ё", "Ё", ""), "Digit1": ("1", "!", ""), "Digit2": ("2", '"', ""), "Digit3": ("3", "№", ""),
    "Digit4": ("4", ";", ""), "Digit5": ("5", "%", ""), "Digit6": ("6", ":", ""), "Digit7": ("7", "?", ""),
    "Digit8": ("8", "*", ""), "Digit9": ("9", "(", ""), "Digit0": ("0", ")", ""), "Minus": ("-", "_", ""),
    "Equal": ("=", "+", ""),
    "KeyQ": ("й", "Й", ""), "KeyW": ("ц", "Ц", ""), "KeyE": ("у", "У", ""), "KeyR": ("к", "К", ""),
    "KeyT": ("е", "Е", ""), "KeyY": ("н", "Н", ""), "KeyU": ("г", "Г", ""), "KeyI": ("ш", "Ш", ""),
    "KeyO": ("щ", "Щ", ""), "KeyP": ("з", "З", ""), "BracketLeft": ("х", "Х", ""), "BracketRight": ("ъ", "Ъ", ""),
    "Backslash": ("\\", "/", ""),
    "KeyA": ("ф", "Ф", ""), "KeyS": ("ы", "Ы", ""), "KeyD": ("в", "В", ""), "KeyF": ("а", "А", ""),
    "KeyG": ("п", "П", ""), "KeyH": ("р", "Р", ""), "KeyJ": ("о", "О", ""), "KeyK": ("л", "Л", ""),
    "KeyL": ("д", "Д", ""), "Semicolon": ("ж", "Ж", ""), "Quote": ("э", "Э", ""),
    "IntlBackslash": ("/", "|", ""), "KeyZ": ("я", "Я", ""), "KeyX": ("ч", "Ч", ""), "KeyC": ("с", "С", ""),
    "KeyV": ("м", "М", ""), "KeyB": ("и", "И", ""), "KeyN": ("т", "Т", ""), "KeyM": ("ь", "Ь", ""),
    "Comma": ("б", "Б", ""), "Period": ("ю", "Ю", ""), "Slash": (".", ",", ""),
}
ES = {
    "Backquote": ("º", "ª", "\\"), "Digit1": ("1", "!", "|"), "Digit2": ("2", '"', "@"), "Digit3": ("3", "·", "#"),
    "Digit4": ("4", "$", "~"), "Digit5": ("5", "%", "€"), "Digit6": ("6", "&", "¬"), "Digit7": ("7", "/", ""),
    "Digit8": ("8", "(", ""), "Digit9": ("9", ")", ""), "Digit0": ("0", "=", ""), "Minus": ("'", "?", ""),
    "Equal": ("¡", "¿", ""),
    "BracketLeft": ("`", "^", "["), "BracketRight": ("+", "*", "]"), "Backslash": ("ç", "Ç", "}"),
    "Semicolon": ("ñ", "Ñ", ""), "Quote": ("´", "¨", "{"),
    "IntlBackslash": ("<", ">", ""), "Comma": (",", ";", ""), "Period": (".", ":", ""), "Slash": ("-", "_", ""),
}
for _c in "QWERTYUIOPASDFGHJKLZXCVBNM":
    ES[f"Key{_c}"] = (_c.lower(), _c, "€" if _c == "E" else "")

# id -> (label, keymap, xkb id, ibus engine prefix)
LAYOUTS = {
    "es": ("Español", ES, "es", "xkb:es"),
    "tr": ("Türkçe", TR, "tr", "xkb:tr"),
    "ru": ("Русский", RU, "ru", "xkb:ru"),
}
ORDER = ["es", "tr", "ru"]
INPUT_SOURCES = "org.gnome.desktop.input-sources"


def system_layout():
    """Which of our layouts GNOME currently types with, or None."""
    try:
        name = IBus.Bus().get_global_engine().get_name()
    except Exception:
        return None
    for lay, (_l, _m, _x, prefix) in LAYOUTS.items():
        if name.startswith(prefix):
            return lay
    return None


def switch_system_layout(lay):
    """Make GNOME type with `lay`.

    GNOME Shell re-activates the first source whenever the sources list changes,
    but only if its most-recently-used memory has fewer than two entries. So:
    collapse the list to the wanted source (resets that memory), then restore
    the full list with the wanted source first.
    """
    gs = Gio.Settings.new(INPUT_SOURCES)
    xkb = LAYOUTS[lay][2]
    current = [tuple(x) for x in gs.get_value("sources").unpack()]
    others = [x for x in current if x != ("xkb", xkb)]
    for want in ORDER:
        if ("xkb", LAYOUTS[want][2]) not in others and want != lay:
            others.append(("xkb", LAYOUTS[want][2]))
    gs.set_value("sources", GLib.Variant("a(ss)", [("xkb", xkb)]))
    Gio.Settings.sync()

    def restore():
        gs.set_value("sources", GLib.Variant("a(ss)", [("xkb", xkb)] + others))
        Gio.Settings.sync()
        return False
    GLib.timeout_add(350, restore)
    return 500  # ms until the restore has run


def cycle_system_layout():
    cur = system_layout()
    nxt = ORDER[(ORDER.index(cur) + 1) % len(ORDER)] if cur in ORDER else ORDER[0]
    return switch_system_layout(nxt), nxt

CSS = b"""
window, .bubble { background: rgba(18,19,24,0.97); border-radius: 14px; }
.bubble { padding: 8px; }
label { color: #f2f2f5; font-family: "Noto Sans", "DejaVu Sans", sans-serif; }
.pill { background: rgba(255,255,255,0.05); border-radius: 6px; padding: 0 10px; min-height: 22px; }
.pill:hover { background: rgba(255,255,255,0.10); }
.pill label { font-size: 12px; font-weight: 600; color: #9ea3b0; }
.pill.on label { color: #f2f2f5; }
.pill.on { background: rgba(255,255,255,0.14); }
.pill.es.on { background: rgba(243,198,107,0.22); }
.pill.tr.on { background: rgba(64,202,192,0.22); }
.pill.ru.on { background: rgba(240,112,138,0.22); }
.dot { min-width: 6px; min-height: 6px; border-radius: 3px; margin-right: 6px; }
.dot.es { background: #f3c66b; } .dot.tr { background: #40cac0; } .dot.ru { background: #f0708a; }
.key { background: #262a34; border-radius: 5px; border: 1px solid rgba(0,0,0,0.5); }
.key.mod { background: #1c1f27; }
.key.iso { background: repeating-linear-gradient(135deg, #262a34 0px, #262a34 5px, #2d3140 5px, #2d3140 7px); }
.key.diff.es { background: rgba(243,198,107,0.16); border-color: rgba(243,198,107,0.45); }
.key.diff.tr { background: rgba(64,202,192,0.16); border-color: rgba(64,202,192,0.45); }
.key.diff.ru { background: rgba(240,112,138,0.16); border-color: rgba(240,112,138,0.45); }
.main { font-size: 17px; font-weight: 600; }
.main.long { font-size: 12px; }
.key.diff.es .main { color: #f3c66b; } .key.diff.tr .main { color: #40cac0; } .key.diff.ru .main { color: #f0708a; }
.eng { font-size: 9px; font-weight: 700; color: #6b7080; }
.sec { font-size: 10px; color: #9ea3b0; }
.alt { font-size: 9px; }
.es .alt { color: #f3c66b; } .tr .alt { color: #40cac0; } .ru .alt { color: #f0708a; }
.mod label { font-size: 13px; color: #9ea3b0; }
"""


def load_config():
    try:
        with open(CONFIG) as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    try:
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        with open(CONFIG, "w") as f:
            json.dump(cfg, f)
    except Exception:
        pass


def label(text, cls, halign, valign, mx=4, my=1):
    lb = Gtk.Label(label=text)
    lb.get_style_context().add_class(cls)
    lb.set_halign(halign)
    lb.set_valign(valign)
    lb.set_margin_start(mx)
    lb.set_margin_end(mx)
    lb.set_margin_top(my)
    lb.set_margin_bottom(my)
    return lb


class Key(Gtk.EventBox):
    def __init__(self, code, wu):
        super().__init__()
        self.code = code
        self.get_style_context().add_class("key")
        self.set_size_request(int(wu * U + (wu - 1) * GAP), U)
        ov = Gtk.Overlay()
        self.add(ov)
        if code in MODS:
            self.get_style_context().add_class("mod")
            ov.add(label(MODS[code], "modl", Gtk.Align.START, Gtk.Align.END, 6, 3))
            return
        if code == "IntlBackslash":
            self.get_style_context().add_class("iso")
        self.main = label("", "main", Gtk.Align.START, Gtk.Align.END, 5, 2)
        self.eng = label("", "eng", Gtk.Align.START, Gtk.Align.START, 5, 2)
        self.sec = label("", "sec", Gtk.Align.END, Gtk.Align.START, 5, 2)
        self.alt = label("", "alt", Gtk.Align.END, Gtk.Align.END, 5, 3)
        ov.add(self.main)
        for w in (self.eng, self.sec, self.alt):
            ov.add_overlay(w)
            ov.set_overlay_pass_through(w, True)

    def update(self, lay, keymap, eng, shift, altgr):
        if self.code in MODS:
            return
        base, sh, ag = keymap.get(self.code, ("", "", ""))
        printed = eng.get(self.code, "")
        differs = bool(base) and base.lower() != printed.lower()
        main = ag if (altgr and ag) else (sh if shift else base)
        small = base if (shift or altgr) else (sh if sh != base.upper() else "")
        self.main.set_text(main)
        self.main.get_style_context().remove_class("long")
        if len(main) > 1:
            self.main.get_style_context().add_class("long")
        self.eng.set_text(printed)
        self.sec.set_text(small)
        self.alt.set_text("" if altgr else ag)
        sc = self.get_style_context()
        for c in ("diff", "es", "tr", "ru"):
            sc.remove_class(c)
        sc.add_class(lay)
        if differs:
            sc.add_class("diff")
        self.set_tooltip_text(f"{printed} key → {base}" + (f"   Shift: {sh}" if sh else "") + (f"   AltGr: {ag}" if ag else ""))


class Pill(Gtk.EventBox):
    def __init__(self, text, cls=None, dot=False):
        super().__init__()
        self.get_style_context().add_class("pill")
        if cls:
            self.get_style_context().add_class(cls)
        box = Gtk.Box(spacing=0)
        box.set_valign(Gtk.Align.CENTER)
        if dot:
            d = Gtk.Box()
            d.get_style_context().add_class("dot")
            d.get_style_context().add_class(cls)
            d.set_valign(Gtk.Align.CENTER)
            box.pack_start(d, False, False, 0)
        self.lbl = Gtk.Label(label=text)
        box.pack_start(self.lbl, False, False, 0)
        self.add(box)

    def set_on(self, on):
        sc = self.get_style_context()
        sc.add_class("on") if on else sc.remove_class("on")


class KeyGlance(Gtk.Window):
    def __init__(self):
        super().__init__(title="Key Glance")
        self.cfg = load_config()
        self.layout = self.cfg.get("layout", "tr")
        self.engraving = self.cfg.get("engraving", self.detect_engraving())
        self.shift = False
        self.altgr = False
        self.placed = False

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_resizable(False)
        self.stick()
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        outer.get_style_context().add_class("bubble")
        self.add(outer)

        # header
        hdr = Gtk.Box(spacing=6)
        outer.pack_start(hdr, False, False, 0)
        self.pills = {lay: Pill(LAYOUTS[lay][0], lay, dot=True) for lay in ORDER}
        self.p_shift = Pill("⇧ Shift")
        self.p_alt = Pill("AltGr")
        self.p_eng = Pill("")
        self.p_close = Pill("✕")
        for lay in ORDER:
            hdr.pack_start(self.pills[lay], False, False, 0)
            self.pills[lay].connect("button-press-event", lambda _w, _e, lay=lay: self.choose(lay))
        sp = Gtk.Box(); sp.set_size_request(8, 1); hdr.pack_start(sp, False, False, 0)
        hdr.pack_start(self.p_shift, False, False, 0)
        hdr.pack_start(self.p_alt, False, False, 0)
        hdr.pack_end(self.p_close, False, False, 0)
        hdr.pack_end(self.p_eng, False, False, 0)
        self.p_shift.connect("button-press-event", lambda *a: self.toggle("shift"))
        self.p_alt.connect("button-press-event", lambda *a: self.toggle("altgr"))
        self.p_eng.connect("button-press-event", lambda *a: self.toggle("engraving"))
        self.p_close.connect("button-press-event", lambda *a: self.destroy())

        # keys
        self.keys = []
        for row in ROWS:
            rb = Gtk.Box(spacing=GAP)
            outer.pack_start(rb, False, False, 0)
            for code, wu in row:
                k = Key(code, wu)
                rb.pack_start(k, False, False, 0)
                self.keys.append(k)

        # drag anywhere else, right-click flips layout, scroll flips layout
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.SCROLL_MASK)
        self.connect("button-press-event", self.on_press)
        self.connect("scroll-event", lambda *a: self.flip())
        self.connect("destroy", Gtk.main_quit)
        self.connect("configure-event", self.on_configure)
        self.connect("key-press-event", self.on_key)
        self.connect("key-release-event", self.on_key)

        try:
            self.bus = IBus.Bus()
            self.bus.set_watch_ibus_signal(True)
            self.bus.connect("global-engine-changed", lambda _b, _n: self.follow_system())
            self.follow_system()
        except Exception:
            self.bus = None

        self.refresh()
        self.show_all()
        GLib.idle_add(self.place)

    # --- state -------------------------------------------------------------
    def detect_engraving(self):
        try:
            gs = Gio.Settings.new("org.gnome.desktop.input-sources")
            srcs = gs.get_value("sources").unpack()
            first = srcs[0][1] if srcs else "us"
            return "es" if first.startswith("es") else "us"
        except Exception:
            return "us"

    def set_layout(self, lay, persist=True):
        self.layout = lay
        if persist:
            self.cfg["layout"] = lay
            save_config(self.cfg)
        self.refresh()
        return True

    def flip(self):
        return self.choose(ORDER[(ORDER.index(self.layout) + 1) % len(ORDER)])

    def toggle(self, what):
        if what == "shift":
            self.shift = not self.shift
        elif what == "altgr":
            self.altgr = not self.altgr
        else:
            self.engraving = "us" if self.engraving == "es" else "es"
            self.cfg["engraving"] = self.engraving
            save_config(self.cfg)
        self.refresh()
        return True

    def refresh(self):
        keymap = LAYOUTS[self.layout][1]
        eng = ENGRAVING[self.engraving]
        for k in self.keys:
            k.update(self.layout, keymap, eng, self.shift, self.altgr)
        for lay, p in self.pills.items():
            p.set_on(lay == self.layout)
        self.p_shift.set_on(self.shift)
        self.p_alt.set_on(self.altgr)
        self.p_eng.lbl.set_text("keys: " + self.engraving.upper())

    def follow_system(self):
        lay = system_layout()
        if lay and lay != self.layout:
            self.set_layout(lay, persist=False)

    def choose(self, lay):
        """Pill click: switch the real keyboard, and show it right away."""
        self.set_layout(lay, persist=False)
        try:
            switch_system_layout(lay)
        except Exception:
            pass
        return True

    # --- window ------------------------------------------------------------
    def place(self):
        GLib.timeout_add(600, self.mark_placed)
        if "x" in self.cfg and "y" in self.cfg:
            self.move(self.cfg["x"], self.cfg["y"])
            return False
        display = Gdk.Display.get_default()
        mon = display.get_primary_monitor() or display.get_monitor(0)
        wa = mon.get_workarea()
        w, h = self.get_size()
        self.move(wa.x + wa.width - w - 12, wa.y + wa.height - h - 12)
        return False

    def mark_placed(self):
        self.placed = True
        return False

    def on_configure(self, _w, ev):
        if not self.placed:
            return
        self.cfg["x"], self.cfg["y"] = ev.x, ev.y
        GLib.timeout_add(800, self.persist)

    def persist(self):
        save_config(self.cfg)
        return False

    def on_press(self, _w, ev):
        if ev.button == 3:
            return self.flip()
        self.begin_move_drag(ev.button, int(ev.x_root), int(ev.y_root), ev.time)
        return True

    def on_key(self, _w, ev):
        pressed = ev.type == Gdk.EventType.KEY_PRESS
        if ev.keyval in (Gdk.KEY_Shift_L, Gdk.KEY_Shift_R):
            self.shift = pressed
        elif ev.keyval in (Gdk.KEY_ISO_Level3_Shift, Gdk.KEY_Alt_R):
            self.altgr = pressed
        elif pressed and ev.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        elif pressed and ev.keyval == Gdk.KEY_space:
            return self.flip()
        self.refresh()
        return False


def _shot(win, path):
    gw = win.get_window()
    w, h = win.get_size()
    pb = Gdk.pixbuf_get_from_window(gw, 0, 0, w, h)
    if pb:
        pb.savev(path, "png", [], [])
        print("saved", path, w, h, flush=True)
    Gtk.main_quit()
    return False


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        print("  --switch es|tr|ru   change the system keyboard layout and exit")
        print("  --cycle             go to the next layout (es → tr → ru) and exit")
        print("  --screenshot FILE   save a picture of the bubble and exit")
        sys.exit(0)
    if "--switch" in sys.argv or "--cycle" in sys.argv:
        IBus.init()
        if "--cycle" in sys.argv:
            wait, _lay = cycle_system_layout()
        else:
            wait = switch_system_layout(sys.argv[sys.argv.index("--switch") + 1])
        loop = GLib.MainLoop()
        GLib.timeout_add(wait, loop.quit)
        loop.run()
        sys.exit(0)
    IBus.init()
    app = KeyGlance()
    if "--screenshot" in sys.argv:
        GLib.timeout_add(1500, _shot, app, sys.argv[sys.argv.index("--screenshot") + 1])
    Gtk.main()
