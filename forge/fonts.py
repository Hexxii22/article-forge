"""Шрифты PT Sans / PT Sans Narrow / PT Mono (ParaType, лицензия SIL OFL 1.1) из репозитория google/fonts.

STIX Two (основной текст и формулы) берётся из TeX Live (пакет texlive-fonts-extra, stix2-otf).
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl"
FILES = [
    "ptsans/PT_Sans-Web-Regular.ttf", "ptsans/PT_Sans-Web-Bold.ttf", "ptsans/PT_Sans-Web-Italic.ttf",
    "ptsans/PT_Sans-Web-BoldItalic.ttf", "ptsansnarrow/PT_Sans-Narrow-Web-Regular.ttf",
    "ptsansnarrow/PT_Sans-Narrow-Web-Bold.ttf", "ptmono/PTM55FT.ttf",
]


def missing(font_dir: Path) -> list[str]:
    return [f for f in FILES if not (Path(font_dir) / Path(f).name).is_file()]


def ensure(font_dir: Path, quiet: bool = False) -> None:
    """Скачивает недостающие файлы шрифтов в font_dir."""
    font_dir = Path(font_dir)
    font_dir.mkdir(parents=True, exist_ok=True)
    for rel in missing(font_dir):
        dst = font_dir / Path(rel).name
        if not quiet:
            print(f"шрифт: {dst.name}")
        with urllib.request.urlopen(f"{BASE_URL}/{rel}", timeout=60) as r:
            data = r.read()
        tmp = dst.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(dst)
