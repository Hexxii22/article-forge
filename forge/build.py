"""Сборка статьи: шрифты → figures.py (рисунки, numbers.tex) → XeLaTeX ×2 → PDF.

Каталог статьи содержит paper.tex и, по желанию, article.toml:

    output = "my-report.pdf"     # имя итогового PDF (по умолчанию paper.pdf)
    figures = "figures.py"       # скрипт рисунков и чисел; "" — не запускать
    passes = 2                   # проходов XeLaTeX (ссылки, LastPage)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from . import fonts
from .style import ROOT, font_dir

TEX_DIR = ROOT / "tex"
DEFAULTS = {"output": "paper.pdf", "figures": "figures.py", "passes": 2}


class BuildError(RuntimeError):
    pass


def config(paper: Path) -> dict:
    cfg = dict(DEFAULTS)
    f = paper / "article.toml"
    if f.is_file():
        cfg.update(tomllib.loads(f.read_text(encoding="utf-8")))
    return cfg


def _env(fdir: Path) -> dict:
    env = dict(os.environ)
    env["FORGE_FONT_DIR"] = str(fdir)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), env.get("PYTHONPATH")]))
    # Пустой элемент в конце TEXINPUTS — «и стандартные пути TeX Live».
    env["TEXINPUTS"] = f"{TEX_DIR}//{os.pathsep}{env.get('TEXINPUTS', '')}"
    return env


def tex_errors(log: Path, limit=12) -> str:
    if not log.is_file():
        return "(нет лога)"
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    hits = [i for i, s in enumerate(lines) if s.startswith("!")]
    out = []
    for i in hits[:3]:
        out += lines[i:i + 4]
    return "\n".join(out[:limit]) or "\n".join(lines[-limit:])


def build(paper, skip_figures=False, python=None, quiet=False) -> Path:
    paper = Path(paper).resolve()
    if not (paper / "paper.tex").is_file():
        raise BuildError(f"{paper}: нет paper.tex")
    if shutil.which("xelatex") is None:
        raise BuildError("xelatex не найден — см. install-deps.sh")
    cfg = config(paper)
    fdir = font_dir().resolve()
    fonts.ensure(fdir, quiet=quiet)
    env = _env(fdir)
    out_dir = paper / "build"
    out_dir.mkdir(exist_ok=True)

    script = cfg.get("figures") or ""
    if script and not skip_figures:
        if not quiet:
            print(f"рисунки: {script}")
        with open(out_dir / "figures.log", "w", encoding="utf-8") as log:
            r = subprocess.run([python or sys.executable, script], cwd=paper, env=env, stdout=log,
                               stderr=subprocess.STDOUT)
        if r.returncode:
            raise BuildError(f"{script} упал, см. {out_dir / 'figures.log'}")

    # \forgefontdir задаётся до \documentclass; jobname фиксирован, чтобы build/paper.* не зависел от вызова.
    cmd = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-jobname=paper",
           f"-output-directory={out_dir}", f"\\def\\forgefontdir{{{fdir.as_posix()}/}}\\input{{paper.tex}}"]
    for i in range(int(cfg["passes"])):
        if not quiet:
            print(f"xelatex: проход {i + 1}")
        with open(out_dir / "xelatex.out", "w", encoding="utf-8") as log:
            r = subprocess.run(cmd, cwd=paper, env=env, stdout=log, stderr=subprocess.STDOUT)
        if r.returncode:
            raise BuildError("XeLaTeX: ошибка\n" + tex_errors(out_dir / "paper.log"))
    pdf = paper / cfg["output"]
    shutil.copyfile(out_dir / "paper.pdf", pdf)
    return pdf


def warnings(paper) -> list[str]:
    """Предупреждения последней сборки: переполненные строки, неразрешённые ссылки, шрифты."""
    log = Path(paper) / "build" / "paper.log"
    if not log.is_file():
        return []
    keys = ("Overfull", "undefined", "LaTeX Warning", "Font Warning", "Missing character")
    return [s for s in log.read_text(encoding="utf-8", errors="replace").splitlines() if any(k in s for k in keys)]
