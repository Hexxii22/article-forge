"""CLI: python -m forge {new,build,fonts,doctor}."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from . import fonts
from .build import BuildError, build, warnings
from .style import ROOT, font_dir

TEMPLATE = ROOT / "templates" / "paper"
TEX_PACKAGES = ["fontspec.sty", "unicode-math.sty", "polyglossia.sty", "microtype.sty", "tcolorbox.sty",
                "tikz.sty", "titlesec.sty", "fancyhdr.sty", "lastpage.sty", "xurl.sty", "balance.sty",
                "needspace.sty", "booktabs.sty", "enumitem.sty", "caption.sty", "multirow.sty",
                "STIXTwoText-Regular.otf", "STIXTwoMath-Regular.otf"]


def cmd_new(a):
    dst = Path(a.path)
    if dst.exists():
        sys.exit(f"{dst} уже существует")
    shutil.copytree(TEMPLATE, dst, ignore=shutil.ignore_patterns("build", "*.pdf", "__pycache__"))
    print(f"создано: {dst}\nдальше: python -m forge build {dst}")


def cmd_build(a):
    try:
        pdf = build(a.paper, skip_figures=a.skip_figures)
    except BuildError as e:
        sys.exit(str(e))
    warn = warnings(a.paper)
    print(f"OK: {pdf}" + (f"  (предупреждений TeX: {len(warn)}, см. build/paper.log)" if warn else ""))
    if a.strict and warn:
        print("\n".join(warn[:20]))
        sys.exit(1)


def cmd_fonts(a):
    fonts.ensure(font_dir())
    print(f"шрифты: {font_dir()}")


def cmd_doctor(a):
    ok = True
    for tool in ("xelatex", "kpsewhich"):
        found = shutil.which(tool)
        print(f"{'ok ' if found else 'НЕТ'} {tool}")
        ok &= bool(found)
    if shutil.which("kpsewhich"):
        for f in TEX_PACKAGES:
            found = subprocess.run(["kpsewhich", f], capture_output=True, text=True).stdout.strip()
            print(f"{'ok ' if found else 'НЕТ'} {f}")
            ok &= bool(found)
    for mod in ("matplotlib", "numpy"):
        try:
            __import__(mod)
            print(f"ok  python: {mod}")
        except ImportError:
            print(f"НЕТ python: {mod}")
            ok = False
    miss = fonts.missing(font_dir())
    print(f"{'ok ' if not miss else '…  '} шрифты PT ({font_dir()})" + (f": нет {len(miss)}, скачаются при сборке"
                                                                      if miss else ""))
    sys.exit(0 if ok else 1)


def main(argv=None):
    p = argparse.ArgumentParser(prog="forge", description="Сборка технических отчётов: данные → рисунки → PDF")
    sub = p.add_subparsers(required=True)
    s = sub.add_parser("new", help="новая статья из шаблона")
    s.add_argument("path")
    s.set_defaults(func=cmd_new)
    s = sub.add_parser("build", help="собрать PDF")
    s.add_argument("paper", help="каталог статьи (с paper.tex)")
    s.add_argument("--skip-figures", action="store_true", help="не запускать figures.py")
    s.add_argument("--strict", action="store_true", help="ошибка при предупреждениях TeX")
    s.set_defaults(func=cmd_build)
    s = sub.add_parser("fonts", help="скачать шрифты PT в .fonts/")
    s.set_defaults(func=cmd_fonts)
    s = sub.add_parser("doctor", help="проверить окружение")
    s.set_defaults(func=cmd_doctor)
    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
