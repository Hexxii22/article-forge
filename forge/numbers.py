"""Числа для текста: макросы \\N<Key> в numbers.tex — в тексте статьи нет чисел, набранных вручную."""

from __future__ import annotations

import re
from pathlib import Path

_KEY = re.compile(r"^[A-Za-z]+$")   # имя команды TeX — только буквы


def fmt(x, nd=1):
    """Число для TeX: тонкий пробел между разрядами и десятичная запятая ({,} — без лишнего отступа)."""
    return f"{x:,.{nd}f}".replace(",", "\\,").replace(".", "{,}")


def tex_escape(text: str) -> str:
    """Экранирует спецсимволы TeX в коротком тексте из данных."""
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("#", "\\#"), ("$", "\\$"),
                 ("_", "\\_"), ("{", "\\{"), ("}", "\\}")):
        text = text.replace(a, b)
    return text


def write_numbers(path, values: dict, source: str = "figures.py", comments=()) -> None:
    """Пишет \\newcommand{\\N<Key>}{<value>} для каждой пары; ключи — только латинские буквы."""
    bad = [k for k in values if not _KEY.match(k)]
    if bad:
        raise ValueError(f"имена макросов TeX — только буквы: {bad}")
    lines = [f"% Сгенерировано {source} — не править вручную."]
    lines += [f"\\newcommand{{\\N{k}}}{{{v}}}" for k, v in values.items()]
    lines += [f"% {c}" for c in comments]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
