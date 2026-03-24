from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


ROOT_DIR = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT_DIR / "public"

SVG_ICON = """<svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="58" y1="42" x2="448" y2="470" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0F2E5F" />
      <stop offset="0.52" stop-color="#21478A" />
      <stop offset="1" stop-color="#2B89D9" />
    </linearGradient>
    <radialGradient id="halo" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(402 108) rotate(130) scale(190 190)">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.24" />
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0" />
    </radialGradient>
    <linearGradient id="panel" x1="132" y1="126" x2="380" y2="400" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" />
      <stop offset="1" stop-color="#F4F9FF" />
    </linearGradient>
    <linearGradient id="badge" x1="316" y1="292" x2="406" y2="386" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#12376C" />
      <stop offset="1" stop-color="#2459A5" />
    </linearGradient>
  </defs>

  <rect x="24" y="24" width="464" height="464" rx="112" fill="url(#bg)" />
  <circle cx="398" cy="110" r="132" fill="url(#halo)" />

  <path d="M132 136H380" stroke="white" stroke-opacity="0.08" stroke-width="2" />
  <path d="M132 192H380" stroke="white" stroke-opacity="0.08" stroke-width="2" />
  <path d="M132 248H380" stroke="white" stroke-opacity="0.08" stroke-width="2" />
  <path d="M132 304H380" stroke="white" stroke-opacity="0.08" stroke-width="2" />
  <path d="M132 360H380" stroke="white" stroke-opacity="0.08" stroke-width="2" />

  <rect x="98" y="112" width="316" height="290" rx="56" fill="url(#panel)" />
  <path d="M154 112H358C388.928 112 414 137.072 414 168V186H98V168C98 137.072 123.072 112 154 112Z" fill="#EAF2FC" />

  <circle cx="148" cy="149" r="10" fill="#21478A" fill-opacity="0.22" />
  <circle cx="180" cy="149" r="10" fill="#2B89D9" fill-opacity="0.32" />
  <circle cx="212" cy="149" r="10" fill="#21478A" fill-opacity="0.14" />

  <path d="M186 278L146 238L186 198" stroke="#21478A" stroke-width="26" stroke-linecap="round" stroke-linejoin="round" />
  <path d="M236 306L280 170" stroke="#2B89D9" stroke-width="24" stroke-linecap="round" />
  <path d="M300 308H360" stroke="#21478A" stroke-width="24" stroke-linecap="round" />

  <rect x="146" y="340" width="122" height="18" rx="9" fill="#D8E6F5" />
  <rect x="146" y="372" width="184" height="18" rx="9" fill="#EAF2FC" />

  <circle cx="360" cy="346" r="48" fill="url(#badge)" />
  <path d="M348 323L382 346L348 369V323Z" fill="white" />
</svg>
"""

PNG_TARGETS = {
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "favicon-48.png": 48,
    "favicon.png": 32,
    "apple-touch-icon.png": 180,
    "icon-192.png": 192,
    "icon-512.png": 512,
    "app-icon-128.png": 128,
    "app-icon.png": 256,
}

ICO_TARGETS = {
    "favicon.ico": 64,
    "app-icon.ico": 256,
}


def main() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    _app = QGuiApplication.instance() or QGuiApplication([])

    svg_path = PUBLIC_DIR / "app-icon.svg"
    svg_path.write_text(SVG_ICON, encoding="utf-8")
    (PUBLIC_DIR / "favicon.svg").write_text(SVG_ICON, encoding="utf-8")

    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        raise RuntimeError("Falha ao carregar o SVG base dos icones.")

    for nome_arquivo, tamanho in PNG_TARGETS.items():
        _renderizar_arquivo(renderer, PUBLIC_DIR / nome_arquivo, tamanho, "PNG")

    for nome_arquivo, tamanho in ICO_TARGETS.items():
        _renderizar_arquivo(renderer, PUBLIC_DIR / nome_arquivo, tamanho, "ICO")

    manifest = {
        "name": "Painel de Automacao RPA - Rodogarcia",
        "short_name": "RPA Rodogarcia",
        "theme_color": "#21478A",
        "background_color": "#F3F7FB",
        "display": "standalone",
        "icons": [
            {
                "src": "/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": "/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }
    (PUBLIC_DIR / "site.webmanifest").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("Icones gerados em:", PUBLIC_DIR)


def _renderizar_arquivo(
    renderer: QSvgRenderer,
    caminho_saida: Path,
    tamanho: int,
    formato: str,
) -> None:
    imagem = QImage(tamanho, tamanho, QImage.Format_ARGB32)
    imagem.fill(Qt.transparent)

    painter = QPainter(imagem)
    painter.setRenderHint(QPainter.Antialiasing, on=True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, on=True)
    painter.setRenderHint(QPainter.TextAntialiasing, on=True)
    renderer.render(painter, QRectF(0, 0, tamanho, tamanho))
    painter.end()

    if not imagem.save(str(caminho_saida), formato):
        raise RuntimeError(f"Falha ao salvar o arquivo {caminho_saida.name}.")


if __name__ == "__main__":
    main()
