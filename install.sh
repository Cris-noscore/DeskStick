#!/usr/bin/env bash
# ============================================================
#  Sticky Desktop — Instalador para Linux + GNOME
#  Execute com: bash install.sh
# ============================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/sticky-desktop"
BIN_LINK="$HOME/.local/bin/sticky-desktop"
DESKTOP_FILE="$HOME/.local/share/applications/sticky-desktop.desktop"
AUTOSTART_FILE="$HOME/.config/autostart/sticky-desktop.desktop"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════╗"
echo "  ║   📌  Sticky Desktop Installer   ║"
echo "  ╚══════════════════════════════════╝"
echo -e "${NC}"

# ── 1. Verificar Python ─────────────────────────────────────
echo -e "${YELLOW}[1/6]${NC} Verificando Python 3..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Python3 não encontrado. Instale com: sudo apt install python3${NC}"
    exit 1
fi
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "     ✓ Python $PYVER encontrado"

# ── 2. Instalar PyQt6 ────────────────────────────────────────
echo -e "${YELLOW}[2/6]${NC} Verificando PyQt6..."
if python3 -c "import PyQt6" &>/dev/null; then
    echo -e "     ✓ PyQt6 já instalado"
else
    echo -e "     Instalando PyQt6..."
    if pip3 install PyQt6 --break-system-packages --quiet 2>/dev/null; then
        echo -e "     ✓ PyQt6 instalado via pip"
    else
        sudo apt-get install -y python3-pyqt6 2>/dev/null || {
            echo -e "${RED}Falha ao instalar PyQt6. Tente: pip3 install PyQt6${NC}"
            exit 1
        }
        echo -e "     ✓ PyQt6 instalado via apt"
    fi
fi

# ── 3. Copiar arquivos ───────────────────────────────────────
echo -e "${YELLOW}[3/6]${NC} Instalando arquivos em $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/." "$INSTALL_DIR/"
echo -e "     ✓ Arquivos copiados"

# ── 4. Criar launcher ────────────────────────────────────────
echo -e "${YELLOW}[4/6]${NC} Criando launcher..."
mkdir -p "$HOME/.local/bin"
cat > "$BIN_LINK" << LAUNCHER
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec python3 "$INSTALL_DIR/main.py" "\$@"
LAUNCHER
chmod +x "$BIN_LINK"
echo -e "     ✓ Launcher criado"

# ── 5. Autostart + menu GNOME ────────────────────────────────
echo -e "${YELLOW}[5/6]${NC} Configurando autostart e menu GNOME..."

mkdir -p "$HOME/.local/share/applications"
cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=Sticky Desktop
GenericName=Post-it para Desktop
Comment=Notas rápidas na área de trabalho
Exec=$BIN_LINK
Icon=accessories-text-editor
Terminal=false
Categories=Utility;Office;
Keywords=nota;postit;lembrete;sticky;
StartupNotify=false
DESKTOP

mkdir -p "$HOME/.config/autostart"
cat > "$AUTOSTART_FILE" << AUTOSTART
[Desktop Entry]
Version=1.0
Type=Application
Name=Sticky Desktop
Exec=$BIN_LINK
Terminal=false
StartupNotify=false
AUTOSTART

command -v update-desktop-database &>/dev/null && \
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo -e "     ✓ Autostart configurado (inicia com o sistema)"
echo -e "     ✓ Ícone registrado no menu de aplicativos"

# ── 6. Atalho global Ctrl+Y no GNOME ─────────────────────────
echo -e "${YELLOW}[6/6]${NC} Registrando atalho global Ctrl+Y..."

KEYBINDING_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/sticky/"

# Adiciona o novo atalho sem remover outros existentes
EXISTING=$(gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings 2>/dev/null || echo "@as []")
if echo "$EXISTING" | grep -q "sticky"; then
    echo -e "     ✓ Atalho já registrado"
else
    if [ "$EXISTING" = "@as []" ] || [ "$EXISTING" = "[]" ]; then
        NEW_LIST="['$KEYBINDING_PATH']"
    else
        NEW_LIST="${EXISTING%]}, '$KEYBINDING_PATH']"
    fi
    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$NEW_LIST" 2>/dev/null || true
fi

gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEYBINDING_PATH \
    name "Sticky Desktop - Nova nota" 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEYBINDING_PATH \
    command "$BIN_LINK --new" 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEYBINDING_PATH \
    binding "<Control>y" 2>/dev/null || true

echo -e "     ✓ Ctrl+Y registrado globalmente no GNOME"

# ── INICIAR O APP ─────────────────────────────────────────────
echo ""
pkill -f "sticky-desktop" 2>/dev/null || true
pkill -f "main.py" 2>/dev/null || true
sleep 1
nohup "$BIN_LINK" > /tmp/sticky-desktop.log 2>&1 &

echo -e "${GREEN}"
echo "  ══════════════════════════════════════"
echo "  ✅  Instalação concluída com sucesso!"
echo "  ══════════════════════════════════════"
echo -e "${NC}"
echo "  O app já está rodando — procure o ícone 📝 na barra."
echo "  • Ctrl+Y      → Nova nota (funciona em qualquer lugar)"
echo "  • Botão dir.  → Menu do app"
echo "  • Inicia automaticamente com o sistema"
echo ""
