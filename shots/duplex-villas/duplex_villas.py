"""Two duplex villas in Al-Shati: AI-style showcase edit of the user's Higgsfield shots.

Villa 1 (the beige corner villa): drone exterior, then each room as "before / after" -
the empty room, then a light wipe to the furnished version (labelled as an AI furniture
visualisation, because the furniture was generated). Villa 2 (the vine-gate villa):
entrance, pool, interior tour. Words in the sky behind trees and buildings, room cards,
punch-in cuts on the beat, whip transitions, synthesized music and sound effects,
Samat Alsakan end card.

Usage:
  python duplex_villas.py <src_dir> <endcard_ad.mp4> out.mp4
  python duplex_villas.py <src_dir> <endcard_ad.mp4> <outdir> --stills 1.0 5.2 ...
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 48000
BPM = 100
BEAT = 60 / BPM
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE, YELLOW, INK = (255, 255, 255), (255, 214, 64), (18, 18, 22)
GRADE = "eq=contrast=1.04:saturation=1.08,vignette=angle=PI/5"

T1 = [("فلتين دوبلكس", 118, WHITE, 440, 650), ("في حي الشاطئ", 80, YELLOW, 590, 650)]
# Each shot: src clip id, in-point, output duration, speed, and what sits on it.
SHOTS = [
    dict(src="8a953d48", inp=0.20, dur=8 * BEAT, title=(0.25, 3.6, T1)),
    dict(src="c1711b89", inp=0.40, dur=4 * BEAT, title=(0.15, 2.3, [("الفيلا", 112, WHITE, 290, 800), ("الأولى", 112, YELLOW, 420, 800)]), whip=True),
    dict(src="4ed1c290", inp=0.30, dur=4 * BEAT, room="المدخل"),
    dict(src="156994c8", alt="ded4fcf1", inp=0.20, dur=6 * BEAT, room="الصالة"),
    dict(src="bea84d41", alt="2499c1c5", inp=0.20, dur=5 * BEAT, room="الدرج"),
    dict(src="026fec05", inp=0.40, dur=4 * BEAT, speed=1.3),
    dict(src="189f8767", alt="6e0d76c9", inp=0.20, dur=6 * BEAT, room="المطبخ"),
    dict(src="43f8ddcd", alt="82d60978", inp=0.20, dur=5 * BEAT, room="صالة المعيشة"),
    dict(src="f85f7f73", alt="db6be470", inp=0.20, dur=6 * BEAT, room="غرفة النوم الرئيسية"),
    dict(src="3667ddca", alt="e12e293f", inp=0.30, dur=4 * BEAT, room="دورة المياه"),
    dict(src="45eda15e", inp=1.00, dur=5 * BEAT, room="المسبح"),
    dict(src="0570a73f", inp=0.30, dur=5 * BEAT, speed=1.4, whip=True,
         title=(0.15, 2.8, [("الفيلا الثانية", 120, WHITE, 330)], False)),
    dict(src="34c55afa", inp=0.00, dur=5 * BEAT, speed=1.4, room="المسبح"),
    dict(src="ef25b8d4", inp=0.40, dur=14 * BEAT, speed=1.7,
         rooms=[(0.40, 3.9, "المدخل"), (4.0, 5.9, "الصالة"), (6.0, 6.95, "المجلس"),
                (7.0, 8.95, "المطبخ"), (9.0, 11.95, "الدرج"), (12.0, 15.0, "غرفة النوم")]),
    dict(src="ce52997f", inp=1.20, dur=6 * BEAT, whip=True, title=(0.2, 3.3, T1)),
    dict(src="END", inp=34.0, dur=6 * BEAT, end=True, flash=True),
]
WIPE = (1.5 * BEAT, 2.8 * BEAT)  # before -> after wipe window inside a shot

for s in SHOTS:
    s.setdefault("speed", 1.0)
    s["n"] = round(s["dur"] * FPS)
START = np.concatenate([[0], np.cumsum([s["n"] for s in SHOTS])]) / FPS
TOTAL = sum(s["n"] for s in SHOTS)
SRC_DIR, END_SRC = "", ""


def shot_at(t):
    i = min(int(np.searchsorted(START, t, side="right")) - 1, len(SHOTS) - 1)
    return i, SHOTS[i], t - START[i]


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


# ---------------- words in the sky ----------------
def render_sky(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, size, colour, yc, *cx in lines:
        cx = cx[0] if cx else W // 2
        while True:
            f = font(size)
            st = max(3, size // 28)
            box, tw, th = tsize(text, f, st)
            if tw <= W - 90:
                break
            size -= 6
        d.text((min(max(cx - tw // 2, 25), W - 25 - tw) - box[0], yc - th // 2 - box[1]), text, font=f, fill=colour + (255,),
               direction="rtl", stroke_width=st, stroke_fill=(10, 14, 30, 120))
    a = np.asarray(img)[..., 3].astype(np.float32)
    sh = Image.fromarray((a * 0.4).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (W, H), (8, 16, 40, 0))
    out.putalpha(sh)
    out = out.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -10))
    out.alpha_composite(img)
    bb = out.getbbox()
    return out.crop(bb), bb


SKY = []  # (t0, t1, layer, bbox, behind)
for i, s in enumerate(SHOTS):
    if "title" in s:
        a, b, lines, *behind = s["title"]
        SKY.append((START[i] + a, START[i] + b) + render_sky(lines) + (behind[0] if behind else True,))


def sky_mask(rgb, y0, y1):
    f = rgb[y0:y1].astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    blue = ((b - r >= 14) & (b > 140) & (b >= g - 6)) | ((b - r >= 22) & (b > 70) & (b >= g))  # second: vignetted corners
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


# ---------------- glass cards ----------------
def draw_icon(d, kind, cx, cy, r):
    if kind == "pin":
        d.polygon([(cx - r * 0.78, cy - r * 0.25), (cx + r * 0.78, cy - r * 0.25), (cx, cy + r * 1.15)], fill=YELLOW + (255,))
        d.ellipse((cx - r * 0.82, cy - r * 1.05, cx + r * 0.82, cy + r * 0.55), fill=YELLOW + (255,))
        d.ellipse((cx - r * 0.32, cy - r * 0.55, cx + r * 0.32, cy + r * 0.05), fill=INK + (255,))
    elif kind == "spark":
        pts = []
        for k in range(8):
            ang = k * math.pi / 4
            rr = r if k % 2 == 0 else r * 0.38
            pts.append((cx + rr * math.sin(ang), cy - rr * math.cos(ang)))
        d.polygon(pts, fill=YELLOW + (255,))


def chip(img, t, a, b, text, cx, cy, icon=None, style="glass", size=50):
    f = font(size)
    box, tw, th = tsize(text, f)
    ch = int(size * 2.05)
    iw = int(size * 1.25) if icon else 0
    cw = tw + iw + int(size * 1.5)
    x0 = int(clamp(cx - cw / 2, 10, W - cw - 10))
    y0 = int(clamp(cy - ch / 2, 10, H - ch - 10))
    c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=ch // 2, fill=255)
    if style == "glass":
        bg = img.crop((x0, y0, x0 + cw, y0 + ch)).filter(ImageFilter.GaussianBlur(14))
        bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 255, 255)), 0.2)
        bg = Image.blend(bg, Image.new("RGB", bg.size, (20, 30, 50)), 0.32)
        c.paste(bg, (0, 0), mask)
        colour = WHITE
    else:
        c.paste(Image.new("RGB", (cw, ch), YELLOW), (0, 0), mask)
        colour = INK
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((1, 1, cw - 2, ch - 2), radius=ch // 2 - 1, outline=(255, 255, 255, 170), width=3)
    if icon:
        draw_icon(d, icon, cw - int(size * 0.75) - iw // 2 + 8, ch // 2, int(size * 0.5))
    tx = (cw - iw - tw) // 2 - box[0] - (6 if icon else 0)
    d.text((tx, (ch - th) // 2 - box[1]), text, font=f, fill=colour + (255,), direction="rtl")
    p = ease_back((t - a) / 0.3)
    sc = 0.55 + 0.45 * p
    alpha = clamp((t - a) / 0.12) * clamp((b - t) / 0.18)
    nw, nh = max(1, int(cw * sc)), max(1, int(ch * sc))
    c = c.resize((nw, nh), Image.BILINEAR)
    if alpha < 1:
        c.putalpha(c.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(c, (x0 + (cw - nw) // 2, y0 + (ch - nh) // 2), c)


def small_note(img, text, cy, alpha):
    f = font(34)
    box, tw, th = tsize(text, f, 3)
    layer = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((10 - box[0], 10 - box[1]), text, font=f, fill=(255, 255, 255, int(235 * alpha)),
                               direction="rtl", stroke_width=3, stroke_fill=(0, 0, 0, int(200 * alpha)))
    img.paste(layer, ((W - layer.width) // 2, cy - layer.height // 2), layer)


# ---------------- camera ----------------
def zoomed(img, s, fx=540, fy=960):
    if s <= 1.0005:
        return img
    cw, ch = W / s, H / s
    x0 = clamp(fx - cw / 2, 0, W - cw)
    y0 = clamp(fy - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def render(frames, t):
    i, s, lt = shot_at(t)
    frac = lt / s["dur"]
    z = 1.0 + 0.04 * frac
    z *= 1 + 0.07 * (1 - ease_out(lt / 0.22))  # punch-in on every cut
    flash = 0.0
    blur = 0.0
    if t < 0.15:
        flash = 0.85 * (1 - t / 0.15)
    for j in range(1, len(SHOTS)):
        if not (SHOTS[j].get("whip") or SHOTS[j].get("flash")):
            continue
        k = 1 - abs(t - START[j]) / 0.16
        if k > 0:
            if SHOTS[j].get("whip"):
                z *= 1 + 0.24 * k * k
                blur = max(blur, k)
            flash = max(flash, (0.95 if SHOTS[j].get("flash") else 0.6) * k ** 2.2)

    def cam(arr):
        img = Image.fromarray(arr)
        out = zoomed(img, z)
        if blur > 0.05:
            acc = np.asarray(out).astype(np.float32)
            for extra in (1.04, 1.08):
                acc += np.asarray(zoomed(img, z * (1 + (extra - 1) * blur))).astype(np.float32)
            return (acc / 3).astype(np.uint8)
        return np.asarray(out).copy()

    fr = cam(frames[0])
    ba_after = False
    if len(frames) > 1:  # before / after wipe
        p = ease_io((lt - WIPE[0]) / (WIPE[1] - WIPE[0]))
        if p > 0:
            after = cam(frames[1])
            xb = int(W * (1 - p))
            fr[:, xb:] = after[:, xb:]
            if 0 < p < 1:
                for off, al in ((0, 1.0), (3, 0.7), (7, 0.4), (12, 0.2), (18, 0.1)):
                    for xx in (xb - off, xb + off):
                        if 0 <= xx < W:
                            fr[:, xx] = (fr[:, xx] * (1 - al) + 255 * al).astype(np.uint8)
        ba_after = p >= 0.5
    if not s.get("end"):
        fr = apply_sky(fr, t)
        img = Image.fromarray(fr)
        a0, a1 = START[i] + 0.12, START[i + 1] - 0.05
        if "room" in s:
            chip(img, t, a0, a1, s["room"], 540, 255, icon="pin")
        for r0, r1, name in s.get("rooms", []):
            o0 = START[i] + (r0 - s["inp"]) / s["speed"]
            o1 = START[i] + (r1 - s["inp"]) / s["speed"]
            if o0 <= t <= o1:
                chip(img, t, max(o0, a0), min(o1, a1), name, 540, 255, icon="pin")
        if "alt" in s:
            if not ba_after:
                chip(img, t, a0, START[i] + WIPE[0] + 0.5 * (WIPE[1] - WIPE[0]), "قبل التأثيث", 540, 1640, size=46)
            else:
                ta = START[i] + WIPE[0] + 0.5 * (WIPE[1] - WIPE[0])
                chip(img, t, ta, a1, "بعد التأثيث", 540, 1640, icon="spark", style="solid", size=46)
                small_note(img, "تصوّر الأثاث بالذكاء الاصطناعي", 1765, clamp((t - ta) / 0.2) * clamp((a1 - t) / 0.18))
        fr = np.asarray(img).copy()
    if flash > 0.01:
        fr = (fr.astype(np.float32) * (1 - flash) + 255 * flash).astype(np.uint8)
    return fr


# ---------------- decoding ----------------
def src_path(clip):
    return END_SRC if clip == "END" else os.path.join(SRC_DIR, clip + ".mp4")


def decode(clip, start, dur, speed, n, end=False):
    vf = (GRADE + "," if not end else "") + f"scale={W}:{H}:flags=lanczos," + \
         ("unsharp=5:5:0.5," if not end else "") + f"setpts=PTS/{speed},fps={FPS}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur * speed + 0.3:.3f}",
                          "-i", src_path(clip), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
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


def shot_frames(s, n=None, offset=0.0):
    n = n or s["n"]
    a = decode(s["src"], s["inp"] + offset * s["speed"], s["dur"], s["speed"], n, s.get("end", False))
    if "alt" in s:
        b = decode(s["alt"], s["inp"] + offset * s["speed"], s["dur"], s["speed"], n)
        for x, y in zip(a, b):
            yield (x, y)
    else:
        for x in a:
            yield (x,)


# ---------------- music and sound ----------------
def note_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(total_s):
    n = int(total_s * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    bar = 4 * BEAT
    # Am9, Fmaj7, Cmaj7(add9), G6 - two bars each
    chords = [(45, [57, 60, 64, 67, 71]), (41, [53, 57, 60, 64, 67]), (48, [55, 60, 64, 67, 71]), (43, [55, 59, 62, 64, 67])]
    clen = 2 * bar
    pad = np.zeros(n, np.float32)
    bass = np.zeros(n, np.float32)
    pl = np.zeros(n, np.float32)
    rng = np.random.default_rng(7)
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
        for bt in range(8):  # bass on beats 1 and 3 (and a pickup)
            if bt % 4 in (0, 2) or bt == 7:
                b0 = c0 + bt * BEAT
                j0, j1 = int(b0 * SR), min(n, int((b0 + BEAT * 1.6) * SR))
                if j0 >= n:
                    continue
                tb = t[j0:j1] - b0
                fb = note_hz(root - 12 if root > 44 else root)
                bass[j0:j1] += (np.sin(2 * np.pi * fb * tb) + 0.3 * np.sin(4 * np.pi * fb * tb)) * np.exp(-tb * 2.2) * np.minimum(1, tb / 0.01) * 0.30
        arp = [notes[0] + 12, notes[2] + 12, notes[1] + 12, notes[3] + 12, notes[4], notes[2] + 12, notes[3] + 12, notes[1] + 12]
        for e in range(16):  # eighth-note plucks
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
    # drums from bar 3
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
            nz = rng.standard_normal(j1 - j0).astype(np.float32)
            nz = np.diff(np.concatenate([[0], nz]))
            drums[j0:j1] += nz * np.exp(-tk * 22) * 0.10
        for half in (0.5,):
            h0 = tb0 + half * BEAT
            h0i, h1i = int(h0 * SR), min(n, int((h0 + 0.05) * SR))
            if h0i < n:
                th = t[h0i:h1i] - h0
                hz = rng.standard_normal(h1i - h0i).astype(np.float32)
                hz = np.diff(np.concatenate([[0], hz]))
                drums[h0i:h1i] += hz * np.exp(-th * 80) * 0.05
        b += 1
    # simple reverb on pad + plucks
    ir_len = int(1.8 * SR)
    ir = rng.standard_normal(ir_len).astype(np.float32) * np.exp(-np.arange(ir_len) / SR * 3.2)
    ir[0] = 0
    wet_in = pad + pl
    L = 1 << int(np.ceil(np.log2(n + ir_len)))
    wet = np.fft.irfft(np.fft.rfft(wet_in, L) * np.fft.rfft(ir, L), L)[:n].astype(np.float32)
    wet *= 0.25 / (np.abs(wet).max() + 1e-9) * (np.abs(wet_in).max() + 1e-9)
    # gentle sidechain pump on the pad from the kick
    pump = np.ones(n, np.float32)
    bb = 0
    while 2 * bar + bb * BEAT < total_s:
        if bb % 2 == 0:
            j0 = int((2 * bar + bb * BEAT) * SR)
            j1 = min(n, j0 + int(0.3 * SR))
            pump[j0:j1] = 1 - 0.35 * np.exp(-np.arange(j1 - j0) / SR * 10)
        bb += 1
    mono_l = pad * pump + bass + drums + wet * 0.9
    mono_r = pad * pump + bass + drums + wet * 0.9
    out[:, 0] = mono_l + pl * 0.8
    out[:, 1] = mono_r + pl * 1.1
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


def shimmer(dur=0.7):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    y = np.zeros(n)
    for k, f in enumerate((1760, 2217, 2637, 3322, 3520, 4435)):
        t0 = k * dur / 8
        m = tt >= t0
        y[m] += np.sin(2 * np.pi * f * (tt[m] - t0)) * np.exp(-(tt[m] - t0) * 9)
    y *= np.minimum(1, tt / 0.01)
    return np.stack([y * 0.8, y], 1).astype(np.float32)


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
            add(whoosh(0.5, seed=j), START[j] - 0.27, 0.30)
        elif s.get("flash"):
            add(whoosh(0.6, seed=99), START[j] - 0.33, 0.25)
            add(boom(), START[j], 0.5)
        else:
            add(whoosh(0.32, seed=j), START[j] - 0.17, 0.12)
    for j, s in enumerate(SHOTS):
        if "alt" in s:
            add(shimmer(), START[j] + WIPE[0], 0.10)
        if "room" in s:
            add(pop(1200), START[j] + 0.12, 0.16)
        for r0, r1, name in s.get("rooms", []):
            add(pop(1200), START[j] + max((r0 - s["inp"]) / s["speed"], 0.12), 0.16)
    for a, *_ in SKY:
        add(pop(700), a, 0.16)
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


def main():
    global SRC_DIR, END_SRC
    SRC_DIR, END_SRC, dst = sys.argv[1:4]
    if "--stills" in sys.argv:
        os.makedirs(dst, exist_ok=True)
        for ts in sys.argv[sys.argv.index("--stills") + 1:]:
            t = float(ts)
            i, s, lt = shot_at(t)
            frs = next(shot_frames(s, 1, lt))
            Image.fromarray(render([f.copy() for f in frs], t)).save(
                os.path.join(dst, f"duplex-villas-still-{int(round(t * 100)):04d}.png"))
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
        for frs in shot_frames(s):
            enc.stdin.write(render([f.copy() for f in frs], k / FPS).tobytes())
            k += 1
            if k % 150 == 0:
                print(f"{k}/{TOTAL} frames", flush=True)
    enc.stdin.close()
    enc.wait()
    os.remove(wav)
    print("done", dst)


if __name__ == "__main__":
    main()
