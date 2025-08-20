#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rei (NGE) — CLI ASCII Portrait
Features:
  • ANSI color themes (default, neon, pastel) and --no-color
  • Nearest-neighbor ASCII scaling (--scale)
  • Lightweight shimmer animation (--animate, --fps)
  • Clean separation of palette, renderer, and art template

Note: Works best on a dark terminal with a monospace font.
"""

import sys
import time
import argparse
from typing import Dict, List

# ---------- ANSI helpers ----------
RESET = "\033[0m"

def ansi(rgb: str, is_bg: bool=False) -> str:
    """Return ANSI 24-bit color code from hex like '#88ccff'."""
    rgb = rgb.lstrip('#')
    r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
    return f"\033[{48 if is_bg else 38};2;{r};{g};{b}m"

def stylize(s: str, fg: str = None, bg: str = None) -> str:
    if fg is None and bg is None:
        return s
    parts = []
    if fg: parts.append(ansi(fg, False))
    if bg: parts.append(ansi(bg, True))
    parts.append(s)
    parts.append(RESET)
    return ''.join(parts)

# ---------- Art Template ----------
# Each character is a semantic token. We'll recolor by palette mapping.
# Tokens:
#   H = hair (blue), h = hair shadow
#   S = skin
#   E = eye white, r = eye red/pupil
#   P = plugsuit base (white), p = plugsuit shadow/grey
#   O = orange accents
#   L = line/outline (dark)
#   . = soft shading / background dots
#   ' ' = background
#
ART = [
"                    LLLLLLLLLLL                 ",
"               LLLLHHHHHHHHHHHHHLL              ",
"            LLHHHHHHHHHHHHHHHHHHHHLL            ",
"          LHHHHHHHHhhhhhhHHHHHHHHHHHLL          ",
"        LHHHHHHHhhhhhhhhhhhHHHHHHHHHHHLL        ",
"       LHHHHHHhhhhhhhhhhhhhhHHHHHHHHHHHLL       ",
"      LHHHHHHhhhhhhhhhhhhhLLLHHHHHHHHHHHLL      ",
"     LHHHHHHhhhhhhHHHHHHHHLLLLLHHHHHHHHHHL      ",
"     LHHHHHhhhhhhHSSSSSSSHLLLLLHHHHHHHHHHLL     ",
"    LHHHHHhhhhhhHSSSEESSSHLLLLHHHHHHHHHHHLL     ",
"    LHHHHHhhhhhHSSSErrESSHLLLHHHHHHHHHHHHLL     ",
"    LHHHHHhhhhhHSSSSEESSShLLLHHHHHHHHHHHHLL     ",
"    LHHHHHHhhhhHSSSSSSSSShLLLHHHHHHHHHHHHLL     ",
"     LHHHHHHhhhHSSSSSSSSShLLLHHHHHHHHHHHLL      ",
"      LLHHHHHhhHSSSSSSSSShLLLHHHHHHHHHHLL       ",
"        LLHHHHhhHSSSSSSSSpLLLHHHHHHHHLL         ",
"          LLLHHhhPPOPPPPPpLLLHHHHHLL            ",
"             LLLLPPPPPPPPPpLLLHL                ",
"               LLPPPPpppPPpLLLL                 ",
"              LLPPOOOpppPPpLLLL                 ",
"             LLPPOOOOOPPPPPpLLL                 ",
"             LLPPOOOPPPPPPPpLLL                 ",
"             LLLPPPpppppppppLLL                 ",
"           LLLLLLLLppLLLLLLLLLLL                ",
"         LLLLLLLLLLLLLLLLLLLLLLLL               ",
"        LLLLLLLLLLLLLLLLLLLLLLLLLL              ",
"         LLLLLLLLLLLLLLLLLLLLLLLL               ",
]

# ---------- Palettes ----------
PALETTES = {
    "default": {
        "hair":   "#72a6ff",   # light blue
        "hair2":  "#3b68bf",   # deep blue shadow
        "skin":   "#ffd8bf",
        "eye":    "#f0f6ff",
        "pupil":  "#e63946",   # red
        "suit":   "#f7f7fb",   # white-ish
        "suit2":  "#c8cbd3",   # grey
        "orange": "#ff9a3c",
        "line":   "#1b1b1f",
        "dot":    "#5a5a66",
        "bg":     None
    },
    "neon": {
        "hair":   "#7ce0ff",
        "hair2":  "#3686a6",
        "skin":   "#ffe9d9",
        "eye":    "#e8ffff",
        "pupil":  "#ff1e56",
        "suit":   "#fefeff",
        "suit2":  "#aab3c2",
        "orange": "#ffb703",
        "line":   "#0b0d11",
        "dot":    "#6c6f7a",
        "bg":     None
    },
    "pastel": {
        "hair":   "#9dc4ff",
        "hair2":  "#6b8ed6",
        "skin":   "#ffe6d5",
        "eye":    "#ffffff",
        "pupil":  "#ff6b6b",
        "suit":   "#ffffff",
        "suit2":  "#d9dde6",
        "orange": "#ffb48a",
        "line":   "#2a2e33",
        "dot":    "#7a7e88",
        "bg":     None
    }
}

# Map tokens to (glyph, palette_key)
TOKEN_MAP = {
    'H': ('█', 'hair'),
    'h': ('▓', 'hair2'),
    'S': ('░', 'skin'),
    'E': ('░', 'eye'),
    'r': ('●', 'pupil'),
    'P': ('▒', 'suit'),
    'p': ('░', 'suit2'),
    'O': ('■', 'orange'),
    'L': ('█', 'line'),
    '.': ('.', 'dot'),
    ' ': (' ', None)
}

def scale_ascii(rows: List[str], k: int) -> List[str]:
    """Nearest-neighbor scale by integer factor k."""
    if k <= 1:
        return rows
    out = []
    for row in rows:
        expanded = ''.join(ch * k for ch in row)
        for _ in range(k):
            out.append(expanded)
    return out

def render(rows: List[str], palette: Dict[str, str], color: bool=True, phase: float=0.0) -> str:
    """
    Render rows to a single ANSI string. `phase` subtly modulates hair highlight
    to give a shimmer effect when animating.
    """
    # slight shimmer on hair color
    def modulate(hex_color: str, factor: float) -> str:
        # brighten by factor in [0, 0.20]
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
        f = min(max(factor, 0.0), 0.25)
        r = int(r + (255 - r) * f)
        g = int(g + (255 - g) * f)
        b = int(b + (255 - b) * f)
        return f"#{r:02x}{g:02x}{b:02x}"

    hair = palette['hair']
    hair_hi = modulate(hair, 0.10 + 0.10*abs(__import__('math').sin(phase)))
    local_palette = dict(palette)
    local_palette['hair'] = hair_hi

    out_lines = []
    for row in rows:
        line_buf = []
        for ch in row:
            glyph, key = TOKEN_MAP.get(ch, (ch, None))
            if not color or key is None:
                line_buf.append(glyph if key is not None else ch)
            else:
                fg = local_palette.get(key, None)
                line_buf.append(stylize(glyph, fg=fg))
        out_lines.append(''.join(line_buf))
    return '\n'.join(out_lines) + (RESET if color else '')

def animate(rows: List[str], palette: Dict[str,str], frames: int, fps: int, color: bool=True):
    try:
        for i in range(frames):
            phase = i * (2 * 3.14159 / max(frames,1))
            img = render(rows, palette, color=color, phase=phase)
            # Clear screen & move cursor home
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.write(img)
            sys.stdout.flush()
            time.sleep(1.0 / max(fps,1))
    except KeyboardInterrupt:
        pass
    finally:
        print(RESET)

def parse_args():
    ap = argparse.ArgumentParser(
        description="Render a CLI ASCII portrait inspired by Rei Ayanami."
    )
    ap.add_argument("--scale", "-s", type=int, default=1, help="Integer scaling factor (default: 1).")
    ap.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    ap.add_argument("--animate", "-a", type=int, default=0, help="Number of shimmer frames to animate.")
    ap.add_argument("--fps", type=int, default=10, help="Animation frames per second (default: 10).")
    ap.add_argument("--theme", choices=list(PALETTES.keys()), default="default", help="Color theme.")
    return ap.parse_args()

def main():
    args = parse_args()
    palette = PALETTES[args.theme]
    rows = scale_ascii(ART, max(1, args.scale))
    if args.animate > 0:
        animate(rows, palette, frames=args.animate, fps=args.fps, color=not args.no_color)
    else:
        print(render(rows, palette, color=not args.no_color))

if __name__ == "__main__":
    main()
