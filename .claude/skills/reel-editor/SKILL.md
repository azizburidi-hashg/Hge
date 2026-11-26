---
name: reel-editor
description: Personal reel editor. The user sends any video (talking head, drone footage, property clips, phone recording) or property photos plus facts, and Claude returns a finished 9:16 Instagram/TikTok reel in the user's saved style - jump-cut punch-ins, word-by-word captions, glass info cards (price, size, location), step pill, pops, music and a comment-keyword CTA. Use when the user sends a video to edit, says "edit this", "make it like that", "make a reel", "daily drone video", "add captions", or sends a reference reel whose editing they want copied.
---

# Reel editor

The user wants to send a video and get it back edited "like that". Default style: `references/STYLE-POWER-EXPLAINER.md` (read it first). If the user sends a NEW reference reel, study it (below) and save a new `references/STYLE-<NAME>.md` next to it; use it as the default only when the user says so.

## Ground rules (from the project's CLAUDE.md, they win)
- **Credits = money.** Before any paid call (Higgsfield video/voice, vidIQ watch, Shorty, OpusClip) say what it costs and get a yes, unless the user already approved that exact step. Quote first with `estimate_video_cost` / `estimate_audio_cost`. Free: Higgsfield voice previews (`list_voices` preview_url), balances, this script.
- **Never post or upload** to Instagram/TikTok/anywhere without a yes in chat for that video.
- **Facts only from the user.** Price, size, bedrooms, location, claims: exactly as given. Missing → ask. No invented stats, logos or "illustrative" numbers.
- Work goes in `shots/<short-name>/` (plan.json, words.json, stills, `<short-name>.mp4`). Quote paths.
- Ask before installing anything new (e.g. faster-whisper for word timings).

## Workflow
1. **Get the material.** Video file(s) attached in chat, or property photos + facts. Copy into `shots/<name>/`. Probe length with ffprobe.
   - Photos only → offer drone-style clips via Higgsfield (`kling3_0` mode pro ≈ 8.75 credits / 5 s clip; `seedance_2_5` 720p ≈ 35). Quote, get a yes, then generate.
2. **Words + timings** (`words.json` = `[["word", start, end], ...]`):
   - The user's own speech → `python .claude/skills/blender-shots/scripts/voice_timing.py align --audio "<file>" --out "shots/<name>"` (needs faster-whisper; ask before installing).
   - No speech yet → write the script from the user's facts, show it (free), then after a yes make the voiceover with Higgsfield `text2speech_v2` (variant `elevenlabs`, ≈0.6 credits per 25 words) with the voice the user picked; time words with `align` on that file, or `voice_timing.py even` for a rough plan.
3. **Plan** `shots/<name>/plan.json` (format in the docstring of `scripts/build_reel.py`):
   - zooms every 1.5–3 s on phrase boundaries (never mid-word);
   - each card's `start` = the start time of the word it illustrates;
   - pill per section, CTA card in the last 4–5 s;
   - music only if the user supplied a track or approved generating one.
4. **Stills first.** Render, then pull 3–4 frames at moments with cards (`ffmpeg -ss T -i out.mp4 -frames:v 1 ...`), hstack them, LOOK at them. Fix overlaps, text over faces, typos.
5. **Deliver.** Send the mp4 with SendUserFile. Say what you checked by eye (the stills), by machine (length, size), and what is unverified (e.g. audio mix not listened to).
6. Only if the user says so: post via vidIQ (`vidiq_instagram_publish_reel`) or draft a caption + hashtags.

Render: `python .claude/skills/reel-editor/scripts/build_reel.py --plan "shots/<name>/plan.json"`

## Studying a new reference reel
`vidiq_watch_shortform_content` with the reel URL (10 vidIQ credits; ask first) and a prompt asking for: cut rhythm, zoom pattern, caption font/position/highlight, every overlay's look and timing, SFX, music, hook, CTA. Write the style card in the same table format as the default. Copy grammar, never content.

## Card types (build_reel.py)
`pill` (text) · `card` (title + rows) · `stat` (value + label) · `cta` (keyword + note). Arabic is UNTESTED: Montserrat has no Arabic letters, so cards and captions fall back to whatever system font exists. For Arabic, add an Arabic font to the fonts folder first and check a still.
