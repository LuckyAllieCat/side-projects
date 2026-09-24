#!/usr/bin/env bash
# Point remaining launchers at Pastel-Retro icon names. Never deletes; backs up user-owned files first.
A=~/.local/share/applications; T=~/.local/share/icons/Pastel-Retro; B=$T/desktop-backup
mkdir -p "$B"
# user-owned launchers: back up, then edit the Icon= line in place
for pair in critterbox:critterbox angolino:angolino mappina:mappina quadernino:quadernino scacchino:scacchino \
            tavlacik:tavlacik pokepal:pokepal markdown-studio:markdown-studio; do
  id=${pair%%:*}; icon=${pair##*:}
  [ -e "$T/256x256/apps/$icon.png" ] || continue
  [ -e "$B/$id.desktop" ] || cp "$A/$id.desktop" "$B/"
  sed -i "s|^Icon=.*|Icon=$icon|" "$A/$id.desktop"
done
# system/snap launchers with hard-coded icon paths: user-level copies with the Icon= line changed
V=/var/lib/snapd/desktop/applications; U=/usr/share/applications
for spec in "$V/snap-store_snap-store:snap-store" "$V/discord_discord:discord" "$V/proton-mail_proton-mail:proton-mail" \
            "$V/slack_slack:slack" "$V/whatsapp-linux-app_whatsapp-linux-app:whatsapp" "$U/idle:idle" "$U/idle-python3.14:idle"; do
  src=${spec%%:*}.desktop; icon=${spec##*:}
  [ -e "$T/256x256/apps/$icon.png" ] || continue
  sed "s|^Icon=.*|Icon=$icon|" "$src" > "$A/$(basename "$src")"
done
update-desktop-database "$A" 2>/dev/null
grep -H "^Icon=" "$A"/*.desktop | grep -v "Icon=/" | grep -E "critterbox|angolino|mappina|snap-store|discord|proton-mail"
