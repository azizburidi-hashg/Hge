"""Luxury villa for sale, Al-Shati (Jeddah): listing video from the user's 14 photos + 1 street clip.

Each still photo becomes a moving "drone" shot: a free depth model (Depth Anything V2 small,
run with onnxruntime) gives every photo a depth map, and the camera dollies / slides with
real parallax (near things move more than far ones). On top: the listing's own facts as
animated glass cards and panels, words in the sky behind the roofline, a count-up for the
area and the price, beat-cut music and sound effects, Samat Alsakan end card.
Every word and number on screen is taken from the user's listing text.

Usage:
  python shati_villa.py <work_dir> <endcard_ad.mp4> out.mp4
  python shati_villa.py <work_dir> <endcard_ad.mp4> <outdir> --stills 1.0 5.0 ...
<work_dir> holds fixed/NN.jpg (upright photos), depth/NN.png (near = white) and 15.mp4.
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 48000
BPM = 100
BEAT = 60 / BPM
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE, YELLOW, INK = (255, 255, 255), (255, 214, 64), (18, 18, 22)
VGRADE = "eq=contrast=1.05:saturation=1.12,vignette=angle=PI/5"

# ---- shots (photo moves: push / left / right) ----
SHOTS = [
    dict(kind="photo", src="04", dur=6 * BEAT, move="push", cx=0.55),
    dict(kind="video", src="15", inp=0.0, dur=5 * BEAT, whip=True),
    dict(kind="video", src="15", inp=5.0, dur=6 * BEAT),
    dict(kind="photo", src="05", dur=6 * BEAT, move="push", cx=0.5, whip=True),
    dict(kind="photo", src="14", dur=5 * BEAT, move="left", whip=True),
    dict(kind="photo", src="02", dur=5 * BEAT, move="right"),
    dict(kind="photo", src="03", dur=4 * BEAT, move="push", cx=0.45),
    dict(kind="photo", src="11", dur=4 * BEAT, move="left"),
    dict(kind="photo", src="12", dur=4 * BEAT, move="right"),
    dict(kind="photo", src="13", dur=4 * BEAT, move="push", cx=0.5),
    dict(kind="photo", src="08", dur=4 * BEAT, move="push", cx=0.62, whip=True),
    dict(kind="photo", src="06", dur=4 * BEAT, move="left"),
    dict(kind="photo", src="07", dur=4 * BEAT, move="right"),
    dict(kind="photo", src="01", dur=4 * BEAT, move="push", cx=0.4),
    dict(kind="photo", src="10", dur=4 * BEAT, move="left"),
    dict(kind="video", src="15", inp=10.0, dur=7 * BEAT, whip=True),
    dict(kind="photo", src="04", dur=7 * BEAT, move="left", whip=True),
    dict(kind="end", src="END", inp=34.0, dur=6 * BEAT, flash=True),
]
for s in SHOTS:
    s["n"] = round(s["dur"] * FPS)
START = np.concatenate([[0], np.cumsum([s["n"] for s in SHOTS])]) / FPS
TOTAL = sum(s["n"] for s in SHOTS)


def S(i, off=0.0):
    return START[i] + off


# ---- overlays, all words from the listing ----
SKYTEXT = [  # (t0, t1, lines[(text, size, colour, y, x)], behind)
    (S(0, 0.25), S(1) - 0.05, [("فيلا فاخرة للبيع", 112, WHITE, 250, 540), ("جدة | حي الشاطئ", 78, YELLOW, 385, 540)], False),
    (S(2, 0.3), S(3) - 0.05, [("بجوار مسجد", 110, WHITE, 300, 540), ("وعلى حديقة", 110, YELLOW, 440, 540)], True),
]
CHIPS = [  # (t0, t1, text, cx, cy, icon, style, size)
    (S(1, 0.15), S(2) - 0.05, "موقع مميز جداً – خلف البروميناد", 540, 300, "pin", "glass", 46),
    (S(1, 0.15 + 2 * BEAT), S(2) - 0.05, "دقيقتين عن البحر و Red Sea Mall", 540, 430, "pin", "glass", 46),
]
STATS = [  # (t0, t1, value, suffix, label, cx, cy)
    (S(3, 0.2), S(4) - 0.05, 730, " م²", "المساحة", 760, 1500),
    (S(3, 0.2 + BEAT), S(4) - 0.05, 10, " سنوات", "العمر", 320, 1500),
]
PANELS = [  # (t0, t1, heading, bullets)
    (S(4, 0.2), S(10) - 0.05, "الدور الأرضي",
     ["4 صوالين مفتوحة بتصميم فاخر", "مجلس رجال بمدخلين (خارجي + داخلي)", "مطبخ رئيسي"]),
    (S(10, 0.2), S(15) - 0.05, "الدور الأول",
     ["4 غرف نوم ماستر", "~(كل غرفة بدورة مياه مستقلة)", "صالة كبيرة تقريباً (10 × 8)", "غرفة غسيل", "مطبخ خدمة"]),
    (S(15, 0.2), S(16) - 0.05, "الملحق (الروف)",
     ["3 غرف ماستر", "صالة كبيرة (تقريباً 12 × 9)", "مطبخ", "حوش خاص"]),
]
PRICE = (S(16, 0.25), S(17) - 0.05)

# ---------------- helpers ----------------
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


def ease_io(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_back(x):
    x = clamp(x)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


_probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def tsize(text, f, stroke=0):
    b = _probe.textbbox((0, 0), text, font=f, direction="rtl", stroke_width=stroke)
    return b, b[2] - b[0], b[3] - b[1]


def fit(text, size, maxw, stroke_div=0):
    while True:
        f = font(size)
        st = max(3, size // stroke_div) if stroke_div else 0
        box, tw, th = tsize(text, f, st)
        if tw <= maxw or size <= 20:
            return f, size, st, box, tw, th
        size -= 2


# ---------------- 2.5D photo camera ----------------
PHOTOS = {}


def load_photo(work, key):
    if key not in PHOTOS:
        img = np.asarray(Image.open(os.path.join(work, "fixed", key + ".jpg")).convert("RGB")).astype(np.float32)
        d = Image.open(os.path.join(work, "depth", key + ".png")).convert("L").filter(ImageFilter.GaussianBlur(3))
        dep = np.asarray(d).astype(np.float32) / 255.0
        PHOTOS[key] = (img, dep)
    return PHOTOS[key]


def bilinear(img, xs, ys):
    h, w = img.shape[:2]
    xs = np.clip(xs, 0, w - 1.001)
    ys = np.clip(ys, 0, h - 1.001)
    x0 = xs.astype(np.int32)
    y0 = ys.astype(np.int32)
    fx = (xs - x0)[..., None]
    fy = (ys - y0)[..., None]
    a = img[y0, x0]
    b = img[y0, x0 + 1]
    c = img[y0 + 1, x0]
    d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


UV = None


def photo_frame(work, s, lt):
    global UV
    img, dep = load_photo(work, s["src"])
    h, w = dep.shape
    hb = min(h, w * 16 / 9)
    frac = lt / s["dur"]
    e = ease_io(frac)
    mv = s["move"]
    if mv == "push":
        z = 1.0 + 0.16 * e
        pl, pd = 0.0, 0.10
    else:
        z = 1.06
        pl, pd = 0.035, 0.03
    hw = hb / z
    ww = hw * 9 / 16
    if mv == "push":
        cx = s.get("cx", 0.5) * w
    else:
        span = (w - ww) * 0.55
        a, b = (0.5 + span / w / 2, 0.5 - span / w / 2) if mv == "left" else (0.5 - span / w / 2, 0.5 + span / w / 2)
        cx = (a + (b - a) * e) * w
    cx = clamp(cx, ww / 2, w - ww / 2)
    cy = h / 2
    if UV is None:
        UV = np.meshgrid((np.arange(W, dtype=np.float32) + 0.5) / W - 0.5, (np.arange(H, dtype=np.float32) + 0.5) / H - 0.5)
    u, v = UV
    x0 = cx + u * ww
    y0 = cy + v * hw
    prog = e - 0.5
    xs, ys = x0, y0
    for _ in range(2):
        n = dep[np.clip(ys, 0, h - 1).astype(np.int32), np.clip(xs, 0, w - 1).astype(np.int32)] - 0.5
        k = 1 + pd * prog * n * 2
        xs = cx + (x0 - cx) / k - pl * w * prog * n * (1 if mv == "left" else -1)
        ys = cy + (y0 - cy) / k
    out = bilinear(img, xs, ys)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    return np.asarray(im).copy()


def grade(fr):
    a = fr.astype(np.float32)
    a = (a - 128) * 1.05 + 128 + 3
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 1.1
    yy, xx = np.ogrid[:H, :W]
    vig = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4 / 2
    return np.clip(a * vig[..., None], 0, 255).astype(np.uint8)


_VIG = None


def grade_fast(fr):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        _VIG = (1 - 0.14 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)).astype(np.float32)[..., None]
    a = fr.astype(np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 1.1
    a = (a - 128) * 1.05 + 131
    return np.clip(a * _VIG, 0, 255).astype(np.uint8)


# ---------------- overlays ----------------
def render_sky(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, size, colour, yc, cx in lines:
        f, size, st, box, tw, th = fit(text, size, W - 90, 28)
        d.text((min(max(cx - tw // 2, 25), W - 25 - tw) - box[0], yc - th // 2 - box[1]), text, font=f,
               fill=colour + (255,), direction="rtl", stroke_width=st, stroke_fill=(10, 14, 30, 120))
    a = np.asarray(img)[..., 3].astype(np.float32)
    sh = Image.fromarray((a * 0.4).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (W, H), (8, 16, 40, 0))
    out.putalpha(sh)
    out = out.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -10))
    out.alpha_composite(img)
    bb = out.getbbox()
    return out.crop(bb), bb


SKY = [(a, b) + render_sky(lines) + (behind,) for a, b, lines, behind in SKYTEXT]


def sky_mask(rgb, y0, y1):
    f = rgb[y0:y1].astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    blue = ((b - r >= 14) & (b > 140) & (b >= g - 6)) | ((b - r >= 22) & (b > 70) & (b >= g))
    hazy = (r > 185) & (g > 195) & (b > 205) & (b >= r + 3)
    m = Image.fromarray(((blue | hazy) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))
    return np.asarray(m).astype(np.float32) / 255.0


def apply_sky(frame, t):
    for a, b, layer, bb, behind in SKY:
        if not (a <= t <= b):
            continue
        p = ease_back((t - a) / 0.32)
        sc = (0.78 + 0.22 * p) * (1 + 0.035 * (t - a) / max(b - a, 1e-3))
        alpha = clamp((t - a) / 0.18) * clamp((b - t) / 0.25)
        lw, lh = layer.size
        nw, nh = max(1, int(lw * sc)), max(1, int(lh * sc))
        L = np.asarray(layer.resize((nw, nh), Image.BILINEAR)).astype(np.float32) / 255.0
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2 + (1 - ease_out((t - a) / 0.32)) * 50
        x0, y0 = int(cx - nw / 2), int(cy - nh / 2)
        xs0, ys0, xs1, ys1 = max(x0, 0), max(y0, 0), min(x0 + nw, W), min(y0 + nh, H)
        if xs1 <= xs0 or ys1 <= ys0:
            continue
        Lc = L[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
        m = sky_mask(frame, ys0, ys1)[:, xs0:xs1] if behind else 1.0
        al = (Lc[..., 3] * m * alpha)[..., None]
        reg = frame[ys0:ys1, xs0:xs1].astype(np.float32)
        frame[ys0:ys1, xs0:xs1] = (reg * (1 - al) + Lc[..., :3] * 255 * al).astype(np.uint8)
    return frame


def draw_icon(d, kind, cx, cy, r):
    if kind == "pin":
        d.polygon([(cx - r * 0.78, cy - r * 0.25), (cx + r * 0.78, cy - r * 0.25), (cx, cy + r * 1.15)], fill=YELLOW + (255,))
        d.ellipse((cx - r * 0.82, cy - r * 1.05, cx + r * 0.82, cy + r * 0.55), fill=YELLOW + (255,))
        d.ellipse((cx - r * 0.32, cy - r * 0.55, cx + r * 0.32, cy + r * 0.05), fill=INK + (255,))
    elif kind == "check":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW + (255,))
        d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)],
               fill=INK + (255,), width=max(3, r // 4), joint="curve")


def glass(img, box, radius, tint=0.34):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    if x1 <= x0 or y1 <= y0:
        return None
    bg = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(16))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 255, 255)), 0.16)
    bg = Image.blend(bg, Image.new("RGB", bg.size, (18, 26, 44)), tint)
    c = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    mask = Image.new("L", bg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), radius=radius, fill=255)
    c.paste(bg, (0, 0), mask)
    ImageDraw.Draw(c).rounded_rectangle((1, 1, bg.width - 2, bg.height - 2), radius=radius - 1,
                                        outline=(255, 255, 255, 160), width=3)
    return c


def paste_anim(img, layer, x, y, t, a, b, pop=True):
    p = ease_back((t - a) / 0.3) if pop else 1
    sc = 0.6 + 0.4 * p
    alpha = clamp((t - a) / 0.12) * clamp((b - t) / 0.18)
    nw, nh = max(1, int(layer.width * sc)), max(1, int(layer.height * sc))
    L = layer.resize((nw, nh), Image.BILINEAR) if sc != 1 else layer
    if alpha < 1:
        L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(L, (int(x + (layer.width - nw) / 2), int(y + (layer.height - nh) / 2)), L)


def chip(img, t, a, b, text, cx, cy, icon, style, size):
    f, size, _, box, tw, th = fit(text, size, W - 200)
    ch = int(size * 2.05)
    iw = int(size * 1.25) if icon else 0
    cw = tw + iw + int(size * 1.5)
    x0 = int(clamp(cx - cw / 2, 10, W - cw - 10))
    y0 = int(clamp(cy - ch / 2, 10, H - ch - 10))
    if style == "glass":
        c = glass(img, (x0, y0, x0 + cw, y0 + ch), ch // 2)
        colour = WHITE
    else:
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ImageDraw.Draw(c).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=ch // 2, fill=YELLOW + (255,))
        colour = INK
    d = ImageDraw.Draw(c)
    if icon:
        draw_icon(d, icon, cw - int(size * 0.75) - iw // 2 + 8, ch // 2, int(size * 0.5))
    tx = (cw - iw - tw) // 2 - box[0] - (6 if icon else 0)
    d.text((tx, (ch - th) // 2 - box[1]), text, font=f, fill=colour + (255,), direction="rtl")
    paste_anim(img, c, x0, y0, t, a, b)


def stat(img, t, a, b, value, suffix, label, cx, cy):
    if not (a <= t <= b):
        return
    cnt = int(round(value * ease_out((t - a) / 0.9)))
    num = f"{cnt}{suffix}"
    cw, ch = 420, 250
    x0, y0 = int(cx - cw / 2), int(cy - ch / 2)
    c = glass(img, (x0, y0, x0 + cw, y0 + ch), 40)
    d = ImageDraw.Draw(c)
    f, *_ = fit(f"{value}{suffix}", 92, cw - 40)
    box, tw, th = tsize(num, f)
    d.text(((cw - tw) // 2 - box[0], 40 - box[1]), num, font=f, fill=YELLOW + (255,), direction="rtl")
    f2 = font(48)
    box, tw, th = tsize(label, f2)
    d.text(((cw - tw) // 2 - box[0], 168 - box[1]), label, font=f2, fill=WHITE + (255,), direction="rtl")
    paste_anim(img, c, x0, y0, t, a, b)


def panel(img, t, a, b, heading, bullets):
    if not (a <= t <= b):
        return
    pw = W - 90
    fs = 46
    rows = []
    k = -1
    for line in bullets:
        sub = line.startswith("~")
        line = line.lstrip("~")
        k += 0 if sub else 1
        f, size, _, box, tw, th = fit(line, 38 if sub else fs, pw - 150)
        rows.append((line, f, box, tw, th, sub, k))
    rh = 92
    ph = 150 + rh * len(bullets) - 30 * sum(r[5] for r in rows)
    x0, y0 = 45, H - 150 - ph
    c = glass(img, (x0, y0, x0 + pw, y0 + ph), 44, tint=0.42)
    if c is None:
        return
    d = ImageDraw.Draw(c)
    hf = font(58)
    box, tw, th = tsize(heading, hf)
    hw_, hh = tw + 80, 96
    d.rounded_rectangle((pw - 30 - hw_, 30, pw - 30, 30 + hh), radius=hh // 2, fill=YELLOW + (255,))
    d.text((pw - 30 - hw_ + 40 - box[0], 30 + (hh - th) // 2 - box[1]), heading, font=hf, fill=INK + (255,), direction="rtl")
    base_alpha = clamp((t - a) / 0.15) * clamp((b - t) / 0.2)
    layer = c
    ybase = 150
    for (line, f, box, tw, th, sub, k) in rows:
        ta = a + 0.45 + k * BEAT
        y_here = ybase
        ybase += rh - (30 if sub else 0)
        if t < ta:
            continue
        p = ease_out((t - ta) / 0.25)
        yy = y_here - (22 if sub else 0) + int((1 - p) * 30)
        row = Image.new("RGBA", (pw, rh), (0, 0, 0, 0))
        rd = ImageDraw.Draw(row)
        if not sub:
            draw_icon(rd, "check", pw - 70, rh // 2, 24)
        rd.text((pw - 110 - tw - box[0], (rh - th) // 2 - box[1]), line, font=f,
                fill=(WHITE + (255,)) if not sub else (225, 225, 225, 255), direction="rtl")
        if p < 1:
            row.putalpha(row.getchannel("A").point(lambda v: int(v * p)))
        layer.alpha_composite(row, (0, yy))
    paste_anim(img, layer, x0, y0, t, a, b, pop=False)
    if base_alpha < 1:
        pass


def price(img, t, a, b):
    if not (a <= t <= b):
        return
    value = 8500000
    cnt = int(round(value * ease_out((t - a) / 1.1)))
    num = f"{cnt:,}"
    cw, ch = W - 120, 520
    x0, y0 = 60, H - 220 - ch
    c = glass(img, (x0, y0, x0 + cw, y0 + ch), 48, tint=0.45)
    d = ImageDraw.Draw(c)
    hf = font(56)
    box, tw, th = tsize("السعر", hf)
    hw_, hh = tw + 80, 94
    d.rounded_rectangle(((cw - hw_) // 2, 34, (cw + hw_) // 2, 34 + hh), radius=hh // 2, fill=YELLOW + (255,))
    d.text(((cw - tw) // 2 - box[0], 34 + (hh - th) // 2 - box[1]), "السعر", font=hf, fill=INK + (255,), direction="rtl")
    f = font(130)
    box, tw, th = tsize(num, f)
    d.text(((cw - tw) // 2 - box[0], 160 - box[1]), num, font=f, fill=YELLOW + (255,), direction="rtl",
           stroke_width=3, stroke_fill=(0, 0, 0, 120))
    f2 = font(56)
    box, tw, th = tsize("ريال سعودي", f2)
    d.text(((cw - tw) // 2 - box[0], 330 - box[1]), "ريال سعودي", font=f2, fill=WHITE + (255,), direction="rtl")
    note = "لا يشمل ضريبة التصرف العقاري ولا يشمل الرسوم الخاضعة لتملك الأجانب"
    f3, *_ = fit(note, 30, cw - 60)
    box, tw, th = tsize(note, f3)
    d.text(((cw - tw) // 2 - box[0], 440 - box[1]), note, font=f3, fill=(235, 235, 235, 255), direction="rtl")
    paste_anim(img, c, x0, y0, t, a, b)


# ---------------- frame assembly ----------------
def zoomed(arr, s):
    if s <= 1.0005:
        return arr
    img = Image.fromarray(arr)
    cw, ch = W / s, H / s
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    return np.asarray(img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))).copy()


def shot_at(t):
    i = min(int(np.searchsorted(START, t, side="right")) - 1, len(SHOTS) - 1)
    return i, SHOTS[i], t - START[i]


def finish(fr, t):
    i, s, lt = shot_at(t)
    z = 1 + 0.06 * (1 - ease_out(lt / 0.22))
    flash, blur = (0.85 * (1 - t / 0.15) if t < 0.15 else 0.0), 0.0
    for j in range(1, len(SHOTS)):
        if not (SHOTS[j].get("whip") or SHOTS[j].get("flash")):
            continue
        k = 1 - abs(t - START[j]) / 0.16
        if k > 0:
            if SHOTS[j].get("whip"):
                z *= 1 + 0.22 * k * k
                blur = max(blur, k)
            flash = max(flash, (0.95 if SHOTS[j].get("flash") else 0.55) * k ** 2.2)
    out = zoomed(fr, z)
    if blur > 0.05:
        acc = out.astype(np.float32)
        for extra in (1.04, 1.08):
            acc += zoomed(fr, z * (1 + (extra - 1) * blur)).astype(np.float32)
        out = (acc / 3).astype(np.uint8)
    if s["kind"] != "end":
        out = apply_sky(out, t)
        img = Image.fromarray(out)
        for a, b, text, cx, cy, icon, style, size in CHIPS:
            if a <= t <= b:
                chip(img, t, a, b, text, cx, cy, icon, style, size)
        for a, b, v, suf, lab, cx, cy in STATS:
            stat(img, t, a, b, v, suf, lab, cx, cy)
        for a, b, head, bl in PANELS:
            panel(img, t, a, b, head, bl)
        price(img, t, *PRICE)
        out = np.asarray(img).copy()
    if flash > 0.01:
        out = (out.astype(np.float32) * (1 - flash) + 255 * flash).astype(np.uint8)
    return out


def decode_video(path, start, dur, n, grade=True):
    vf = (VGRADE + "," if grade else "") + f"scale={W}:{H}:flags=lanczos," + ("unsharp=5:5:0.6," if grade else "") + f"fps={FPS}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur + 0.3:.3f}", "-i", path,
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
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


def shot_frames(work, endsrc, s, n=None, offset=0.0):
    n = n or s["n"]
    if s["kind"] == "photo":
        for k in range(n):
            yield grade_fast(photo_frame(work, s, offset + k / FPS))
    elif s["kind"] == "video":
        yield from decode_video(os.path.join(work, "15.mp4"), s["inp"] + offset, s["dur"], n)
    else:
        yield from decode_video(endsrc, s["inp"] + offset, s["dur"], n, grade=False)


# ---------------- music and sound ----------------
def note_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(total_s):
    n = int(total_s * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    bar = 4 * BEAT
    chords = [(41, [53, 57, 60, 64, 67]), (43, [55, 59, 62, 64, 67]), (40, [52, 55, 59, 62, 64]), (45, [57, 60, 64, 67, 71])]
    clen = 2 * bar
    pad = np.zeros(n, np.float32)
    bass = np.zeros(n, np.float32)
    pl = np.zeros(n, np.float32)
    rng = np.random.default_rng(11)
    k = 0
    while k * clen < total_s:
        root, notes = chords[k % 4]
        c0 = k * clen
        i0, i1 = int(c0 * SR), min(n, int((c0 + clen + 0.8) * SR))
        tt = t[i0:i1] - c0
        env = np.minimum(1, tt / 0.5) * np.clip((clen + 0.8 - tt) / 0.8, 0, 1)
        seg = np.zeros(i1 - i0, np.float32)
        for m in notes:
            f = note_hz(m)
            for det in (-0.12, 0.0, 0.13):
                ph = rng.uniform(0, 6.28)
                fd = f * 2 ** (det / 12)
                seg += (np.sin(2 * np.pi * fd * tt + ph) + 0.35 * np.sin(4 * np.pi * fd * tt + ph)
                        + 0.12 * np.sin(6 * np.pi * fd * tt + ph))
        pad[i0:i1] += seg * env * 0.022
        for bt in range(8):
            if bt % 4 in (0, 2) or bt == 7:
                b0 = c0 + bt * BEAT
                j0, j1 = int(b0 * SR), min(n, int((b0 + BEAT * 1.6) * SR))
                if j0 >= n:
                    continue
                tb = t[j0:j1] - b0
                fb = note_hz(root - 12 if root > 44 else root)
                bass[j0:j1] += (np.sin(2 * np.pi * fb * tb) + 0.3 * np.sin(4 * np.pi * fb * tb)) * np.exp(-tb * 2.2) * np.minimum(1, tb / 0.01) * 0.30
        arp = [notes[0] + 12, notes[2] + 12, notes[1] + 12, notes[3] + 12, notes[4], notes[2] + 12, notes[3] + 12, notes[1] + 12]
        for e in range(16):
            p0 = c0 + e * BEAT / 2
            if p0 < 2 * bar:
                continue
            j0, j1 = int(p0 * SR), min(n, int((p0 + 0.9) * SR))
            if j0 >= n:
                continue
            tp = t[j0:j1] - p0
            f = note_hz(arp[e % 8])
            pl[j0:j1] += (np.sin(2 * np.pi * f * tp) + 0.25 * np.sin(4 * np.pi * f * tp)) * np.exp(-tp * 7) * np.minimum(1, tp / 0.004) * 0.075
        k += 1
    drums = np.zeros(n, np.float32)
    b = 0
    while True:
        tb0 = 2 * bar + b * BEAT
        if tb0 > total_s - 2.5:
            break
        j0, j1 = int(tb0 * SR), min(n, int((tb0 + 0.35) * SR))
        tk = t[j0:j1] - tb0
        if b % 4 in (0, 2) or (b % 8 == 7):
            fk = 45 + 75 * np.exp(-tk * 30)
            drums[j0:j1] += np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tk * 9) * 0.55
        if b % 4 in (1, 3):
            nz = np.diff(np.concatenate([[0], rng.standard_normal(j1 - j0).astype(np.float32)]))
            drums[j0:j1] += nz * np.exp(-tk * 22) * 0.10
        h0 = tb0 + 0.5 * BEAT
        h0i, h1i = int(h0 * SR), min(n, int((h0 + 0.05) * SR))
        if h0i < n:
            th = t[h0i:h1i] - h0
            hz = np.diff(np.concatenate([[0], rng.standard_normal(h1i - h0i).astype(np.float32)]))
            drums[h0i:h1i] += hz * np.exp(-th * 80) * 0.05
        b += 1
    ir_len = int(1.8 * SR)
    ir = rng.standard_normal(ir_len).astype(np.float32) * np.exp(-np.arange(ir_len) / SR * 3.2)
    ir[0] = 0
    wet_in = pad + pl
    L = 1 << int(np.ceil(np.log2(n + ir_len)))
    wet = np.fft.irfft(np.fft.rfft(wet_in, L) * np.fft.rfft(ir, L), L)[:n].astype(np.float32)
    wet *= 0.25 / (np.abs(wet).max() + 1e-9) * (np.abs(wet_in).max() + 1e-9)
    pump = np.ones(n, np.float32)
    bb = 0
    while 2 * bar + bb * BEAT < total_s:
        if bb % 2 == 0:
            j0 = int((2 * bar + bb * BEAT) * SR)
            j1 = min(n, j0 + int(0.3 * SR))
            pump[j0:j1] = 1 - 0.35 * np.exp(-np.arange(j1 - j0) / SR * 10)
        bb += 1
    mono = pad * pump + bass + drums + wet * 0.9
    out[:, 0] = mono + pl * 0.8
    out[:, 1] = mono + pl * 1.1
    fade = int(1.6 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    out /= np.abs(out).max() + 1e-9
    return out * 0.55


def whoosh(dur=0.5, seed=1):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    tt = np.linspace(0, 1, n)
    cut = 300 + 5200 * np.sin(np.pi * tt) ** 2
    y = np.zeros(n, np.float32)
    acc = 0.0
    for i in range(n):
        al = 1 - math.exp(-2 * math.pi * cut[i] / SR)
        acc += al * (x[i] - acc)
        y[i] = acc
    y = y * np.sin(np.pi * tt) ** 1.5 / (np.abs(y).max() + 1e-9)
    pan = 0.5 + 0.4 * np.sin(np.pi * (tt - 0.5))
    return np.stack([y * (1 - pan) * 1.4, y * pan * 1.4], 1)


def boom(dur=0.9):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 42 + 50 * np.exp(-tt * 9)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5)
    return np.stack([y, y], 1).astype(np.float32)


def pop(freq=1150):
    n = int(0.09 * SR)
    tt = np.arange(n) / SR
    y = (np.sin(2 * np.pi * freq * tt) + 0.35 * np.sin(4 * np.pi * freq * tt)) * np.exp(-tt * 55)
    return np.stack([y, y], 1).astype(np.float32)


def ticks(dur):
    n = int(dur * SR)
    y = np.zeros(n, np.float32)
    k = 0
    while True:
        p = (k / 14) ** 1.8 * dur
        if p >= dur:
            break
        i = int(p * SR)
        m = min(n - i, int(0.02 * SR))
        tt = np.arange(m) / SR
        y[i:i + m] += np.sin(2 * np.pi * 2600 * tt) * np.exp(-tt * 300)
        k += 1
    return np.stack([y, y], 1)


def build_audio(path):
    total = TOTAL / FPS
    mix = music(total)
    nn = len(mix)

    def add(sig, at, gain):
        i = int(at * SR)
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(nn, i + len(sig))
        if j > i:
            mix[i:j] += sig[: j - i] * gain

    add(boom(), 0.0, 0.45)
    for j in range(1, len(SHOTS)):
        s = SHOTS[j]
        if s.get("whip"):
            add(whoosh(0.5, seed=j), START[j] - 0.27, 0.28)
        elif s.get("flash"):
            add(whoosh(0.6, seed=99), START[j] - 0.33, 0.25)
            add(boom(), START[j], 0.5)
        else:
            add(whoosh(0.32, seed=j), START[j] - 0.17, 0.10)
    for a, *_ in SKYTEXT:
        add(pop(700), a, 0.16)
    for a, *_ in CHIPS:
        add(pop(1200), a, 0.16)
    for a, b, v, *_ in STATS:
        add(ticks(0.9), a, 0.06)
    for a, b, head, bl in PANELS:
        add(pop(900), a, 0.14)
        for k in range(len([x for x in bl if not x.startswith("~")])):
            add(pop(1300), a + 0.45 + k * BEAT, 0.12)
    add(ticks(1.1), PRICE[0], 0.07)
    add(boom(), PRICE[0] + 1.1, 0.35)
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


def main():
    work, endsrc, dst = sys.argv[1:4]
    if "--stills" in sys.argv:
        os.makedirs(dst, exist_ok=True)
        for ts in sys.argv[sys.argv.index("--stills") + 1:]:
            t = float(ts)
            i, s, lt = shot_at(t)
            fr = next(shot_frames(work, endsrc, s, 1, lt))
            Image.fromarray(finish(fr.copy(), t)).save(os.path.join(dst, f"shati-villa-still-{int(round(t * 100)):04d}.png"))
        return
    wav = os.path.splitext(dst)[0] + "-audio.wav"
    build_audio(wav)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
         "-ar", str(SR), "-shortest", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    k = 0
    for s in SHOTS:
        for fr in shot_frames(work, endsrc, s):
            enc.stdin.write(finish(fr.copy(), k / FPS).tobytes())
            k += 1
            if k % 150 == 0:
                print(f"{k}/{TOTAL} frames", flush=True)
    enc.stdin.close()
    enc.wait()
    os.remove(wav)
    print("done", dst)


if __name__ == "__main__":
    main()
