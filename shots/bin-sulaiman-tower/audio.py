#!/usr/bin/env python3
"""Soundtrack for bin-sulaiman-tower: cleaned voice + light synthesized SFX, loudness-normalized.

    python shots/bin-sulaiman-tower/audio.py

Writes final_audio.wav next to this file (48 kHz stereo, -14 LUFS integrated, -1.5 dBTP).
"""
import json, os, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
U = "/root/.claude/uploads/999ee3d3-348d-5550-a2bd-b38465d36af0/"
FACE = U + "34d6d11a-copy_C4652030-4B84-4704-B5D7-554DE7948489_compressed_by_happyscribe.com.mov"
SR = 48000
DUR = 875 / 30.0

# cuts into b-roll / photos get a soft whoosh; graphics get a pop; the name gets a low hit
WHOOSH = [5.72, 8.74, 16.34, 19.46, 24.42]
POPS = [0.03, 10.46, 17.08, 24.49, 25.98, 27.92]
IMPACT = [22.64]


def voice():
    cmd = ["nice", "-n", "10", "ffmpeg", "-v", "error", "-i", FACE, "-vn", "-ac", "1", "-ar", str(SR),
           "-af", "highpass=f=80,lowpass=f=15000,"
                  "acompressor=threshold=-21dB:ratio=3:attack=5:release=120:makeup=3dB",
           "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, check=True, capture_output=True).stdout, dtype=np.float32).copy()
    n = int(round(DUR * SR))
    return np.pad(a, (0, max(0, n - len(a))))[:n]


def biquad_bp(x, f_start, f_end, q=1.2):
    """Band-pass with a centre frequency that sweeps from f_start to f_end (log)."""
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    n = len(x)
    for i in range(n):
        f = f_start * (f_end / f_start) ** (i / n)
        w0 = 2 * np.pi * f / SR
        alpha = np.sin(w0) / (2 * q)
        b0, b2 = alpha, -alpha
        a0, a1, a2 = 1 + alpha, -2 * np.cos(w0), 1 - alpha
        yi = (b0 * x[i] + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1 = x1, x[i]
        y2, y1 = y1, yi
        y[i] = yi
    return y


def whoosh(rng):
    n = int(0.55 * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    sw = biquad_bp(noise, 350, 2800)
    env = np.where(t < 0.62, np.sin(np.pi / 2 * t / 0.62) ** 2, np.exp(-(t - 0.62) / 0.09))
    out = sw * env
    return out / (np.abs(out).max() + 1e-9), int(0.62 * n)   # peak lands on the cut


def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 420 + 800 * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.sin(ph) * np.exp(-t / 0.022)
    return out / np.abs(out).max(), 0


def impact(rng):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    low = np.sin(2 * np.pi * (48 + 30 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.28)
    nz = rng.standard_normal(n)
    lp = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc += 0.03 * (nz[i] - acc)
        lp[i] = acc
    body = lp / (np.abs(lp).max() + 1e-9) * np.exp(-t / 0.09)
    out = low + 0.6 * body
    return out / np.abs(out).max(), 0


def place(track, snd, t, gain, anchor):
    s = int(round(t * SR)) - anchor
    a, b = max(0, s), min(len(track), s + len(snd))
    if b > a:
        track[a:b] += gain * snd[a - s:b - s]


def loudnorm(src, dst):
    base = ["nice", "-n", "10", "ffmpeg", "-v", "info", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", src]
    meas = subprocess.run(base + ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True)
    m = json.loads(re.findall(r"\{[^{}]+\}", meas.stderr)[-1])
    af = ("loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(base[:5] + ["error"] + base[6:] + ["-af", af, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", "-y", dst],
                   check=True)
    return m


def main():
    rng = np.random.default_rng(7)
    v = voice()
    peak = np.percentile(np.abs(v), 99.9)
    mix = v.copy()
    for t in WHOOSH:
        s, anc = whoosh(rng)
        place(mix, s, t, 0.16 * peak, anc)
    for t in POPS:
        s, anc = pop()
        place(mix, s, t, 0.20 * peak, anc)
    for t in IMPACT:
        s, anc = impact(rng)
        place(mix, s, t, 0.42 * peak, anc)
    raw = os.path.join(HERE, "mix.f32")
    mix.astype(np.float32).tofile(raw)
    m = loudnorm(raw, os.path.join(HERE, "final_audio.wav"))
    os.remove(raw)
    print("voice+sfx measured", m["input_i"], "LUFS ->", "final_audio.wav at -14 LUFS")


if __name__ == "__main__":
    main()
