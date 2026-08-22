# Maintainer: mike <galiciar319@gmail.com>
pkgname=classanalizer
pkgver=0.1.0
pkgrel=1
pkgdesc="Asistente de clases virtuales y generador de guías de estudio con Google Gemini"
arch=('any')
url="https://github.com/MiguelGalicia13/ClassAnalizer"
license=('MIT')
depends=('python' 'uv' 'ffmpeg' 'pipewire' 'xdg-utils')
optdepends=('libnotify: notificaciones nativas en el escritorio')
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver" 2>/dev/null || cd "$startdir"
    
    install -d "$pkgdir/opt/$pkgname"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/icons/hicolor/scalable/apps"

    cp -r bin src assets openclaw_skill pyproject.toml README.md "$pkgdir/opt/$pkgname/"
    
    # Crear enlace al binario
    ln -sf "/opt/$pkgname/bin/classanalizer" "$pkgdir/usr/bin/classanalizer"
    
    # Instalar desktop e icono
    install -m 644 assets/icon.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/classanalizer.svg"
    install -m 644 classanalizer.desktop "$pkgdir/usr/share/applications/classanalizer.desktop"
}
