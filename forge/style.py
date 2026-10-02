"""Оформление рисунков matplotlib под вёрстку artforge.sty.

Палитра — по методике dataviz: категориальные слоты в фиксированном порядке (проверены валидатором
контраста на белом фоне), последовательная шкала — один синий тон, тонкие отметки, волосяные сетки,
текст — только «чернилами», не цветом серии. Цвета совпадают с \\definecolor в tex/artforge.sty.

    from forge import style
    style.apply()                      # шрифт PT Sans, rcParams
    fig, ax = plt.subplots(figsize=(style.COL_W, 2.0))
    ...
    style.save(fig, FIG / "fig_x.pdf")
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib import patheffects as pe  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASE, NEUTRAL = "#e1e0d9", "#c3c2b7", "#f0efec"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"   # слоты 1–4 (валидатор: PASS, белый фон)
SLOTS = (S1, S2, S3, S4)
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
       "#1c5cab", "#184f95", "#104281", "#0d366b"]

COL_W, FULL_W = 3.30, 6.90   # дюймы: колонка и полоса A4 при полях 17 мм и промежутке 6,5 мм

RC = {
    "font.family": "PT Sans", "font.size": 7.5, "pdf.fonttype": 42,
    "axes.edgecolor": BASE, "axes.linewidth": 0.6, "axes.labelcolor": INK2, "axes.labelsize": 7.5,
    "axes.titlesize": 7.8, "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlepad": 5,
    "axes.titlelocation": "left", "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "xtick.major.size": 0, "ytick.major.size": 0,
    "xtick.major.pad": 3, "ytick.major.pad": 3,
    "grid.color": GRID, "grid.linewidth": 0.5, "legend.fontsize": 6.8, "legend.frameon": False,
    "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "axes.spines.top": False, "axes.spines.right": False,
}


def font_dir() -> Path:
    """Каталог шрифтов: $FORGE_FONT_DIR или .fonts/ в корне репозитория."""
    return Path(os.environ.get("FORGE_FONT_DIR", ROOT / ".fonts"))


def apply(fonts: Path | None = None) -> None:
    """Регистрирует PT Sans из каталога шрифтов и задаёт rcParams."""
    for f in sorted(Path(fonts or font_dir()).glob("PT_Sans*.ttf")):
        fm.fontManager.addfont(str(f))
    plt.rcParams.update(RC)


def ru(x, nd=1):
    """Число с десятичной запятой и типографским минусом (русская типографика)."""
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def ru_axis(axis, nd=1):
    axis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ru(v, nd)))


def axis_grid(ax, axis="y"):
    ax.grid(True, axis=axis)
    ax.set_axisbelow(True)


def save(fig, path):
    """Сохраняет векторный PDF и закрывает фигуру."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def rounded_hbar(ax, y, x0, x1, h, color, r_pt=1.6):
    """Горизонтальный бар: скруглённый конец данных, прямой у базовой линии (dataviz: marks)."""
    if x1 <= x0:
        return
    fig = ax.figure
    fig.canvas.draw_idle()
    inv = ax.transData.inverted()
    p0 = inv.transform(ax.transData.transform((x0, y)))
    dx = abs(inv.transform((ax.transData.transform((x0, y))[0] + r_pt * fig.dpi / 72, 0))[0] - p0[0])
    dy = h / 2
    rx = min(dx, (x1 - x0) / 2)
    ry = dy
    k = 0.5523
    verts = [(x0, y - dy), (x1 - rx, y - dy),
             (x1 - rx + k * rx, y - dy), (x1, y - dy + ry - k * ry), (x1, y - dy + ry),
             (x1, y + dy - ry),
             (x1, y + dy - ry + k * ry), (x1 - rx + k * rx, y + dy), (x1 - rx, y + dy),
             (x0, y + dy), (x0, y - dy)]
    codes = [MPath.MOVETO, MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO,
             MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO, MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(verts, codes), facecolor=color, edgecolor="none", lw=0))


class LabelPlacer:
    """Подписи точек без наложений: перебор позиций вокруг точки, проверка по реальной рамке текста.

    Фигуре нужен холст с измерением текста: ``FigureCanvasAgg(fig)`` (сохранять можно всё равно в PDF).
    Штраф позиции = площадь за краем панели + 3 × площадь пересечения с уже поставленными подписями.
    """

    CANDIDATES = [(5, 4, "left", "bottom"), (5, -3, "left", "top"), (-5, 4, "right", "bottom"),
                  (-5, -3, "right", "top"), (0, 7, "center", "bottom"), (0, -7, "center", "top")]

    def __init__(self, fig, fontsize=5.9, color=INK, halo=2.2):
        self.fig = fig
        self.fontsize, self.color = fontsize, color
        self.halo = [pe.withStroke(linewidth=halo, foreground="white")] if halo else None
        self.placed: dict[int, list] = {}

    def place(self, ax, text, x, y, prefer_below=False):
        renderer = self.fig.canvas.get_renderer()
        panel = ax.get_window_extent(renderer)
        boxes = self.placed.setdefault(id(ax), [])
        cands = self.CANDIDATES
        if prefer_below:
            cands = [c for c in cands if c[1] < 0] + [c for c in cands if c[1] > 0]
        best, best_cost = None, None
        for dx, dy, ha, va in cands:
            ann = ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                              fontsize=self.fontsize, color=self.color, zorder=7, path_effects=self.halo,
                              annotation_clip=False)
            bb = ann.get_window_extent(renderer)
            outside = (max(0, panel.x0 - bb.x0) + max(0, bb.x1 - panel.x1)) * bb.height + \
                (max(0, panel.y0 - bb.y0) + max(0, bb.y1 - panel.y1)) * bb.width
            overlap = sum(max(0, min(bb.x1, o.x1) - max(bb.x0, o.x0)) * max(0, min(bb.y1, o.y1) - max(bb.y0, o.y0))
                          for o in boxes)
            cost = outside + 3 * overlap
            if best_cost is None or cost < best_cost:
                if best is not None:
                    best[0].remove()
                best, best_cost = (ann, bb), cost
            else:
                ann.remove()
            if cost == 0:
                break
        boxes.append(best[1])
        return best[0]
