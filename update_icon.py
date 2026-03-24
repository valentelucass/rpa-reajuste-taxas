from pathlib import Path
import shutil

from PIL import Image


ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"
ASSETS_DIR = ROOT / "assets"
ICON_NUMBER = 3
SOURCE_FILENAME = f"rpa_icon_{ICON_NUMBER}.png"
PUBLIC_SOURCE = PUBLIC_DIR / SOURCE_FILENAME
LEGACY_SOURCE = ROOT / "rpa-icons" / SOURCE_FILENAME

ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
PNG_SIZES = {
    "app-icon-128.png": 128,
    "apple-touch-icon.png": 180,
    "favicon-16.png": 16,
    "favicon-32.png": 32,
    "favicon-48.png": 48,
    "favicon.png": 32,
    "icon-192.png": 192,
    "icon-512.png": 512,
}


def _resolver_fonte() -> Path:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    if PUBLIC_SOURCE.exists():
        return PUBLIC_SOURCE

    if LEGACY_SOURCE.exists():
        return LEGACY_SOURCE

    raise FileNotFoundError(
        f"Icone fonte nao encontrado em public/{SOURCE_FILENAME} nem em rpa-icons/{SOURCE_FILENAME}."
    )


def _salvar_png_redimensionado(imagem: Image.Image, destino: Path, tamanho: int) -> None:
    imagem.resize((tamanho, tamanho), Image.Resampling.LANCZOS).save(destino, format="PNG")


def main() -> None:
    origem = _resolver_fonte()
    destino_app_png = PUBLIC_DIR / "app-icon.png"
    destino_app_ico = PUBLIC_DIR / "app-icon.ico"
    destino_favicon_ico = PUBLIC_DIR / "favicon.ico"
    destino_assets_png = ASSETS_DIR / "app_icon.png"
    destino_assets_ico = ASSETS_DIR / "app_icon.ico"

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(origem, destino_app_png)
    shutil.copyfile(origem, destino_assets_png)

    imagem = Image.open(origem).convert("RGBA")
    imagem.save(destino_app_ico, format="ICO", sizes=ICO_SIZES)
    imagem.save(destino_favicon_ico, format="ICO", sizes=ICO_SIZES)
    imagem.save(destino_assets_ico, format="ICO", sizes=ICO_SIZES)

    for nome_arquivo, tamanho in PNG_SIZES.items():
        _salvar_png_redimensionado(imagem, PUBLIC_DIR / nome_arquivo, tamanho)

    print(f"Icones atualizados com sucesso a partir de {origem}")


if __name__ == "__main__":
    main()
