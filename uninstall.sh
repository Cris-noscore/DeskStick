#!/usr/bin/env bash
# ============================================================
#  Sticky Desktop — Desinstalador
#  Execute com: bash uninstall.sh
# ============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}"
echo "  📌 Sticky Desktop — Desinstalador"
echo -e "${NC}"

pkill -f "sticky-desktop" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true

rm -rf "$HOME/.local/share/sticky-desktop"
rm -f  "$HOME/.local/bin/sticky-desktop"
rm -f  "$HOME/.local/share/applications/sticky-desktop.desktop"
rm -f  "$HOME/.config/autostart/sticky-desktop.desktop"
rm -f  /tmp/sticky-desktop.log

# Remove atalho do GNOME
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "[]" 2>/dev/null || true

command -v update-desktop-database &>/dev/null && \
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo -e "${GREEN}✅ Sticky Desktop removido com sucesso!${NC}"
