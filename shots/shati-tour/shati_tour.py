"""Al-Shati neighbourhood tour: "AI-style" edit of the user's two clips.

Effects: intro punch, punch-in zooms on key words, whip-zoom transitions with flash,
big words in the sky behind the tower / trees / lamp posts, glass cards for the
services, word-by-word Arabic captions, synthesized whoosh / pop / boom sounds,
light colour grade, the Samat Alsakan end card from the user's earlier ad.

Usage:
  python shati_tour.py A.mov B.mov endcard_ad.mp4 drone.mp4 out.mp4
  python shati_tour.py A.mov B.mov endcard_ad.mp4 drone.mp4 <outdir> --stills 1.0 3.5 ...
Every caption word is from the user's own voice (speech-to-text, checked by hand).
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 48000
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE, YELLOW, INK = (255, 255, 255), (255, 214, 64), (18, 18, 22)
GRADE = "eq=contrast=1.07:saturation=1.18:gamma=0.98,vignette=angle=PI/5"

SRC = {}
# clip, source start, duration, speed, kind
SEGS = [
    ("A", 0.00, 8.30, 1, "talk"),
    ("A", 8.30, 2.10, 1, "drive"),
    ("B", 0.00, 3.30, 1, "drive"),
    ("B", 3.30, 2.00, 3, "drive"),   # silent stretch, sped up 3x
    ("B", 5.30, 7.30, 1, "talk"),
    ("B", 12.60, 4.00, 1, "pan"),
    ("D", 0.00, 3.00, 1, "drone"),   # Higgsfield (Kling 4.0 Flash) drone reveal from the pan's last frame
    ("E", 34.00, 3.50, 1, "end"),    # Samat Alsakan card from the earlier ad
]
NF = [round(d * FPS / sp) for _, _, d, sp, _ in SEGS]
OUT0 = np.concatenate([[0], np.cumsum(NF)]) / FPS
TOTAL = int(sum(NF))
FACE = {"A": (500, 1120), "B": (508, 810)}


def O(clip, t):
    """source time in a clip -> output time"""
    for i, (c, s, d, sp, _) in enumerate(SEGS):
        if c == clip and s - 1e-6 <= t <= s + d + 1e-6:
            return OUT0[i] + (t - s) / sp
    raise ValueError((clip, t))


def seg_at(t):
    i = min(int(np.searchsorted(OUT0, t, side="right")) - 1, len(SEGS) - 1)
    c, s, d, sp, k = SEGS[i]
    return i, c, s + (t - OUT0[i]) * sp, k


BOUNDS = [(OUT0[1], "whip", 0.6), (OUT0[2], "whip", 0.35), (OUT0[4], "whip", 0.7),
          (OUT0[5], "whip", 0.6), (OUT0[7], "flash", 0.95)]

# ---------------- captions (word, start, end) in source time ----------------
CAPS = [
    ("A", [("احنا", 0.00, 0.50), ("اليوم", 0.50, 0.98), ("في", 0.98, 1.18)]),
    ("A", [("وسط", 1.18, 1.60), ("حي", 1.60, 1.86), ("الشاطئ", 1.86, 2.42)]),
    ("A", [("وتحديداً", 2.42, 3.04), ("ممشى", 3.04, 3.46), ("الأمير", 3.46, 3.80)]),
    ("A", [("حبينا", 4.72, 5.68), ("نعطيكم", 5.68, 6.12)]),
    ("A", [("تغطية", 6.12, 6.60), ("أكثر", 6.60, 6.88), ("لحي", 6.88, 7.18), ("الشاطئ", 7.18, 7.64)]),
    ("A", [("ومعروف", 7.64, 8.27)]),
    ("B", [("وحي", 5.60, 6.04), ("الشاطئ", 6.04, 6.66)]),
    ("B", [("مليان", 6.66, 7.14), ("خدمات", 7.14, 7.72)]),
    ("B", [("مساجد", 7.72, 8.88), ("ومدارس", 8.88, 9.90)]),
    ("B", [("ومطاعم", 9.90, 10.50), ("ومقاهي", 10.50, 11.12)]),
    ("B", [("وغير", 11.12, 11.40), ("كده", 11.40, 11.68)]),
    ("B", [("الفيو", 11.68, 11.92), ("ما", 11.92, 12.08), ("شاء", 12.08, 12.30), ("الله", 12.30, 12.55)]),
]
CAP_CHUNKS = []
for i, (clip, words) in enumerate(CAPS):
    ws = [(w, O(clip, a), O(clip, b)) for w, a, b in words]
    end = ws[-1][2] + 0.35
    j = seg_at(ws[-1][2] - 1e-3)[0]
    end = min(end, OUT0[j + 1])  # a caption never runs into the next shot
    if i + 1 < len(CAPS):
        nc, nw = CAPS[i + 1]
        end = min(end, O(nc, nw[0][1]))
    CAP_CHUNKS.append((ws, ws[0][1], end))

# ---------------- big words in the sky, behind the scene ----------------
SKY = [  # (from, to, lines[(text, size, colour, y_center[, x_center])])
    (O("A", 1.60), O("A", 4.72), [("حي", 100, YELLOW, 690, 760), ("الشاطئ", 200, WHITE, 865, 730)]),
    (O("A", 8.36), O("A", 9.28), [("ومعروف", 190, WHITE, 860)]),
    (O("A", 9.28), O("B", 0.50), [("حي", 100, YELLOW, 690), ("الشاطئ", 210, WHITE, 862)]),
    (O("B", 0.50), O("B", 1.90), [("مسطحات", 160, WHITE, 690), ("الخضرة", 180, YELLOW, 865)]),
    (O("B", 1.90), O("B", 3.30), [("حي", 100, YELLOW, 690), ("الفخامة", 200, WHITE, 865)]),
    (O("B", 14.30), O("D", 1.00), [("حي", 100, YELLOW, 450, 470), ("الشاطئ", 220, WHITE, 625, 470)]),
]

# ---------------- glass cards ----------------
CHIPS = [  # (from, to, text, cx, cy, icon, style)
    (O("A", 2.95), O("A", 4.72), "ممشى الأمير", 540, 400, "pin", "glass"),
    (O("B", 6.66), O("B", 12.50), "مليان خدمات", 540, 190, None, "solid"),
    (O("B", 7.72), O("B", 12.50), "مساجد", 775, 330, "check", "glass"),
    (O("B", 8.88), O("B", 12.50), "مدارس", 305, 330, "check", "glass"),
    (O("B", 9.90), O("B", 12.50), "مطاعم", 775, 460, "check", "glass"),
    (O("B", 10.50), O("B", 12.50), "مقاهي", 305, 460, "check", "glass"),
]

ZOOM = {"A": [(0.0, 1.0), (4.72, 1.12), (7.64, 1.0)],
        "B": [(5.30, 1.0), (6.66, 1.12), (7.72, 1.0), (9.90, 1.10), (11.68, 1.0)]}

_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
    return _fonts[size]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def text_size(d, text, f, stroke=0):
    b = d.textbbox((0, 0), text, font=f, direction="rtl", stroke_width=stroke)
    return b, b[2] - b[0], b[3] - b[1]


_probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))

# ---------------- pre-render sky text layers (cropped to their box) ----------------
def render_sky(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, size, colour, yc, *cx in lines:
        cx = cx[0] if cx else W // 2
        while True:
            f = font(size)
            box, tw, th = text_size(d, text, f, max(3, size // 28))
            if tw <= W - 90:
                break
            size -= 6
        d.text((min(max(cx - tw // 2, 25), W - 25 - tw) - box[0], yc - th // 2 - box[1]), text, font=f, fill=colour + (255,),
               direction="rtl", stroke_width=max(3, size // 28), stroke_fill=(10, 14, 30, 120))
    a = np.asarray(img)[..., 3].astype(np.float32)
    sh = Image.fromarray((a * 0.4).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (W, H), (8, 16, 40, 0))
    out.putalpha(sh)
    out = out.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -10))
    out.alpha_composite(img)
    bb = out.getbbox()
    return out.crop(bb), bb


SKY_LAYERS = [render_sky(lines) for _, _, lines in SKY]


def sky_mask(rgb, y0, y1):
    f = rgb[y0:y1].astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    blue = (b - r >= 14) & (b > 140) & (b >= g - 6) & (r > 115)
    hazy = (r > 185) & (g > 195) & (b > 205) & (b >= r + 3)
    m = Image.fromarray(((blue | hazy) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))
    return np.asarray(m).astype(np.float32) / 255.0


def apply_sky(frame, t):
    for (a, b, _), (layer, bb) in zip(SKY, SKY_LAYERS):
        if not (a <= t <= b):
            continue
        p = ease_back((t - a) / 0.32)
        sc = (0.78 + 0.22 * p) * (1 + 0.035 * (t - a) / max(b - a, 1e-3))
        alpha = clamp((t - a) / 0.18) * clamp((b - t) / 0.2)
        lw, lh = layer.size
        nw, nh = max(1, int(lw * sc)), max(1, int(lh * sc))
        L = np.asarray(layer.resize((nw, nh), Image.BILINEAR)).astype(np.float32) / 255.0
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2 + (1 - ease_out((t - a) / 0.32)) * 50
        x0, y0 = int(cx - nw / 2), int(cy - nh / 2)
        xs0, ys0, xs1, ys1 = max(x0, 0), max(y0, 0), min(x0 + nw, W), min(y0 + nh, H)
        if xs1 <= xs0 or ys1 <= ys0:
            continue
        Lc = L[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
        m = sky_mask(frame, ys0, ys1)[:, xs0:xs1]
        al = (Lc[..., 3] * m * alpha)[..., None]
        reg = frame[ys0:ys1, xs0:xs1].astype(np.float32)
        frame[ys0:ys1, xs0:xs1] = (reg * (1 - al) + Lc[..., :3] * 255 * al).astype(np.uint8)
    return frame


# ---------------- glass cards ----------------
def draw_icon(d, kind, cx, cy, r):
    if kind == "check":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW + (255,))
        d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)],
               fill=INK + (255,), width=max(4, r // 5), joint="curve")
    elif kind == "pin":
        d.polygon([(cx - r * 0.78, cy - r * 0.25), (cx + r * 0.78, cy - r * 0.25), (cx, cy + r * 1.15)], fill=YELLOW + (255,))
        d.ellipse((cx - r * 0.82, cy - r * 1.05, cx + r * 0.82, cy + r * 0.55), fill=YELLOW + (255,))
        d.ellipse((cx - r * 0.32, cy - r * 0.55, cx + r * 0.32, cy + r * 0.05), fill=INK + (255,))


def apply_chips(frame, t):
    img = None
    for a, b, text, cx, cy, icon, style in CHIPS:
        if not (a <= t <= b):
            continue
        if img is None:
            img = Image.fromarray(frame)
        f = font(50 if style == "glass" else 54)
        box, tw, th = text_size(_probe, text, f)
        ch = 104
        iw = 64 if icon else 0
        cw = tw + iw + 76
        x0, y0 = int(cx - cw / 2), int(cy - ch / 2)
        x0, y0 = clamp(x0, 10, W - cw - 10), clamp(y0, 10, H - ch - 10)
        x0, y0 = int(x0), int(y0)
        chip = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=ch // 2, fill=255)
        if style == "glass":
            bg = img.crop((x0, y0, x0 + cw, y0 + ch)).filter(ImageFilter.GaussianBlur(14))
            bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 255, 255)), 0.22)
            bg = Image.blend(bg, Image.new("RGB", bg.size, (20, 30, 50)), 0.28)
            chip.paste(bg, (0, 0), mask)
            colour = WHITE
        else:
            chip.paste(Image.new("RGB", (cw, ch), YELLOW), (0, 0), mask)
            colour = INK
        d = ImageDraw.Draw(chip)
        d.rounded_rectangle((1, 1, cw - 2, ch - 2), radius=ch // 2 - 1, outline=(255, 255, 255, 170), width=3)
        if icon:
            draw_icon(d, icon, cw - 38 - 22, ch // 2, 26)
        tx = (cw - iw - tw) // 2 - box[0] - (8 if icon else 0)
        d.text((tx, (ch - th) // 2 - box[1]), text, font=f, fill=colour + (255,), direction="rtl")
        p = ease_back((t - a) / 0.3)
        sc = 0.55 + 0.45 * p
        alpha = clamp((t - a) / 0.12) * clamp((b - t) / 0.2)
        nw, nh = max(1, int(cw * sc)), max(1, int(ch * sc))
        chip = chip.resize((nw, nh), Image.BILINEAR)
        if alpha < 1:
            chip.putalpha(chip.getchannel("A").point(lambda v: int(v * alpha)))
        img.paste(chip, (x0 + (cw - nw) // 2, y0 + (ch - nh) // 2), chip)
    return frame if img is None else np.asarray(img).copy()


# ---------------- captions ----------------
def apply_caption(frame, t):
    for ws, a, b in CAP_CHUNKS:
        if not (a <= t < b):
            continue
        size = 78
        while True:
            f = font(size)
            st = max(4, size // 14)
            dims = [text_size(_probe, w, f, st) for w, _, _ in ws]
            gap = int(size * 0.32)
            total = sum(d[1] for d in dims) + gap * (len(ws) - 1)
            if total <= W - 160:
                break
            size -= 4
        ph, pw = int(size * 1.55), total + 70
        layer = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=ph // 2, fill=(0, 0, 0, 150))
        xr = pw - 35
        for (w, ws_, we), (box, tw, th) in zip(ws, dims):
            active = ws_ <= t < (we if we > ws_ else ws_ + 0.2)
            colour = YELLOW if active or (t >= ws[-1][2] and w == ws[-1][0]) else WHITE
            spoken = t >= ws_
            fill = colour + ((255,) if spoken else (150,))
            d.text((xr - tw - box[0], (ph - th) // 2 - box[1]), w, font=f, fill=fill, direction="rtl",
                   stroke_width=st, stroke_fill=(0, 0, 0, 230 if spoken else 120))
            xr -= tw + gap
        p = ease_back((t - a) / 0.18)
        sc = 0.8 + 0.2 * p
        nw, nh = int(pw * sc), int(ph * sc)
        layer = layer.resize((nw, nh), Image.BILINEAR)
        img = Image.fromarray(frame)
        img.paste(layer, ((W - nw) // 2, 1590 - nh // 2), layer)
        return np.asarray(img).copy()
    return frame


# ---------------- camera moves ----------------
def base_zoom(i, clip, st, kind):
    c, s, d, sp, _ = SEGS[i]
    frac = clamp((st - s) / d)
    if kind == "talk":
        z, prev, k0 = 1.0, 1.0, -1.0
        for kt, kz in ZOOM[clip]:
            if st >= kt:
                prev, z, k0 = z, kz, kt
        if st - k0 < 0.12:
            z = prev + (z - prev) * ease_out((st - k0) / 0.12)
        return z, FACE[clip]
    if kind == "drone":
        return 1.0, (540, 960)
    if kind in ("drive", "pan"):
        return 1.0 + 0.07 * frac, (540, 900)
    return 1.0 + 0.04 * frac, (540, 960)


def zoomed(img, s, fx, fy):
    if s <= 1.0005:
        return img
    cw, ch = W / s, H / s
    x0 = clamp(fx - cw / 2, 0, W - cw)
    y0 = clamp(fy - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def render(frame, t):
    i, clip, st, kind = seg_at(t)
    s, (fx, fy) = base_zoom(i, clip, st, kind)
    if t < 0.4:
        s *= 1 + 0.28 * (1 - ease_out(t / 0.4))
    flash, blur = 0.0, 0.0
    if t < 0.12:
        flash = 0.8 * (1 - t / 0.12)
    for tb, style, strength in BOUNDS:
        k = 1 - abs(t - tb) / 0.16
        if k > 0:
            if style == "whip":
                s *= 1 + 0.24 * k * k
                blur = max(blur, k)
            flash = max(flash, strength * k ** 2.2)
    img = Image.fromarray(frame)
    out = zoomed(img, s, fx, fy)
    if blur > 0.05:
        a = np.asarray(out).astype(np.float32)
        for extra in (1.04, 1.08):
            a += np.asarray(zoomed(img, s * (1 + (extra - 1) * blur), fx, fy)).astype(np.float32)
        out = Image.fromarray((a / 3).astype(np.uint8))
    fr = np.asarray(out).copy()
    if kind != "end":
        fr = apply_sky(fr, t)
        fr = apply_chips(fr, t)
        fr = apply_caption(fr, t)
    if flash > 0.01:
        fr = (fr.astype(np.float32) * (1 - flash) + 255 * flash).astype(np.uint8)
    return fr


# ---------------- decoding ----------------
def decode(clip, start, dur, speed, n, kind):
    vf = (GRADE + "," if kind != "end" else "") + f"scale={W}:{H}:flags=lanczos,setpts=PTS/{speed},fps={FPS}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur + 0.2:.3f}", "-i", SRC[clip],
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size, last, got = W * H * 3, None, 0
    while got < n:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        got += 1
        yield last
    p.stdout.close()
    p.wait()
    while got < n:
        got += 1
        yield last


# ---------------- sound ----------------
def load_audio(clip, start, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", SRC[clip],
                          "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(round(dur * SR))
    if len(a) < n:
        a = np.vstack([a, np.zeros((n - len(a), 2), np.float32)])
    a = a[:n]
    f = min(len(a), int(0.01 * SR))
    ramp = np.linspace(0, 1, f)[:, None]
    a[:f] *= ramp
    a[-f:] *= ramp[::-1]
    return a


def whoosh(dur=0.5, seed=1):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n)
    cut = 300 + 5200 * np.sin(np.pi * t) ** 2
    y = np.zeros(n, np.float32)
    acc = 0.0
    for i in range(n):
        al = 1 - math.exp(-2 * math.pi * cut[i] / SR)
        acc += al * (x[i] - acc)
        y[i] = acc
    env = np.sin(np.pi * t) ** 1.5
    y = y * env / (np.abs(y).max() + 1e-9)
    pan = 0.5 + 0.4 * np.sin(np.pi * (t - 0.5))
    return np.stack([y * (1 - pan) * 1.4, y * pan * 1.4], 1)


def boom(dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 42 + 50 * np.exp(-t * 9)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    y[: int(0.006 * SR)] += np.random.default_rng(3).standard_normal(int(0.006 * SR)) * 0.4
    return np.stack([y, y], 1).astype(np.float32)


def pop(freq=1150):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 55)
    return np.stack([y, y], 1).astype(np.float32)


def build_audio(path):
    parts = []
    for (clip, s, d, sp, kind), n in zip(SEGS, NF):
        dur = n / FPS
        parts.append(np.zeros((int(round(dur * SR)), 2), np.float32) if kind in ("end", "drone")
                     else load_audio(clip, s, dur))  # sped-up stretch: keep its quiet road sound
    mix = np.vstack(parts)
    total = int(round(TOTAL / FPS * SR))
    mix = np.vstack([mix, np.zeros((max(0, total - len(mix)), 2), np.float32)])[:total]

    def add(sig, at, gain):
        i = int(at * SR)
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(total, i + len(sig))
        mix[i:j] += sig[: j - i] * gain

    add(boom(), 0.0, 0.55)
    for k, (tb, style, _) in enumerate(BOUNDS):
        if style == "whip":
            add(whoosh(0.5, seed=k + 1), tb - 0.27, 0.32)
        else:
            add(whoosh(0.6, seed=9), tb - 0.33, 0.28)
            add(boom(), tb, 0.6)
    add(whoosh(1.4, seed=21), OUT0[6] - 0.1, 0.30)  # rising air as the drone lifts off
    for a, *_ in SKY:
        add(pop(700), a, 0.18)
    for a, *_ in CHIPS:
        add(pop(1200), a, 0.22)
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


def main():
    SRC["A"], SRC["B"], SRC["E"], SRC["D"], dst = sys.argv[1:6]
    if "--stills" in sys.argv:
        os.makedirs(dst, exist_ok=True)
        for ts in sys.argv[sys.argv.index("--stills") + 1:]:
            t = float(ts)
            i, clip, st, kind = seg_at(t)
            fr = next(decode(clip, st, 0.1, 1, 1, kind))
            name = f"shati-tour-still-{int(round(t * 100)):04d}.png"
            Image.fromarray(render(fr.copy(), t)).save(os.path.join(dst, name))
        return
    wav = os.path.splitext(dst)[0] + "-audio.wav"
    build_audio(wav)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
         "-ar", str(SR), "-shortest", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    k = 0
    for (clip, s, d, sp, kind), n in zip(SEGS, NF):
        for fr in decode(clip, s, d, sp, n, kind):
            enc.stdin.write(render(fr.copy(), k / FPS).tobytes())
            k += 1
            if k % 90 == 0:
                print(f"{k}/{TOTAL} frames", flush=True)
    enc.stdin.close()
    enc.wait()
    os.remove(wav)
    print("done", dst)


if __name__ == "__main__":
    main()
