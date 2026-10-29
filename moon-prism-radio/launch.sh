#!/usr/bin/env bash
# moon prism radio launcher — force X11/XWayland for reliable transparent
# frameless window, always-on-top, and drag-positioning (native Wayland
# restricts self-positioning and conflicts with Vulkan here).
DIR="/home/luckyalliecat/PycharmProjects/moon-prism-radio"
exec "$DIR/node_modules/electron/dist/electron" "$DIR" --ozone-platform=x11 "$@"
