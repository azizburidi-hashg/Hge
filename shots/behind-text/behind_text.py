"""Text-behind-the-building edit for the building ad.

Big animated words sit in the sky, behind the building and the trees:
sky pixels are found by colour each frame, and the text layer is shown only there.

Usage:
  python behind_text.py <input.mp4> <output.mp4>              -> full clip
  python behind_text.py <input.mp4> <outdir> --stills 1.5 13.3 -> PNG stills
"""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 576, 1024, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255, 255)
YELLOW = (255, 216, 74, 255)

# Every word here is taken from the ad's own captions.
SEGMENTS = [
    # (start, end, lines, behind)  behind=False: dense trees, so the words sit in front;
    # behind=(y0, y1): behind the sky, except the small line in rows y0..y1, kept in front
    (12.20, 14.30, [("أرض", 80, WHITE, 120), ("600 متر", 140, YELLOW, 245)], False),
    (14.40, 17.60, [("واجهة 20 متر", 76, WHITE, 140), ("شارع 25 متر", 76, YELLOW, 245)], False),
    (21.60, 24.20, [("5 محلات", 120, YELLOW, 105), ("مؤجرة بالكامل", 60, WHITE, 205)], (160, 250)),
    (24.30, 26.50, [("حديقة", 120, WHITE, 100), ("عامة", 120, YELLOW, 225)], True),
    (26.60, 28.85, [("10 مواقف", 120, YELLOW, 105), ("سيارات", 70, WHITE, 205)], (160, 250)),
]
FADE_IN, FADE_OUT = 0.35, 0.25


def render_layer(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, size, colour, yc in lines:
        while True:  # shrink until the line fits the frame
            f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
            box = d.textbbox((0, 0), text, font=f, direction="rtl", stroke_width=max(2, size // 30))
            if box[2] - box[0] <= W - 50:
                break
            size -= 4
        tw, th = box[2] - box[0], box[3] - box[1]
        x, y = (W - tw) // 2 - box[0], yc - th // 2 - box[1]
        d.text((x, y), text, font=f, fill=colour, direction="rtl",
               stroke_width=max(2, size // 30), stroke_fill=(20, 20, 20, 170))
    # soft shadow under the letters so they read on a pale sky
    a = np.array(img)[..., 3]
    sh = Image.fromarray((a * 0.45).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
    shadow = Image.new("RGBA", (W, H), (10, 20, 40, 0))
    shadow.putalpha(sh)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, 6))
    out.alpha_composite(img)
    return out


LAYERS = [render_layer(seg[2]) for seg in SEGMENTS]


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def text_at(t):
    for (s, e, _, behind), layer in zip(SEGMENTS, LAYERS):
        if s <= t <= e:
            p_in = ease_out((t - s) / FADE_IN)
            p_out = min(max((e - t) / FADE_OUT, 0.0), 1.0)
            scale = 0.82 + 0.18 * p_in + 0.04 * ((t - s) / (e - s))  # pop in, then slow push
            alpha = p_in * p_out
            rise = (1 - p_in) * 40
            sw, shh = int(W * scale), int(H * scale)
            L = layer.resize((sw, shh), Image.BICUBIC)
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            canvas.alpha_composite(L, ((W - sw) // 2, int((H - shh) * 0.3 + rise)))
            arr = np.asarray(canvas).astype(np.float32) / 255.0
            arr[..., 3] *= alpha
            return arr, behind
    return None


def sky_mask(rgb):
    f = rgb.astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    blue = (b - r >= 14) & (b > 140) & (b >= g - 6)
    hazy = (r > 185) & (g > 190) & (b > 200) & (b >= r + 2)  # pale sky near the sun
    m = blue | hazy
    m[int(H * 0.45):] = False  # sky never sits in the lower part of these shots
    img = Image.fromarray((m * 255).astype(np.uint8))
    img = img.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return np.asarray(img).astype(np.float32) / 255.0


def composite(rgb, t):
    got = text_at(t)
    if got is None:
        return rgb
    layer, behind = got
    if behind is False:
        a = layer[..., 3]
    else:
        m = sky_mask(rgb)
        if isinstance(behind, tuple):
            m = m.copy()
            m[behind[0]:behind[1]] = 1.0
        a = layer[..., 3] * m
    out = rgb.astype(np.float32) * (1 - a[..., None]) + layer[..., :3] * 255 * a[..., None]
    return out.clip(0, 255).astype(np.uint8)


def read_frames(src, start=0.0, count=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", src]
    if count:
        cmd += ["-frames:v", str(count)]
    cmd += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()


def main():
    src, dst = sys.argv[1], sys.argv[2]
    if "--stills" in sys.argv:
        os.makedirs(dst, exist_ok=True)
        for ts in sys.argv[sys.argv.index("--stills") + 1:]:
            t = float(ts)
            fr = next(read_frames(src, t, 1))
            Image.fromarray(composite(fr, t)).save(os.path.join(dst, f"behind-text-still-{int(t*1000):05d}.png"))
        return
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest",
         "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    for i, fr in enumerate(read_frames(src)):
        enc.stdin.write(composite(fr, i / FPS).tobytes())
    enc.stdin.close()
    enc.wait()


if __name__ == "__main__":
    main()
