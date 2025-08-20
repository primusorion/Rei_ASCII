# Rei ASCII CLI 🎨

A high-quality **image-to-ASCII art renderer** for the terminal, inspired by *Rei Ayanami (Neon Genesis Evangelion)*.  
Turn any image into detailed **color ASCII art**, complete with shading, dithering, and shimmer animations.  

---

## ✨ Features
- 🎭 Multiple ASCII palettes (`default`, `blocks`, `dots`, `dense`, `emoji`)
- 🌈 Truecolor ANSI output (blue hair, red eyes, white plugsuit will pop!)
- 📐 Smart resizing + terminal auto-fit
- 🖌️ Optional dithering for smoother gradients
- ⚡ Shimmer/scanline animation for cyberpunk vibes
- 💾 Save + share ASCII art easily

---

## 🚀 Installation

Clone the repo:
```bash
git clone https://github.com/your-username/Rei-ASCII-CLI.git
cd Rei-ASCII-CLI
```

## Install requirements:

```bash
pip install -r requirements.txt
```

## 🖥️ Usage

Basic render:
```bash
python rei_ascii.py rei.png --width 120 --color --dither
```
Fit to terminal:
```bash
python rei_ascii.py rei.png --fit-term --color --charset blocks
```
Animated shimmer (Rei goes cyberpunk ✨):
```bash
python rei_ascii.py rei.png --width 120 --color --animate 50 --fps 15 --charset dense
```

## 🔤 Options

| Flag         | Description                                                   |
| ------------ | ------------------------------------------------------------- |
| `--width`    | Output width in characters                                    |
| `--height`   | Output height in characters                                   |
| `--fit-term` | Auto-fit to terminal size                                     |
| `--charset`  | ASCII palette (`default`, `blocks`, `dots`, `dense`, `emoji`) |
| `--color`    | Enable ANSI 24-bit colors                                     |
| `--dither`   | Enable dithering for smoother shading                         |
| `--animate`  | Number of shimmer frames to render                            |
| `--fps`      | Frames per second (for animation)                             |


## 📦 Requirements
Python 3.8+
Pillow (image processing)
Install with:

```bash
pip install -r requirements.txt
```

## 📸 Example Output

![alt text](image.png)

## 🛠️ Roadmap

Add support for GIF → ASCII animation

Export to HTML with colored ASCII

Add more character sets and color themes

