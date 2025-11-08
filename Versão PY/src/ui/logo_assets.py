# -*- coding: utf-8 -*-
"""
Utilitários para carregar logos DAC na aplicação Tkinter.
Mantém proporções consistentes e fornece caminhos centralizados.
"""

from pathlib import Path
from PIL import Image, ImageTk

BASE_DIR = Path(__file__).resolve().parents[2]
PY_RES = BASE_DIR / "recursos" / "imagens" / "logos"

LOGOS = {
    "color": PY_RES / "dac-color.png",
    "mono_white": PY_RES / "dac-mono-white.png",
    "mono_black": PY_RES / "dac-mono-black.png",
    "simplified": PY_RES / "dac-simplified.png",
}

def load_logo_tk(name: str, size: int = 64):
    """
    Retorna um ImageTk.PhotoImage redimensionado mantendo proporção.
    name: uma das chaves de LOGOS
    size: dimensão máxima desejada (quadrado)
    """
    path = LOGOS.get(name, LOGOS["simplified"])  # fallback
    if not path.exists():
        raise FileNotFoundError(f"Logo não encontrada: {path}")

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    scale = float(size) / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    return ImageTk.PhotoImage(img)