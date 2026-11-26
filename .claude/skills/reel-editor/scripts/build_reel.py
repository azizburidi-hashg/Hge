"""Edit a vertical reel from a plan file: punch-in zoom cuts, glass info cards, word captions, pops and music.

  python build_reel.py --plan shots/NAME/plan.json

The plan (all times in seconds of the FINISHED video):
{
  "output": "shots/NAME/NAME.mp4",
  "size": "1080x1920", "fps": 30,
  "clips": [ {"path": "talking.mp4", "start": 0, "end": 44} ],   # one talking head, or several drone clips in order
  "audio": "clips" | "path/to/voiceover.mp3" | null,           # "clips" keeps the clips' own sound (silence if a clip has none)
  "words": "shots/NAME/words.json",                            # [["word", start, end], ...]  (optional)
  "captions": {"y": 0.70, "size": 74, "accent": "#FFFFFF", "max_words": 3},
  "zooms": [ {"t": 0, "scale": 1.0}, {"t": 2.1, "scale": 1.14, "focus_y": 0.40} ],  # each holds until the next
  "cards": [
    {"type": "pill",  "text": "Step 1 •○○", "start": 6, "end": 14, "y": 0.07},
    {"type": "card",  "title": "North Jeddah", "rows": [["Price", "SAR 3.2M"], ["Land", "450 m²"]], "start": 2, "end": 6, "y": 0.16},
    {"type": "stat",  "value": "450 m²", "label": "Land size", "start": 8, "end": 11, "y": 0.18},
    {"type": "cta",   "keyword": "VILLA", "note": "Details → your DMs", "start": 39, "end": 44, "y": 0.55}
  ],
  "music": "shots/NAME/music.mp3", "music_volume": 0.12,       # optional, looped and kept under the voice
  "sfx": true                                                  # soft pop on every card entrance
}

Prints one JSON line at the end: {"ok": true, "output": ..., "duration": ...} or {"ok": false, "error": ...}.
Needs ffmpeg/ffprobe and Node with Playwright (cards are drawn in a headless browser).
"""
import argparse
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "blender-shots", "fonts"))
AR_FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "fonts"))  # Cairo (Arabic + Latin), OFL


class PlanError(Exception):
    pass


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise PlanError("command failed: %s\n%s" % (cmd[0], p.stderr[-2500:]))
    return p.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
               "-of", "json", path])
    info = json.loads(out)
    dur = float(info["format"]["duration"])
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    return dur, has_audio


# ---------------------------------------------------------------- pass 1: clips -> one base video
def build_base(plan, W, H, fps, tmp):
    clips = plan.get("clips") or []
    if not clips:
        raise PlanError("plan has no clips")
    parts = []
    for i, c in enumerate(clips):
        path = c["path"]
        if not os.path.exists(path):
            raise PlanError("clip not found: %s" % path)
        dur, has_audio = probe(path)
        s = float(c.get("start", 0))
        e = float(c.get("end", dur))
        e = min(e, dur)
        if e <= s:
            raise PlanError("clip %d: end must be after start" % i)
        part = os.path.join(tmp, "part%02d.mp4" % i)
        vf = ("scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d,setsar=1,fps=%d,"
              "unsharp=5:5:%.2f,format=yuv420p" % (W, H, W, H, fps, float(plan.get("sharpen", 0.0))))
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % s, "-t", "%.3f" % (e - s), "-i", path]
        if has_audio:
            cmd += ["-vf", vf, "-af", "aresample=48000,aformat=channel_layouts=stereo"]
        else:
            cmd += ["-f", "lavfi", "-t", "%.3f" % (e - s), "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", vf, "-map", "0:v", "-map", "1:a"]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                "-shortest", part]
        run(cmd)
        parts.append(part)
    listfile = os.path.join(tmp, "parts.txt")
    with open(listfile, "w") as f:
        for p in parts:
            f.write("file '%s'\n" % p.replace("'", "'\\''"))
    base = os.path.join(tmp, "base.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", base])
    return base


# ---------------------------------------------------------------- cards (drawn by headless Chromium)
CARD_CSS = """
@font-face { font-family: Mont; src: url('file://%(fonts)s/Montserrat.ttf'); font-weight: 100 900; }
@font-face { font-family: Cairo; src: url('file://%(ar)s/Cairo-arabic-400.ttf'); font-weight: 400; unicode-range: U+0600-06FF, U+0750-077F, U+FB50-FDFF, U+FE70-FEFF, U+200C-200F; }
@font-face { font-family: Cairo; src: url('file://%(ar)s/Cairo-arabic-800.ttf'); font-weight: 700 900; unicode-range: U+0600-06FF, U+0750-077F, U+FB50-FDFF, U+FE70-FEFF, U+200C-200F; }
@font-face { font-family: Cairo; src: url('file://%(ar)s/Cairo-latin-400.ttf'); font-weight: 400; unicode-range: U+0000-00FF, U+2000-206F, U+2190-21FF; }
@font-face { font-family: Cairo; src: url('file://%(ar)s/Cairo-latin-800.ttf'); font-weight: 700 900; unicode-range: U+0000-00FF, U+2000-206F, U+2190-21FF; }
html, body { margin: 0; background: transparent; }
body.rtl { direction: rtl; font-family: Cairo, Mont, sans-serif; }
body.rtl .card .row, body.rtl .stat .label { font-weight: 600; }
body { width: %(W)dpx; display: flex; justify-content: center; padding: 30px 0; font-family: Mont, sans-serif; }
.pill { background: rgba(0,0,0,.88); color: #fff; font-weight: 800; font-size: 48px; padding: 20px 48px;
        border-radius: 999px; border: 2px solid rgba(255,255,255,.18); box-shadow: 0 10px 30px rgba(0,0,0,.35); }
.pill.big { font-size: 64px; padding: 22px 64px; }
.card { width: %(cw)dpx; background: rgba(18,18,20,.72); border: 2px solid rgba(255,255,255,.22);
        border-radius: 36px; padding: 34px 44px; color: #fff; box-shadow: 0 20px 50px rgba(0,0,0,.45);
        backdrop-filter: blur(20px); }
.card .title { font-weight: 800; font-size: 62px; margin-bottom: 18px; color: %(accent)s; }
.card .row { display: flex; justify-content: space-between; font-size: 52px; padding: 16px 0;
             border-top: 1px solid rgba(255,255,255,.14); }
.card .row:first-of-type { border-top: none; }
.card .row b { font-weight: 800; }
.stat { text-align: center; background: rgba(18,18,20,.72); border: 2px solid rgba(255,255,255,.22);
        border-radius: 36px; padding: 30px 60px; color: #fff; box-shadow: 0 20px 50px rgba(0,0,0,.45); }
.stat .value { font-weight: 800; font-size: 96px; color: %(accent)s; line-height: 1.05; }
.stat .label { font-size: 44px; opacity: .85; margin-top: 8px; }
.cta { width: %(cw)dpx; background: rgba(10,10,10,.9); border: 2px solid rgba(255,255,255,.2); border-radius: 30px;
       padding: 28px 36px; color: #fff; box-shadow: 0 20px 50px rgba(0,0,0,.5); }
.cta .box { display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,.08);
            border-radius: 999px; padding: 18px 30px; font-size: 42px; }
.cta .box b { font-weight: 800; }
.cta .send { font-weight: 800; color: #4aa3ff; }
.cta .note { margin-top: 18px; text-align: center; font-size: 34px; opacity: .85; }
"""

NODE_RENDER = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: jobs.width, height: 1200 } });
  for (const j of jobs.items) {
    await page.setContent(j.html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    if (j.box) {
      await page.screenshot({ path: j.out, omitBackground: true, clip: { x: 0, y: 0, width: jobs.width, height: j.box } });
    } else {
      const el = await page.$('#c');
      await el.screenshot({ path: j.out, omitBackground: true });
    }
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def card_html(card, W, accent, rtl=False):
    t = card.get("type", "card")
    if t == "pill":
        inner = '<div class="pill%s">%s</div>' % (" big" if card.get("big") else "", esc(card["text"]))
    elif t == "stat":
        inner = '<div class="stat"><div class="value">%s</div><div class="label">%s</div></div>' % (
            esc(card["value"]), esc(card.get("label", "")))
    elif t == "cta":
        inner = ('<div class="cta"><div class="box"><span>Comment <b>%s</b></span><span class="send">Send</span></div>'
                 '<div class="note">%s</div></div>') % (esc(card["keyword"]), esc(card.get("note", "")))
    elif t == "card":
        rows = "".join('<div class="row"><span>%s</span><b>%s</b></div>' % (esc(a), esc(b))
                       for a, b in card.get("rows", []))
        title = '<div class="title">%s</div>' % esc(card["title"]) if card.get("title") else ""
        inner = '<div class="card">%s%s</div>' % (title, rows)
    else:
        raise PlanError("unknown card type: %s" % t)
    css = CARD_CSS % {"fonts": FONT_DIR, "ar": AR_FONT_DIR, "W": W, "cw": int(W * 0.78), "accent": accent}
    return '<html><head><meta charset="utf-8"><style>%s</style></head><body class="%s"><div id="c">%s</div></body></html>' % (
        css, "rtl" if rtl else "", inner)


def render_cards(cards, W, accent, tmp, rtl=False):
    if not cards:
        return []
    items = []
    for i, c in enumerate(cards):
        out = os.path.join(tmp, "card%02d.png" % i)
        items.append({"html": card_html(c, W, accent, rtl), "out": out})
    jobfile = os.path.join(tmp, "cards.json")
    with open(jobfile, "w") as f:
        json.dump({"width": W, "items": items}, f, ensure_ascii=False)
    script = os.path.join(tmp, "render_cards.js")
    with open(script, "w") as f:
        f.write(NODE_RENDER)
    if not shutil.which("node"):
        raise PlanError("node is not installed (cards need Node + Playwright)")
    run(["node", script, jobfile])
    return [it["out"] for it in items]


# ---------------------------------------------------------------- captions (ASS, one short phrase at a time)
def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return "%d:%02d:%05.2f" % (h, m, s)


def ass_color(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return "&H00%s%s%s" % (b, g, r)


def ass_esc(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def caption_events(words, maxw):
    """Short phrases (<= maxw words, split at punctuation and pauses); one event per spoken word,
    returned as (start, end, [(word, is_current_word), ...])."""
    groups, cur = [], []
    for i, (w, s, e) in enumerate(words):
        brk = w.endswith("|")  # "word|" = end the phrase here; the | is not shown
        w = w.rstrip("|")
        cur.append((w, float(s), float(e)))
        gap = float(words[i + 1][1]) - float(e) if i + 1 < len(words) else 99
        if brk or len(cur) >= maxw or w[-1:] in ".,!?;:،؟" or gap > 0.35:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    events = []
    for g in groups:
        g_end = g[-1][2] + 0.08
        for k, (w, s, e) in enumerate(g):
            end = g[k + 1][1] if k + 1 < len(g) else g_end
            events.append((s, end, [(w2, j == k) for j, (w2, _, _) in enumerate(g)]))
    return events


CAP_BOX = 320  # height of a caption frame in pixels


def render_caption_track(words, W, cfg, rtl, dur, tmp):
    """Captions drawn by Chromium (correct Arabic shaping, same fonts as the cards).
    Returns a concat-demuxer list that plays the caption frames at the right times."""
    size = int(cfg.get("size", 80))
    outline = float(cfg.get("outline", 4))
    accent = cfg.get("accent", "#FFFFFF")
    css = CARD_CSS % {"fonts": FONT_DIR, "ar": AR_FONT_DIR, "W": W, "cw": int(W * 0.78), "accent": accent}
    css += ("body { padding: 0; height: %dpx; align-items: center; } "
            ".cap { max-width: %dpx; text-align: center; font-weight: 800; font-size: %dpx; line-height: 1.25; color: #fff; "
            "-webkit-text-stroke: %.1fpx #000; paint-order: stroke fill; text-shadow: 0 6px 16px rgba(0,0,0,.55); } "
            ".cap .hl { color: %s; }" % (CAP_BOX, int(W * 0.86), size, outline * 2, accent))
    def page(inner):
        return ('<html><head><meta charset="utf-8"><style>%s</style></head><body class="%s"><div id="c" class="cap">%s</div>'
                '</body></html>' % (css, "rtl" if rtl else "", inner))
    events = [(max(0.0, s), min(e, dur), parts) for s, e, parts in caption_events(words, int(cfg.get("max_words", 3)))]
    items = [{"html": page(""), "out": os.path.join(tmp, "cap_blank.png"), "box": CAP_BOX}]
    for i, (s, e, parts) in enumerate(events):
        inner = " ".join('<span class="hl">%s</span>' % esc(w) if hl else esc(w) for w, hl in parts)
        items.append({"html": page(inner), "out": os.path.join(tmp, "cap%03d.png" % i), "box": CAP_BOX})
    jobfile = os.path.join(tmp, "caps.json")
    with open(jobfile, "w") as f:
        json.dump({"width": W, "items": items}, f, ensure_ascii=False)
    script = os.path.join(tmp, "render_cards.js")
    with open(script, "w") as f:
        f.write(NODE_RENDER)
    run(["node", script, jobfile])
    blank = items[0]["out"]
    seq, t = [], 0.0
    for (s, e, _), it in zip(events, items[1:]):
        if s > t + 0.001:
            seq.append((blank, s - t))
        if e > s:
            seq.append((it["out"], e - max(s, t)))
            t = e
    if dur > t:
        seq.append((blank, dur - t))
    lst = os.path.join(tmp, "caps.txt")
    with open(lst, "w") as f:
        f.write("ffconcat version 1.0\n")
        for path, d in seq:
            f.write("file '%s'\nduration %.3f\n" % (path, max(d, 0.001)))
        f.write("file '%s'\n" % seq[-1][0])
    return lst


def build_captions(words, W, H, cfg, path, rtl=False):
    size = int(cfg.get("size", 74))
    y = float(cfg.get("y", 0.70))
    accent = ass_color(cfg.get("accent", "#FFFFFF"))
    maxw = int(cfg.get("max_words", 3))
    font = cfg.get("font", "Montserrat")
    outline = float(cfg.get("outline", 3))
    bold = -1 if font == "Montserrat" else 0
    encoding = -1 if rtl else 1  # -1 = libass detects right-to-left paragraphs (Arabic word order)
    lines = []
    for s, end, parts in caption_events(words, maxw):
        txt = [("{\\c%s}%s{\\c&H00FFFFFF}" % (accent, ass_esc(w)) if hl else ass_esc(w)) for w, hl in parts]
        lines.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,{\\an5\\pos(%d,%d)}%s"
                     % (ass_time(s), ass_time(end), W // 2, int(H * y), " ".join(txt)))
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,%s,%d,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,%d,0,0,0,100,100,0,0,1,%.1f,3,5,60,60,0,%d

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (W, H, font, size, bold, outline, encoding)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")


# ---------------------------------------------------------------- sound: a soft synthesized pop
def write_pop(path):
    sr, dur = 48000, 0.14
    n = int(sr * dur)
    frames = bytearray()
    for i in range(n):
        t = i / sr
        f = 900 - 500 * (t / dur)
        v = math.sin(2 * math.pi * f * t) * math.exp(-t * 32) * 0.55
        s = int(max(-1, min(1, v)) * 32767)
        frames += struct.pack("<hh", s, s)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(frames))


# ---------------------------------------------------------------- pass 2: zooms + cards + captions + audio
def build_final(plan, base, W, H, fps, tmp):
    dur, _ = probe(base)
    inputs = ["-i", base]
    fc = []

    # zoom segments (jump-cut punch-ins): piecewise constant scale, cut at each zoom time
    zooms = sorted(plan.get("zooms") or [{"t": 0, "scale": 1.0}], key=lambda z: z["t"])
    if zooms[0]["t"] > 0:
        zooms.insert(0, {"t": 0, "scale": 1.0})
    segs = []
    for i, z in enumerate(zooms):
        s = float(z["t"])
        e = float(zooms[i + 1]["t"]) if i + 1 < len(zooms) else dur
        if e - s < 0.05 or s >= dur:
            continue
        sc = max(1.0, float(z.get("scale", 1.0)))
        fy = float(z.get("focus_y", 0.42))
        sw, sh = int(round(W * sc / 2) * 2), int(round(H * sc / 2) * 2)
        cy = int(min(max(sh * fy - H / 2, 0), sh - H))
        fc.append("[0:v]trim=%.3f:%.3f,setpts=PTS-STARTPTS,scale=%d:%d,crop=%d:%d:%d:%d,setsar=1[z%d]"
                  % (s, min(e, dur), sw, sh, W, H, (sw - W) // 2, cy, i))
        segs.append("[z%d]" % i)
    fc.append("%sconcat=n=%d:v=1:a=0[vz]" % ("".join(segs), len(segs)))
    last = "vz"

    # cards
    cards = plan.get("cards") or []
    accent = (plan.get("captions") or {}).get("card_accent", "#F5C451")
    pngs = render_cards(cards, W, accent, tmp, bool(plan.get("rtl")))
    for png in pngs:
        inputs += ["-loop", "1", "-t", "%.3f" % dur, "-i", png]
    idxs = list(range(inputs.count("-i")))  # input 0 is the base video, then one per card
    for i, c in enumerate(cards):
        st, en = float(c["start"]), float(c["end"])
        ii = idxs[i + 1]
        y = int(H * float(c.get("y", 0.15)))
        fc.append("[%d:v]format=rgba,fade=t=in:st=%.3f:d=0.18:alpha=1,fade=t=out:st=%.3f:d=0.15:alpha=1[c%d]"
                  % (ii, st, max(st, en - 0.15), i))
        fc.append("[%s][c%d]overlay=x=(W-w)/2:y='if(lt(t,%.3f),%d+40*max(0,1-(t-%.3f)/0.22),%d)':"
                  "enable='between(t,%.3f,%.3f)'[v%d]" % (last, i, st + 0.22, y, st, y, st, en, i))
        last = "v%d" % i

    # captions
    words_path = plan.get("words")
    if words_path:
        with open(words_path, encoding="utf-8") as f:
            words = json.load(f)
        ccfg = plan.get("captions") or {}
        engine = ccfg.get("engine", "browser" if plan.get("rtl") else "ass")
    if words_path and engine == "browser":
        lst = render_caption_track(words, W, ccfg, bool(plan.get("rtl")), dur, tmp)
        ci = len(idxs)
        inputs += ["-f", "concat", "-safe", "0", "-i", lst]
        idxs.append(ci)
        fc.append("[%d:v]fps=%d,format=rgba[capv]" % (ci, fps))
        fc.append("[%s][capv]overlay=x=0:y=%d:eof_action=pass[vc]" % (last, int(H * float(ccfg.get("y", 0.7))) - CAP_BOX // 2))
        last = "vc"
    elif words_path:
        ass = os.path.join(tmp, "captions.ass")
        build_captions(words, W, H, plan.get("captions") or {}, ass, bool(plan.get("rtl")))
        fdir = os.path.join(tmp, "fonts")
        os.makedirs(fdir, exist_ok=True)
        for d in (FONT_DIR, AR_FONT_DIR):
            for fn in os.listdir(d):
                if fn.lower().endswith((".ttf", ".otf")) and not os.path.exists(os.path.join(fdir, fn)):
                    os.symlink(os.path.join(d, fn), os.path.join(fdir, fn))
        fc.append("[%s]subtitles=filename='%s':fontsdir='%s'[vc]" % (last, ass, fdir))
        last = "vc"
    fc.append("[%s]format=yuv420p[vout]" % last)

    # audio: base track (clips or voiceover) + music bed + pops
    audio = plan.get("audio", "clips")
    n_in = len(idxs)
    mix = []
    if audio == "clips":
        mix.append("[0:a]")
    elif audio:
        inputs += ["-i", audio]
        fc.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo[vo]" % n_in)
        n_in += 1
        mix.append("[vo]")
    if plan.get("music"):
        inputs += ["-stream_loop", "-1", "-i", plan["music"]]
        vol = float(plan.get("music_volume", 0.12))
        fc.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.3f,atrim=0:%.3f,"
                  "afade=t=out:st=%.3f:d=1.0[mus]" % (n_in, vol, dur, max(0, dur - 1.0)))
        n_in += 1
        mix.append("[mus]")
    if plan.get("sfx", True) and cards:
        pop = os.path.join(tmp, "pop.wav")
        write_pop(pop)
        inputs += ["-i", pop]
        fc.append("[%d:a]asplit=%d%s" % (n_in, len(cards), "".join("[p%d]" % i for i in range(len(cards)))))
        for i, c in enumerate(cards):
            ms = int(float(c["start"]) * 1000)
            fc.append("[p%d]adelay=%d|%d,volume=0.6[pd%d]" % (i, ms, ms, i))
            mix.append("[pd%d]" % i)
        n_in += 1
    if not mix:
        fc.append("anullsrc=r=48000:cl=stereo,atrim=0:%.3f[aout]" % dur)
    else:
        lufs = plan.get("loudness", -14)  # social-media loudness target; null keeps the original level
        norm = ",loudnorm=I=%s:TP=-1.5:LRA=11,aresample=48000" % lufs if lufs is not None else ""
        fc.append("%samix=inputs=%d:duration=first:normalize=0%s,alimiter=limit=0.89[aout]" % ("".join(mix), len(mix), norm))

    out = plan["output"]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    script = os.path.join(tmp, "graph.txt")
    with open(script, "w") as f:
        f.write(";\n".join(fc))
    run(["ffmpeg", "-y", "-v", "error"] + inputs +
        ["-filter_complex_script", script, "-map", "[vout]", "-map", "[aout]",
         "-r", str(fps), "-t", "%.3f" % dur,
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    return out, dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--keep-temp", action="store_true")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="reel-")
    try:
        with open(a.plan, encoding="utf-8") as f:
            plan = json.load(f)
        W, H = [int(x) for x in str(plan.get("size", "1080x1920")).lower().split("x")]
        fps = int(plan.get("fps", 30))
        if "output" not in plan:
            raise PlanError("plan needs an output path")
        base = build_base(plan, W, H, fps, tmp)
        out, dur = build_final(plan, base, W, H, fps, tmp)
        print(json.dumps({"ok": True, "output": out, "duration": round(dur, 2)}))
    except (PlanError, KeyError, ValueError, OSError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)
    finally:
        if a.keep_temp:
            print("temp kept at " + tmp, file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
