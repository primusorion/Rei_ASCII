#!/usr/bin/env python3
import sys, argparse, time, math, shutil
from PIL import Image, ImageOps

RESET = "\033[0m"

def ansi_color(r, g, b, bg=False):
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

CHARSETS = {
    "default": "@%#*+=-:. ",
    "blocks": "█▓▒░ ",
    "dots": "@Øo:. ",
    "dense": "MWN0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!l;:,. ",
    "emoji": "✨⚡🔥💧🎵 "
}

def resize_image(img, width, height=None, fit_term=False):
    w, h = img.size
    if fit_term:
        cols, rows = shutil.get_terminal_size((80, 24))
        width = cols
        height = rows * 2
    if not height:
        aspect = h / w
        height = int(aspect * width * 0.55)
    return img.resize((width, height))

def to_ascii(img, charset, color=True, dither=True, phase=0.0):
    img = img.convert("RGB")
    if dither:
        img = img.convert("L").convert("RGB")  # pseudo-dither
    w, h = img.size
    pixels = img.load()
    ascii_str = []

    for y in range(h):
        line = []
        for x in range(w):
            r, g, b = pixels[x, y]
            # shimmer effect on blue
            if color and b > r and b > g:
                factor = 0.2 * math.sin((x+y)/6.0 + phase)
                r = min(255, int(r + 60*factor))
                g = min(255, int(g + 30*factor))
                b = min(255, int(b + 80*factor))
            gray = int(0.299*r + 0.587*g + 0.114*b)
            chars = CHARSETS.get(charset, CHARSETS["default"])
            char = chars[gray * (len(chars)-1) // 255]
            if color:
                line.append(f"{ansi_color(r,g,b)}{char}{RESET}")
            else:
                line.append(char)
        ascii_str.append("".join(line))
    return "\n".join(ascii_str)

def animate(img, charset, frames=30, fps=10, color=True):
    for i in range(frames):
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(to_ascii(img, charset, color=color, phase=i*0.3))
        sys.stdout.flush()
        time.sleep(1.0/fps)

def main():
    ap = argparse.ArgumentParser(description="Enhanced Rei ASCII CLI Renderer")
    ap.add_argument("image", help="Path to image (PNG/JPG)")
    ap.add_argument("--width", type=int, default=100, help="Output width")
    ap.add_argument("--height", type=int, help="Output height")
    ap.add_argument("--fit-term", action="store_true", help="Auto-fit to terminal size")
    ap.add_argument("--charset", choices=list(CHARSETS.keys()), default="default", help="ASCII charset")
    ap.add_argument("--color", action="store_true", help="Enable ANSI colors")
    ap.add_argument("--dither", action="store_true", help="Enable dithering for smoother shading")
    ap.add_argument("--animate", type=int, default=0, help="Number of shimmer frames")
    ap.add_argument("--fps", type=int, default=10, help="Animation FPS")
    args = ap.parse_args()

    try:
        img = Image.open(args.image)
    except Exception as e:
        print("Error loading image:", e)
        return

    img = resize_image(img, args.width, args.height, args.fit_term)

    if args.animate > 0:
        animate(img, args.charset, frames=args.animate, fps=args.fps, color=args.color)
    else:
        print(to_ascii(img, args.charset, color=args.color, dither=args.dither))

if __name__ == "__main__":
    main()
