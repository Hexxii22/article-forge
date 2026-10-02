# article-forge

Инструмент для воспроизводимых технических отчётов в журнальном формате: **данные → рисунки и числа →
XeLaTeX → PDF**. Ни одно число в тексте не набирается вручную — его пишет скрипт рисунков в `numbers.tex`
в виде макроса `\N<Key>`, поэтому пересчёт данных автоматически обновляет и графики, и текст.

Пример — заготовка [`templates/paper/`](templates/paper/): `python3 -m forge new papers/demo && python3 -m forge build papers/demo`
собирает одностраничную статью с диаграммой, таблицей и числами из `data/results.json`.

## Что внутри

| Путь | Назначение |
|---|---|
| `tex/artforge.sty` | вёрстка: A4, две колонки, STIX Two + PT Sans/Mono, колонтитулы «стр. N / M», титульный блок с аннотацией и «ключевыми цифрами», блоки `keybox`/`notebox`, `\code{}` с переносами |
| `forge/style.py` | оформление matplotlib в тех же цветах: палитра (слоты проверены на контраст), `rounded_hbar`, `LabelPlacer` (подписи без наложений), `ru()` — десятичная запятая, размеры `COL_W`/`FULL_W` |
| `forge/numbers.py` | `fmt()` и `write_numbers()` → `numbers.tex` |
| `forge/build.py` | сборка: шрифты → `figures.py` → XeLaTeX ×2 → PDF; разбор ошибок из лога |
| `forge/fonts.py` | загрузка PT Sans / PT Sans Narrow / PT Mono (OFL) из `google/fonts` в `.fonts/` |
| `templates/paper/` | заготовка новой статьи (одна диаграмма, таблица, библиография) |

## Установка

```bash
sudo bash install-deps.sh          # TeX Live с XeLaTeX (Debian/Ubuntu), poppler-utils
python3 -m pip install -r requirements.txt   # Python ≥ 3.11
python3 -m forge doctor            # проверка: xelatex, пакеты TeX, шрифты STIX Two, matplotlib
```

Шрифты PT скачиваются при первой сборке (`python3 -m forge fonts` — заранее) и в git не хранятся.

## Новая статья

```bash
python3 -m forge new papers/my-report
# 1. положить результаты в papers/my-report/data/
# 2. в figures.py: рисунки (style.COL_W — в колонку, style.FULL_W — на полосу) и словарь чисел для write_numbers()
# 3. в paper.tex: \ArticleTitle, \ArticleAbstract, …, текст с \N<Key> вместо чисел
python3 -m forge build papers/my-report --strict   # --strict: ошибка при переполненных строках и битых ссылках
```

Правила, которые держит инструмент:

- **числа — только из данных**: `figures.py` пишет `numbers.tex`; ключи макросов — латинские буквы;
- **рисунки — векторные PDF** со шрифтом PT Sans (как подписи в тексте), ширина задаётся в дюймах под колонку;
- **сборка детерминирована**: те же данные дают тот же PDF;
- XeLaTeX запускается из каталога статьи; результат и логи — в `build/` (в git не попадает).

## Лицензии

Код и шаблоны — MIT (`LICENSE`). Шрифты: STIX Two — SIL OFL 1.1 (из TeX Live), PT Sans / PT Mono —
SIL OFL 1.1 (ParaType, скачиваются из `google/fonts`).
