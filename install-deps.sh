#!/usr/bin/env bash
# Зависимости сборки на Debian/Ubuntu: XeLaTeX, русский язык, пакеты LaTeX, шрифты STIX Two, pdftoppm.
set -euo pipefail
apt-get update
apt-get install -y --no-install-recommends \
  texlive-xetex texlive-lang-cyrillic texlive-latex-recommended texlive-latex-extra \
  texlive-pictures texlive-science texlive-fonts-extra fonts-lmodern lmodern poppler-utils
