#!/usr/bin/env bash
# Run each icons6 batch through codex one at a time (keeps usage spikes small).
export PATH=~/.nvm/versions/node/v22.23.2/bin:$PATH
T=$(cd "$(dirname "$0")" && pwd); R=$T/icons6-refs
for b in a b c d; do
  echo "=== batch $b $(date +%T)"
  codex exec --skip-git-repo-check -s workspace-write -C "$T/icons6$b" \
    -i "$R/0-style-sheet.png" -i "$R/critterbox.png" -i "$R/moon-prism-radio.png" -i "$R/discord.png" \
    -i "$R/terminal.png" -i "$R/folder.png" - < "$T/icons6$b/prompt.txt" > "$T/icons6$b/codex.log" 2>&1
  echo "exit $?"; ls "$T/icons6$b/out"
done
