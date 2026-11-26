#!/usr/bin/env python3
"""bin-sulaiman-tower: vertical Short (talking head + building b-roll + Arabic captions/graphics).

    python shots/bin-sulaiman-tower/build.py --stills     # key frames as PNG, to check by eye
    python shots/bin-sulaiman-tower/build.py --render     # full clip (run audio.py first)

1080x1920, 30 fps, 875 frames (29.17 s). Timing follows the speaker's own words (word timestamps
from a local faster-whisper transcript).
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "bin-sulaiman-tower"
U = "/root/.claude/uploads/999ee3d3-348d-5550-a2bd-b38465d36af0/"
FACE = U + "34d6d11a-copy_C4652030-4B84-4704-B5D7-554DE7948489_compressed_by_happyscribe.com.mov"
CLIP_A = U + "51d86c6c-4ac632bd-1ba1-4a6a-9d37-66d004692ec6.mov"   # drive-past, road side
CLIP_B = U + "b01c9943-b0eb2254-506c-42cb-a371-beaf2bb19440.mov"   # from the car, roundabout, zooms in
CLIP_C = U + "dedc44c2-05d1a895-6d74-484d-9315-aa8c0eccec44.mov"   # short road pan with crane
PHOTO_FILES = {"p1": "c8dc2a01-image.jpg", "p2": "efb0eec0-image.jpg", "p3": "412a843c-image.jpg",
               "p5": "d1f5d98b-image.jpg", "p6": "c3209cfd-image.jpg"}
FONT_DIR = os.path.join(HERE, "fonts")
TAJ = os.path.join(FONT_DIR, "Tajawal-ExtraBold.ttf")
PLEX_B = os.path.join(FONT_DIR, "IBMPlexSansArabic-Bold.ttf")
PLEX_M = os.path.join(FONT_DIR, "IBMPlexSansArabic-Medium.ttf")

W, H, FPS = 1080, 1920, 30
N = 875
YELLOW = (255, 199, 44, 255)
WHITE = (255, 255, 255, 255)
INK = (17, 17, 17, 255)


def fr(t):
    return int(round(t * FPS))


# ---------------------------------------------------------------- sources
BROLL = "eq=contrast=1.06:saturation=1.12,unsharp=5:5:0.5"
FACE_GRADE = "eq=contrast=1.04:saturation=1.06"


def face_vf(w, h, x, y, ow=W, oh=H):
    return f"fps=30,crop={w}:{h}:{x}:{y},scale={ow}:{oh}:flags=lanczos,{FACE_GRADE}"


FACE13 = face_vf(830, 1476, 145, 444)
FACE14 = face_vf(772, 1372, 174, 548)
FACE15 = face_vf(720, 1280, 200, 640)
FACE_SPLIT = face_vf(900, 800, 110, 1060, W, H // 2)
CLIPB_VF = ("trim=duration=1.4,setpts=(PTS-STARTPTS)*1.6,"
            "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            f"crop=524:931:26:93,scale={W}:{H}:flags=lanczos,{BROLL}")
CLIP_VF = f"fps=30,scale={W}:{H}:flags=lanczos,{BROLL}"

SEGS = [
    dict(f0=0, f1=fr(2.24), kind="decode", src=CLIP_B, ss=0.5, vf=CLIPB_VF, whole=True),
    dict(f0=fr(2.24), f1=fr(3.20), kind="face", vf=FACE13),
    dict(f0=fr(3.20), f1=fr(5.72), kind="face", vf=FACE15),
    dict(f0=fr(5.72), f1=fr(7.24), kind="photo", img="p6", b0=(150, 0, 870, 1280), b1=(290, 80, 830, 1040)),
    dict(f0=fr(7.24), f1=fr(8.74), kind="photo", img="p1", b0=(150, 250, 690, 1210), b1=(300, 270, 840, 1230)),
    dict(f0=fr(8.74), f1=fr(13.72), kind="decode", src=CLIP_A, ss=2.40, vf=CLIP_VF),
    dict(f0=fr(13.72), f1=fr(16.34), kind="face", vf=FACE14),
    dict(f0=fr(16.34), f1=fr(19.46), kind="photo", img="p5", b0=(330, 120, 870, 1080), b1=(350, 140, 850, 1029)),
    dict(f0=fr(19.46), f1=fr(21.46), kind="decode", src=CLIP_C, ss=0.20, vf=CLIP_VF),
    dict(f0=fr(21.46), f1=fr(22.64), kind="photo", img="p2", b0=(100, 0, 820, 1280), b1=(170, 100, 770, 1167)),
    dict(f0=fr(22.64), f1=fr(24.42), kind="photo", img="p6", b0=(247, 83, 873, 1196), b1=(200, 0, 920, 1280),
         ease="out"),
    dict(f0=fr(24.42), f1=N, kind="split", img="p3", b0=(0, 140, 900, 940), b1=(80, 190, 840, 866)),
]

PHOTOS = {}


def photo(key):
    if key not in PHOTOS:
        im = Image.open(U + PHOTO_FILES[key]).convert("RGB")
        im = ImageEnhance.Contrast(im).enhance(1.06)
        im = ImageEnhance.Color(im).enhance(1.10)
        PHOTOS[key] = im
    return PHOTOS[key]


def ease_io(x):
    return x * x * (3 - 2 * x)


def ease_out(x):
    return 1 - (1 - x) ** 3


def kb(seg, k, size=(W, H)):
    n = seg["f1"] - seg["f0"]
    x = k / max(1, n - 1)
    e = ease_out(x) if seg.get("ease") == "out" else ease_io(x)
    box = tuple(a + (b - a) * e for a, b in zip(seg["b0"], seg["b1"]))
    return np.asarray(photo(seg["img"]).transform(size, Image.EXTENT, box, Image.BICUBIC))


def decode(src, ss, n, vf, w=W, h=H):
    cmd = ["nice", "-n", "10", "ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-i", src, "-vf", vf + ",format=rgb24",
           "-frames:v", str(n), "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size, last = w * h * 3, None
    for _ in range(n):
        buf = p.stdout.read(size)
        if len(buf) == size:
            last = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        if last is None:
            raise RuntimeError(f"no frames from {src}")
        yield last
    p.stdout.close()
    p.wait()


def seg_frames(seg, k0=0, count=None):
    """Frames k0..k0+count of a segment (k = offset inside the segment)."""
    n = seg["f1"] - seg["f0"]
    count = n - k0 if count is None else count
    kind = seg["kind"]
    if kind == "photo":
        for k in range(k0, k0 + count):
            yield kb(seg, k)
    elif kind == "face":
        yield from decode(FACE, (seg["f0"] + k0) / FPS, count, seg["vf"])
    elif kind == "decode":
        if seg.get("whole"):
            frames = list(decode(seg["src"], seg["ss"], n, seg["vf"]))
            yield from frames[k0:k0 + count]
        else:
            yield from decode(seg["src"], seg["ss"] + k0 / FPS, count, seg["vf"])
    elif kind == "split":
        faces = decode(FACE, (seg["f0"] + k0) / FPS, count, FACE_SPLIT, W, H // 2)
        for k, f in zip(range(k0, k0 + count), faces):
            top = kb(seg, k, (W, H // 2))
            yield np.vstack([top, f])


# ---------------------------------------------------------------- typography
_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fonts[key]


def shadowed(layer, blur=12, off=(0, 6), strength=0.55):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * strength))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(a)
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, dest=off)
    out.alpha_composite(layer)
    return out


def text_box(f, s):
    return f.getbbox(s, direction="rtl")


def draw_centered(d, cx, cy, s, f, fill, **kw):
    l, t, r, b = f.getbbox(s, direction="rtl", stroke_width=kw.get("stroke_width", 0))
    d.text((cx - (l + r) / 2, cy - (t + b) / 2), s, font=f, fill=fill, direction="rtl", **kw)


def caption_sprite(text, hl, size=88):
    words = text.split(" ")
    stroke = 7
    while True:
        f = font(TAJ, size)
        space = f.getlength(" ", direction="rtl")
        widths = [f.getlength(w, direction="rtl") for w in words]
        total = sum(widths) + space * (len(words) - 1)
        if total <= 880 or size <= 60:
            break
        size -= 4
    l, t, r, b = f.getbbox(text, direction="rtl", stroke_width=stroke)
    pad = 36
    cw, ch = int(total + 2 * pad + 2 * stroke), int(b - t + 2 * pad)
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = cw - pad - stroke
    for w, wd in zip(words, widths):
        x -= wd
        d.text((x, pad - t), w, font=f, fill=YELLOW if w in hl else WHITE, stroke_width=stroke,
               stroke_fill=(0, 0, 0, 255), direction="rtl")
        x -= space
    return shadowed(layer, blur=10, off=(0, 6), strength=0.6)


def pin_icon(s, color=YELLOW, hole=INK):
    im = Image.new("RGBA", (s, int(s * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(s * 0.14, s * 0.66), (s * 0.86, s * 0.66), (s * 0.5, s * 1.28)], fill=color)
    d.ellipse((0, 0, s - 1, s - 1), fill=color)
    r = s * 0.19
    d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=hole)
    return im


def check_icon(s):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=YELLOW)
    d.line([(s * 0.27, s * 0.53), (s * 0.44, s * 0.69), (s * 0.75, s * 0.36)], fill=INK, width=max(3, int(s * 0.12)),
           joint="curve")
    return im


def pill(text, f, fg, bg, padx=40, pady=18, icon=None, gap=18, shadow=True, min_h=None):
    l, t, r, b = f.getbbox(text, direction="rtl")
    tw, th = r - l, b - t
    iw = icon.width if icon is not None else 0
    ih = icon.height if icon is not None else 0
    pw = int(tw + 2 * padx + (iw + gap if icon is not None else 0))
    ph = int(max(th, ih, min_h or 0) + 2 * pady)
    m = 30
    layer = Image.new("RGBA", (pw + 2 * m, ph + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((m, m, m + pw, m + ph), radius=ph // 2, fill=bg)
    if icon is not None:   # icon on the right (start of an Arabic line)
        layer.alpha_composite(icon, dest=(int(m + pw - padx - iw), int(m + (ph - ih) / 2)))
        cx = m + padx + tw / 2
    else:
        cx = m + pw / 2
    draw_centered(d, cx, m + ph / 2, text, f, fg)
    return shadowed(layer, blur=14, off=(0, 6), strength=0.45) if shadow else layer


# ---------------------------------------------------------------- overlay content
CAPS = [
    (0.00, 1.40, "وين تتوقعون", []),
    (1.40, 2.24, "هالمبنى", ["هالمبنى"]),
    (2.24, 3.20, "يا أهل جدة؟", ["جدة؟"]),
    (3.20, 5.12, "هالمبنى الجميل", []),
    (5.12, 5.72, "الفخم", ["الفخم"]),
    (5.72, 6.66, "هو اللي", []),
    (6.66, 7.54, "قالوا لك عليه", []),
    (7.54, 8.74, "التغذية البصرية", ["التغذية", "البصرية"]),
    (8.74, 10.46, "هذا المبنى في", []),
    (13.72, 15.12, "والمبنى هذا", []),
    (15.12, 16.34, "كل ما أمر منه", []),
    (16.34, 17.08, "ما شاء الله", []),
    (17.08, 17.92, "GRC", ["GRC"]),
    (17.92, 19.46, "يليق بشكل مو طبيعي", ["مو", "طبيعي"]),
    (19.46, 20.56, "وغير كذا", []),
    (20.56, 21.78, "كل ماله يصير", []),
    (21.78, 22.64, "أفخم وأفخم", ["أفخم", "وأفخم"]),
]
CAP_Y = 1470
T_LOC, T_LOC_SUB, T_LOC_END = 10.46, 11.48, 13.72
T_GRC, T_GRC_SUB, T_GRC_END = 17.08, 17.40, 19.46
T_NAME, T_NAME_END = 22.64, 24.42
T_SPLIT = 24.42
CHIPS = [(24.49, "مبنى مكتبي جديد"), (25.98, "موقع استراتيجي"), (27.92, "إطلالة بحرية")]

SPR = {}


def sprites():
    if SPR:
        return SPR
    SPR["caps"] = [caption_sprite(t, hl) for _, _, t, hl in CAPS]
    SPR["hook"] = pill("شفتوه؟", font(TAJ, 104), INK, YELLOW, padx=56, pady=14)
    # location card parts
    ft, fs = font(TAJ, 86), font(PLEX_M, 46)
    title, sub = "حي المرجان", "طريق الكورنيش · أبحر الجنوبية"
    pin = pin_icon(58)
    tl, tt, tr, tb = ft.getbbox(title, direction="rtl")
    sl, st, sr, sb = fs.getbbox(sub, direction="rtl")
    inner = max(tr - tl + pin.width + 22, sr - sl)
    cw, chh = int(inner + 2 * 56), 250
    t_layer = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    d = ImageDraw.Draw(t_layer)
    row_w = tr - tl + pin.width + 22
    x_right = cw / 2 + row_w / 2
    t_layer.alpha_composite(pin, dest=(int(x_right - pin.width), 34))
    draw_centered(d, x_right - pin.width - 22 - (tr - tl) / 2, 82, title, ft, WHITE)
    s_layer = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    draw_centered(ImageDraw.Draw(s_layer), cw / 2, 178, sub, fs, (236, 236, 236, 255))
    SPR["loc"] = (t_layer, s_layer)
    # GRC callout
    SPR["grc"] = pill("GRC", font(TAJ, 112), INK, YELLOW, padx=60, pady=10)
    SPR["grc_sub"] = pill("خرسانة مسلّحة بالألياف الزجاجية", font(PLEX_B, 46), WHITE, (0, 0, 0, 185), padx=38,
                          pady=16)
    # name reveal
    fn = font(TAJ, 124)
    name = "برج بن سليمان"
    l, t, r, b = fn.getbbox(name, direction="rtl")
    lay = Image.new("RGBA", (int(r - l + 120), int(b - t + 120)), (0, 0, 0, 0))
    draw_centered(ImageDraw.Draw(lay), lay.width / 2, lay.height / 2, name, fn, WHITE)
    SPR["name"] = shadowed(lay, blur=18, off=(0, 8), strength=0.7)
    SPR["name_w"] = r - l
    SPR["kicker"] = pill("حي المرجان · جدة", font(PLEX_B, 46), WHITE, (0, 0, 0, 0), padx=0, pady=8,
                         icon=pin_icon(40), gap=14, shadow=False)
    SPR["kicker"] = shadowed(SPR["kicker"], blur=8, off=(0, 3), strength=0.8)
    grad = np.zeros((H, W, 4), np.uint8)
    ramp = np.clip((np.arange(H) - 720) / (H - 720), 0, 1) ** 1.3 * 215
    grad[..., 3] = ramp[:, None].astype(np.uint8)
    SPR["grad"] = Image.fromarray(grad, "RGBA")
    # split screen
    SPR["name_pill"] = pill("برج بن سليمان", font(TAJ, 58), INK, YELLOW, padx=40, pady=10)
    SPR["chips"] = [pill(s, font(TAJ, 60), INK, (255, 255, 255, 245), padx=34, pady=14, icon=check_icon(54), gap=18)
                    for _, s in CHIPS]
    return SPR


def back_ease(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def with_alpha(sp, a):
    if a >= 0.999:
        return sp
    sp = sp.copy()
    sp.putalpha(sp.getchannel("A").point(lambda v: int(v * a)))
    return sp


def put(img, sp, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.001:
        return
    if abs(scale - 1) > 0.002:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.BILINEAR)
    sp = with_alpha(sp, alpha)
    img.alpha_composite(sp, dest=(int(round(cx - sp.width / 2)), int(round(cy - sp.height / 2))))


def pop_in(dt, dur=0.22, start=0.72):
    if dt < 0:
        return 0.0, 0.0
    x = min(1.0, dt / dur)
    return start + (1 - start) * back_ease(x), min(1.0, dt / 0.08)


def slide(dt, dur=0.28):
    if dt < 0:
        return 0.0, 1.0
    x = min(1.0, dt / dur)
    e = ease_out(x)
    return e, 1 - e


def glass(img, box, radius, alpha):
    x0, y0, x1, y1 = [int(v) for v in box]
    reg = img.crop((x0, y0, x1, y1)).convert("RGB").filter(ImageFilter.GaussianBlur(22))
    reg = ImageEnhance.Brightness(reg).enhance(0.45).convert("RGBA")
    mask = Image.new("L", reg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, reg.width - 1, reg.height - 1), radius=radius,
                                           fill=int(255 * alpha))
    reg.putalpha(mask)
    edge = Image.new("RGBA", reg.size, (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle((0, 0, reg.width - 1, reg.height - 1), radius=radius,
                                           outline=(255, 255, 255, int(70 * alpha)), width=2)
    reg.alpha_composite(edge)
    img.alpha_composite(reg, dest=(x0, y0))


def overlay(base, i):
    S = sprites()
    t = i / FPS
    img = Image.fromarray(base).convert("RGBA")

    # hook pill
    if t < 2.24:
        s, a = pop_in(t - 0.0)
        put(img, S["hook"], W / 2, 330, s, a)

    # captions
    for (t0, t1, _, _), sp in zip(CAPS, S["caps"]):
        if t0 <= t < t1:
            s, a = pop_in(t - t0, dur=0.16, start=0.86)
            put(img, sp, W / 2, CAP_Y, s, max(a, 0.6))

    # location card
    if T_LOC <= t < T_LOC_END:
        e, rest = slide(t - T_LOC)
        t_layer, s_layer = S["loc"]
        cx, cy = W / 2, 1440 + 40 * rest
        box = (cx - t_layer.width / 2, cy - t_layer.height / 2, cx + t_layer.width / 2, cy + t_layer.height / 2)
        glass(img, box, 44, e)
        put(img, t_layer, cx, cy, 1.0, e)
        if t >= T_LOC_SUB:
            e2, _ = slide(t - T_LOC_SUB, 0.2)
            put(img, s_layer, cx, cy + 12 * (1 - e2), 1.0, e2)

    # GRC callout
    if T_GRC <= t < T_GRC_END:
        s, a = pop_in(t - T_GRC)
        put(img, S["grc"], W / 2, 320, s, a)
        if t >= T_GRC_SUB:
            e, rest = slide(t - T_GRC_SUB, 0.22)
            put(img, S["grc_sub"], W / 2, 462 - 20 * rest, 1.0, e)

    # name reveal
    if T_NAME <= t < T_NAME_END:
        img.alpha_composite(S["grad"])
        s, a = pop_in(t - T_NAME, dur=0.28, start=0.8)
        put(img, S["name"], W / 2, 1330, s, a)
        e, rest = slide(t - T_NAME - 0.12, 0.25)
        put(img, S["kicker"], W / 2, 1185 + 18 * rest, 1.0, e)
        bar_e = ease_out(min(1.0, max(0.0, (t - T_NAME - 0.18) / 0.35)))
        bw = SPR["name_w"] * 0.55 * bar_e
        if bw > 4:
            ImageDraw.Draw(img).rounded_rectangle((W / 2 - bw / 2, 1440, W / 2 + bw / 2, 1452), radius=6,
                                                  fill=YELLOW)

    # split screen: divider, name pill, feature chips
    if t >= T_SPLIT:
        d = ImageDraw.Draw(img)
        d.rectangle((0, H // 2 - 4, W, H // 2 + 4), fill=YELLOW)
        e, _ = slide(t - T_SPLIT, 0.25)
        put(img, S["name_pill"], W / 2, 180, 1.0, e)
        for k, ((tc, _), sp) in enumerate(zip(CHIPS, S["chips"])):
            if t >= tc:
                e, rest = slide(t - tc, 0.26)
                right = 1012 + 70 * rest
                put(img, sp, right - sp.width / 2, 400 + k * 150, 1.0, e)
    return img.convert("RGB")


# ---------------------------------------------------------------- driver
def seg_of(i):
    for s in SEGS:
        if s["f0"] <= i < s["f1"]:
            return s
    raise IndexError(i)


STILLS = [fr(1.9), fr(4.6), fr(8.2), fr(12.4), fr(18.9), fr(21.0), fr(23.9), fr(28.6)]


def render_stills():
    for n, i in enumerate(STILLS, 1):
        seg = seg_of(i)
        frame = next(seg_frames(seg, i - seg["f0"], 1))
        out = os.path.join(HERE, f"{NAME}-still-{n:04d}.png")
        overlay(frame, i).save(out)
        print(out, f"t={i / FPS:.2f}s", seg["kind"])


def render():
    audio = os.path.join(HERE, "final_audio.wav")
    if not os.path.exists(audio):
        sys.exit("run audio.py first")
    out = os.path.join(HERE, f"{NAME}.mp4")
    enc = ["nice", "-n", "10", "ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", audio, "-map", "0:v", "-map", "1:a",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-profile:v", "high",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{N / FPS:.4f}", out]
    p = subprocess.Popen(enc, stdin=subprocess.PIPE)
    i = 0
    for seg in SEGS:
        for frame in seg_frames(seg):
            p.stdin.write(overlay(frame, i).tobytes())
            i += 1
            if i % 75 == 0:
                print(f"  frame {i}/{N}", flush=True)
    p.stdin.close()
    p.wait()
    print("wrote", out, i, "frames")


if __name__ == "__main__":
    if "--stills" in sys.argv:
        render_stills()
    elif "--render" in sys.argv:
        render()
    else:
        print(__doc__)
