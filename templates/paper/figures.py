"""Рисунки и числа статьи из data/results.json.

Правило: каждое число в тексте — макрос \\N<Key> из numbers.tex, который пишет этот скрипт.
Запуск: python -m forge build <каталог статьи> (или напрямую: python figures.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # корень article-forge — пакет forge

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from forge import style  # noqa: E402
from forge.numbers import fmt, write_numbers  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "data" / "results.json").read_text(encoding="utf-8"))
FIG = HERE / "figures"
style.apply()


def fig_speed():
    runs = DATA["runs"]
    fig, ax = plt.subplots(figsize=(style.COL_W, 1.35))
    for i, r in enumerate(runs):
        med = float(np.median(r["ms"]))
        style.rounded_hbar(ax, i, 0, med, 0.56, style.S1)
        ax.text(med + 0.8, i, f"{style.ru(med, 1)} мс", va="center", fontsize=6.6, color=style.INK)
    ax.set_yticks(range(len(runs)), [r["variant"] for r in runs])
    ax.invert_yaxis()
    ax.set_xlim(0, max(max(r["ms"]) for r in runs) * 1.2)
    ax.set_xlabel("время, мс (медиана)")
    ax.spines["left"].set_visible(False)
    style.axis_grid(ax, "x")
    style.save(fig, FIG / "fig_speed.pdf")


def numbers():
    med = {r["variant"]: float(np.median(r["ms"])) for r in DATA["runs"]}
    base, best = med["базовый"], min(med.values())
    write_numbers(HERE / "numbers.tex", {
        "Runs": sum(len(r["ms"]) for r in DATA["runs"]),
        "BaseMs": fmt(base, 1),
        "BestMs": fmt(best, 1),
        "Speedup": fmt(base / best, 1),
    })


if __name__ == "__main__":
    fig_speed()
    numbers()
