# moon prism radio 🌙✨

A tiny always-on-top desktop widget that plays YouTube and SoundCloud links.

## Setup (Windows)

1. Install Node.js (LTS) from https://nodejs.org/en/download — pick the
   Windows Installer (.msi), click through it, then CLOSE and REOPEN PowerShell.
   (Or in PowerShell: `winget install OpenJS.NodeJS.LTS`)
2. Then:

```powershell
cd moon-prism-radio
npm install
npm start
```

## Use it

- Paste any YouTube link (video, playlist, shorts, youtu.be) or SoundCloud link
  (track, playlist/set, artist page) and hit **play** or Enter.
- Drag the widget by its top bar to put it anywhere on your desktop.
- **pin** toggles always-on-top (gold = pinned).
- **x** quits.

## Double-clickable .exe (optional)

Once it runs, you can package it so you never need the terminal:

```powershell
npx electron-packager . "moon prism radio" --platform=win32 --arch=x64
```

This creates a folder containing `moon prism radio.exe`.
