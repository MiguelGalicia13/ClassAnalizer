#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

echo "🎓 Instalando ClassAnalizer en tu sistema Arch Linux..."

# 1. Asegurar directorios locales
mkdir -p "$BIN_DIR" "$APP_DIR" "$ICON_DIR"

# 2. Enlace simbólico del ejecutable en ~/.local/bin
ln -sf "$SCRIPT_DIR/bin/classanalizer" "$BIN_DIR/classanalizer"
chmod +x "$BIN_DIR/classanalizer"
echo "  ✓ Ejecutable enlazado en: $BIN_DIR/classanalizer"

# 3. Instalar icono del sistema
cp "$SCRIPT_DIR/assets/icon.svg" "$ICON_DIR/classanalizer.svg"
echo "  ✓ Icono instalado en: $ICON_DIR/classanalizer.svg"

# 4. Instalar archivo .desktop
sed "s|Exec=classanalizer gui|Exec=$BIN_DIR/classanalizer gui|g" "$SCRIPT_DIR/classanalizer.desktop" > "$APP_DIR/classanalizer.desktop"
chmod +x "$APP_DIR/classanalizer.desktop"
echo "  ✓ Acceso directo instalado en: $APP_DIR/classanalizer.desktop"

# 5. Actualizar bases de datos de escritorio si las utilidades existen
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo ""
echo "✨ ¡Instalación completada con éxito!"
echo "   - Puedes ejecutarlo desde la terminal escribiendo: classanalizer"
echo "   - O abrirlo desde el menú de aplicaciones de tu entorno (Rofi, KDE, GNOME, etc.)."
