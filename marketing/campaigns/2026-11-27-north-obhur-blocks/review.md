# Compliance review: بلوك 32 وبلوك 35، منطقة عمائر أبحر الشمالية

Reviewer: compliance reviewer, 2026-11-27. Files read: `../../BRAND.md`, `listing.md` (source of truth), `research.md`, `strategy.md`, `copy.md` (all sections, including section 12), `video-plan.md`, `leads.md`, `leads.csv`, `calendar.md`, `calendar.csv`, `weekly-review.md`, and both flyer images (I looked at them).
I did not edit any other file.

**How I checked.** By eye: every price, area, plot range and street fact in every piece against `listing.md`, both flyers, all calendar rows. By hand: the arithmetic and the X character counts (there is no counting tool here, so treat my counts as ±2). By search: every phone, WhatsApp, handle, FAL and CR string in the folder, and every total (46.2M / 25.7M). **Not verified:** the Bayut, Raghdan, Sabq, Al-Madina, Al-Ain and ZATCA links in `research.md` (I did not open them), prayer times, and the current REGA rules.

**Already raised with the owner (not repeated below as a new finding):** the Block 32 flyer shows plot 228 twice, omits 220 to 222, and labels the north street "شارع عرض 32 متر / الشمالي", while the listing says four 20 m streets. Gate C00b covers it.

---

## Checks that passed

- **Arithmetic.** 14,012.13 × 3,300 = 46,240,029 SAR (≈46.2M). 7,800 × 3,300 = 25,740,000 SAR (≈25.7M). Plots 212 to 229 are 18 numbers and 250 to 261 are 12. The research per-m² figures check out: 2,233,800 / 620.5 = 3,600; 1,782,000 / 405 ≈ 4,400; 1,762,200 / 400 ≈ 4,406; 1,050,000 / 312 ≈ 3,365; 11,000,000 / 1,838 ≈ 5,985. The 5-ad median is 3,600, and 3,300 is about 8% below it.
- **Totals stay private.** They appear only in `copy.md` REPLY-PRICE (l.392-393), `leads.md` (l.45, 105, 130), and internal planning text (`research.md`, `strategy.md`, `video-plan.md` "not allowed"). None is in a public piece.
- **Free and organic.** There is no paid, boosted or sponsored row in `calendar.md` or `calendar.csv`. Every row's status is `needs owner OK`. Nothing is marked posted, sent or paid. `leads.csv` holds only the header (no personal data).
- **X lengths, counted with links = 23 and `wa.me/…` = 23.** All are ≤280. X-1 261, X-2 257, X-3 267 (after the marker is removed), X-4 ≈254, X-1V ≈261, X-2V ≈261, X-3V 253, TRUST-1/X ≈206.

---

## Must fix

| # | File / line or label | Problem | Fix |
|---|---|---|---|
| M1 | `copy.md` TT-3 (l.90), SNAP-3 (l.59), IG-ST-3 (l.158) | Each of these pieces covers **both** blocks but has only **one** `[رقم ترخيص الإعلان]`. SNAP-3 has a note under it (l.62), but the text itself was not changed. IG-ST-3 and TT-3 have no note at all. TT-3 is also the caption for C17, C25, C26, C46, C47, C54/55 (fallback), C64 and C65. | In the text itself, write `ترخيص الإعلان: بلوك 32 [رقم ترخيص الإعلان] · بلوك 35 [رقم ترخيص الإعلان]`, as WA-BCAST-2 and X-4 already do. |
| M2 | `calendar.md` l.11, l.18, C28 (l.56), C33 (l.61), C42 (l.75), C52 (l.85), C54 (l.87), C55 (l.88), C59 (l.92), C60 (l.93), C61 (l.94). The same rows in `calendar.csv` (l.33, 38, 47, 57, 59, 60, 64, 65, 66) | The caption IDs don't match `copy.md`. The calendar still says TRUST-1, the "VIDEO-2 caption" and X-4 are "not in copy.md yet", but they exist (copy.md §12). The Video 2 caption's ID is `VID2-CAP`, not "VIDEO-2 caption". C33, C42 and C52 still say "X-1/X-2/X-3 (repeat, new media)", but copy.md wrote X-1V, X-2V and X-3V for exactly those rows. | Set C33 → X-1V, C42 → X-2V, C52 → X-3V (and drop the C00c Bayut gate from C52, because X-3V has no comparison line). Set C54/C55 → VID2-CAP, and C28/C59/C60 → TRUST-1 / Story. Set C61 → X-4. Remove the "not in copy.md yet" text and the "copy" blockers. Update l.11 and l.18 in both files. |
| M3 | Both flyers (`amar-block-32-north-obhur.jpg`, `amar-block-35-north-obhur.jpg`). They are the main asset in most rows (C01-C22, C27, C34, C39, C44, C45, C51, C58, C63, C67, C68, C71) | (a) The aerial backgrounds aren't the site (generic villa district / sea bay and skyline) and carry no «صورة توضيحية» label. Only C17 and the videos add one. Every static use (status, Snapchat, IG carousel, X, GBP, portals, WhatsApp outreach, Telegram) shows them unlabeled. (b) Both plans draw a **mosque (مسجد)** next to the block, which isn't in the listing. (c) The plans print plot edge figures (25 / 20 / 30). Read as metres, 18 × 25×20 = 9,000 m² against 14,012.13, and 12 × 500 = 6,000 against 7,800. That implies individual plot sizes the listing says are unknown, and the sizes don't match the stated areas. (d) No REGA ad license number on the image. (e) The brand name is misspelled «للإستثمار» (should be «للاستثمار»). The phone is printed as «055 528 2922», which isn't a BRAND.md format. | The owner's designer reissues both flyers with: «صورة توضيحية» on the aerial and «مخطط توضيحي» on the plan; the mosque removed unless the owner confirms it; the edge figures removed or confirmed; the ad license number per block; «للاستثمار»; and `+966 55 528 2922`. This is together with the known Block 32 plot and street fix. Until then, no row uses a flyer without the labels overlaid. Add a gate "C00e: flyers relabelled" or extend C00b to the Block 35 flyer. |
| M4 | `copy.md` SNAP-1 l.44, SNAP-2 l.52, SNAP-3 l.60, TRUST-1 note l.541. `calendar.md`/`.csv` CTA column of C10, C22, C29, C37, C48, C56, C59, C69 | The contact is written `0555282922`. BRAND.md says "exactly as written, never changed", and it lists only `+966 55 528 2922`, `+966555282922` and `wa.me/966555282922`. The digits are right, but the format isn't in BRAND.md. | Use `واتساب +966 55 528 2922`. Or, if the owner wants the local format on Snapchat, he says so and `0555282922` is added to BRAND.md first. |
| M5 | `research.md` l.28, l.47, l.42/l.78 | Numbers with no source: **3,800** ريال/م² (Jan 2025 range; the only sources listed are 3,900 and 4,000), **2,500** ريال/م² ("إعلانات قديمة 2,100 إلى 2,500"; only the 2,100 ad is sourced), and the waterfront item's **November 2024** date. Line 78 says "يجب التحقق من الرابط الأصلي" and gives no URL. | Add the URL for each number, or delete the number. 3,800 → "3,900 إلى 4,000". Drop "2,500" or source it. Give the waterfront news URL or remove the item. |
| M6 | `leads.md` l.148 (reply to "فيه مخططات قريبة بـ 2,100 أو 2,500") | It gives the buyer "إعلانات 2026 … كانت من 3,365 وفوق" with **no** item-18 gate, unlike the "السعر غالي" reply at l.145. Also, two of the ads behind that range (Bayut 88127344 and 88127349) have no visible date (`research.md` l.58-59), so "2026" is not supported. | Add "(بند 18: لا تُرسل قبل التحقق من روابط Bayut)". Change "إعلانات 2026" to "إعلانات حديثة". Make the same date wording change at l.142, in `research.md` l.27 and l.64, and in `strategy.md` l.31. |
| M7 | `leads.md` l.172 (flood reply) | It says "أمانة جدة عندها مشاريع تصريف أمطار في أحياء أبحر الشمالية". The source (`research.md` l.40) names الفردوس، الصواري، الياقوت، الشراع, which are separate districts with an outfall at شرم أبحر, not districts of North Obhur. | "أمانة جدة عندها مشاريع تصريف أمطار في أحياء شمال جدة، ومصبّها في شرم أبحر". Keep the rest. |
| M8 | `leads.md` l.237 (follow-up day 3) | It sends a Block 32 lead the Prince Mishaal bin Majed Road news and Jeddah Tower. `research.md` §7.6 says the infrastructure points are used "فقط إذا أكد المالك قرب البلوكين منها". Sending them in a block follow-up implies the blocks benefit. | Gate it: use the road line only after the owner confirms proximity (leads.md item 6). Until then, the day-3 message is the district line only ("أبحر الشمالية فيها مشروع برج جدة ومدينة جدة الاقتصادية") plus the offer of details. |
| M9 | `video-plan.md` l.31 (facts table) and Video 2 shot 3 VO (l.96) | "مناسبة للتطوير العقاري" is applied to **both** blocks. The listing says it only for Block 32. Block 35's listing says "أراضٍ سكنية" and "موقع مميز". Video 2 is public and covers both blocks. | VO: «داخل منطقة عمائر أبحر الشمالية.» On-screen: drop «مناسبة للتطوير العقاري». Mark the table row "(Block 32 only)". The same correction applies to `leads.md` l.167 when the buyer asks about Block 35. |
| M10 | `copy.md` IG-2 (l.120). `calendar` C14 leaves the choice open | "والمساحة تكفي مشروع عمائر كامل في مكان واحد" claims a development capacity for Block 35 that the listing doesn't state, given that floors and zoning are unknown. | Use the stricter line by default: "والمساحة نحو 7,800 م² في مكان واحد". Revert only if the owner confirms. |
| M11 | `copy.md` IG-1 l.104 ("أرض واحدة متصلة") and PORTAL-32 l.424 ("في بلوك واحد متصل") | "متصل/متصلة" isn't in the listing. For Block 32 it is exactly what the open flyer question (220 to 222 missing) puts in doubt. | Remove the word until C00b is resolved: "بلوك 32 كامل … تحيط به أربعة شوارع" / "يضم قطع الأراضي من رقم 212 إلى 229." |

---

## Should fix

| # | File / line or label | Problem | Fix |
|---|---|---|---|
| S1 | `copy.md` l.196 (X-3 fallback) and l.543 (TRUST-1/X) | The counts are off. The fallback line is about 45 characters, not 41, so the post comes to about 243, not 239. TRUST-1/X is about 206, not about 190. Both are still under 280. Also, X-3 **with** the `[check sources first]` marker is about 289, which is over the limit if anyone forgets to delete it. | Correct the stated counts. Add "the marker must be deleted, it pushes the post over 280". |
| S2 | `copy.md` §1 hooks (l.25, 27, 28, 30) | Word counts are wrong: HOOK-5 has 7 words (not 6), HOOK-7 has 7 (not 6), HOOK-8 has 5 (not 4), HOOK-10 has 5 (not 4). All are still under 8. | Correct the Words column. |
| S3 | `copy.md` IG-1 l.111, IG-2 l.127; GBP-32/35 (button "Learn more" plus the WhatsApp line); X-1/X-2 (page URL plus wa.me) | Two calls to action in one piece (link in bio or page, **and** WhatsApp). BRAND.md asks for one clear CTA. | IG: delete "التفاصيل: الرابط في البايو". GBP: set the button to "Call now" (or no button) and keep the WhatsApp line. X: keep the page link as information but make wa.me the only instruction ("راسلنا"), or drop the page URL. |
| S4 | `copy.md` REPLY-PRICE l.395 | It covers both blocks but has a single placeholder. | `ترخيص الإعلان: بلوك 32 [..] · بلوك 35 [..]`, or send only the asked block's line. |
| S5 | `copy.md` PORTAL-35 l.444 ("متصل"), HOOK-8 l.28 ("أرض كبيرة متصلة") | The same "connected" wording as M11, but lower risk for Block 35. | Drop "متصل" or get the owner's OK. |
| S6 | `calendar` C43 (md l.76, csv l.48) and C29 (md l.57, csv l.34) | C43 can carry "Video 1 full", and C29's fallback is "both photos". Both include the Block 32 flyer, but neither row lists C00b. | Add C00b to both. |
| S7 | `copy.md` TRUST-1 / X (l.543), WEB-32/WEB-35 (§11) | There is no calendar row for TRUST-1/X. The website text replacements have no row or approval step, and editing the live site is an outward action. | Add a row for each (or drop TRUST-1/X), status `needs owner OK`. |
| S8 | `video-plan.md` l.38-42, l.66, l.89, l.110 | Stale. It says "copy.md doesn't exist yet" and names "Video 1/2/3 caption" sections that copy.md doesn't have. | Point to TT-1/TT-2/TT-3 (Video 1 and its cuts), VID2-CAP (Video 2) and TT-3 (Video 3), as copy.md §12 and the calendar do. |
| S9 | `video-plan.md` Video 1 shot 6 (l.75) | It says the zoom ends "with … the four street labels visible". The Block 35 plan labels only the north and south widths: west reads "شارع" with no width, and east has no label. | "ending with plots 250 to 261 visible". The four-streets fact comes from the on-screen text. |
| S10 | `video-plan.md` VO l.73 and l.97 | "تحيط فيه أربعة شوارع". | "تحيط به أربعة شوارع". |
| S11 | `copy.md` WA-DEV-2 / Wave 1 (l.272), sent at 13:15 (C01) | "مساء الخير" at 13:15 reads off in Saudi usage. The same issue applies to `leads.md` day-1 "مساء الخير" and day-3 "صباح الخير", which are used at 13:30 in C57 and C62. | Use "السلام عليكم" or "هلا [الاسم]", which work at any hour. |
| S12 | `copy.md` IG-ST-1/2/3 (l.143, 151, 159), X-3 / WA-INV-1 markers | Production notes sit inside the copy blocks ("[link sticker: …]", "[check sources first]"). | Move them outside the code block, or tell the owner to strip them before posting. |
| S13 | `copy.md` l.3 and l.7 | l.3 says "Every fact below is copied from the listing", but the Jeddah Tower line comes from research. l.7 says totals appear "in one place only", but `leads.md` also has them (privately). | Reword both lines to match. |
| S14 | Block 32 flyer headline | It's spelled «بلك», while every other piece says «بلوك». | «بلوك», in the reissue (M3). |
| S15 | `research.md` l.39, l.45-52 | The research is fine for internal use, but most of it comes from search snippets. | Open every link before any number is used publicly (the file already says this, and the owner should actually do it). |

---

## Looks good

- Every price (3,300 ريال/م²), area (نحو 14,012.13 م² / نحو 7,800 م²), plot range (212 to 229 / 250 to 261) and street fact (four 20 m streets, with Block 35's N/W/E/S breakdown) in copy.md, video-plan.md, leads.md and calendar hooks matches `listing.md`. In leads.md, "نحو 14,012 م²" is an acceptable rounding in private chat.
- FAL `1100304235` appears on every property piece in copy.md, on every video end card, and on the TRUST pieces. CR `7052161564` matches BRAND.md.
- `[رقم ترخيص الإعلان]` appears on every property piece, never with an invented number. Gate C00 blocks every property row until the real numbers arrive.
- Contacts: `+966 55 528 2922`, `wa.me/966555282922`, `@samatAlsakan`, `@samatalsakan`, `samatalsakan`, `t.me/jeddah3qarat`, `https://samat-alsakan.com/...` and the office map link all match BRAND.md character for character. The only exception is the local format in M4.
- No guaranteed returns, no "أقل من سعر السوق", no scarcity, deadlines or "آخر فرصة", no "official/government" wording. The comparison line is limited to X-3 and WA-INV-1, is gated, and has fallbacks. X-3V deliberately leaves it out.
- None of the claims the owner hasn't confirmed appear in public copy: floors, deed, single plots, distances, opening dates, the mosque, or who pays tax. leads.md answers each of these with "أتأكد لك وأرد عليك", tied to a numbered owner item.
- Jeddah Tower and Jeddah Economic City are mentioned as district context only, with no distance, date or "قريب".
- video-plan.md: labels for illustrations and diagrams, no AI voice or footage, no paid tools, Blender requests that follow the kit rules (stills first, runner only, 1 sample), and no invented map route.
- strategy.md: a clear, measurable goal, sensible buyer focus, and a strict "what not to say" list.
- weekly-review.md: lead-based metrics, and "no boosting" is stated twice.
- Arabic is natural Saudi white dialect for social and WhatsApp, and clean MSA for portals, GBP and the website. Right-to-left layout is fine: numbers and parentheses read correctly and URLs sit on their own lines.
- Look and feel: navy and gold text cards, a calm voice, no loud claims.

---

## Placeholders the owner must fill

- `[رقم ترخيص الإعلان]`: **Block 32** and **Block 35**, each separately. This applies to copy.md (every property piece), video end cards, 3D-6 (third line), flyers (M3), and the leads.md reply at l.222.
- `[الاسم]`, `[اسم المرسل]` (copy.md §7); `[اسم المتصل]`, `[اليوم]`, `[الوقت]`, `[اليوم والتاريخ]`, `[رابط موقع البلوك المؤكد من المالك]`, `[الاسم]، جواله [الرقم]`, `[البند …]: [الجواب المؤكد]`, `[صورة …]` / `[أرسل صورة البلوك من المجلد]` (leads.md).
- `[check sources first]` in X-3 and WA-INV-1: delete it after the Bayut check, or use the fallback line.
- `[رابط التحقق]`: the optional FAL verification line in TRUST-1/X, only if the owner gives the link.
- `<full path …>` in the 3D requests, and the `[owner footage]` shots in Video 2.
- Owner answers: broker cooperation, the location pin, visit times, the mosque, whether single plots are sold, deed, floors, plot sizes, and leads.md items 1-18.

## Outward actions that need the owner's yes (one by one, in chat)

Every calendar row C01-C71 except the review and task rows. That covers outreach waves 1 and 2, both broadcasts, status posts, X posts and the X-1 pin, IG posts and highlights, Snapchat, TikTok, Telegram, both portal listings, both GBP posts, and any change to the live website text (WEB-32/35). It also covers each finished video before posting, and any paid tool (none is planned; a price quote comes first). Nothing in this folder has been posted, sent or paid for.

## Regulatory reminder

REGA's advertising rules apply to organic posts as well as paid ones. Before anything is published, and before any paid ad in future, the owner should check the current REGA advertising rules on **rega.gov.sa**. In particular: that each block's ad license number has been issued; how it must be shown on images, video and portal listings (including whether a QR code or license barcode is required on the visual); and whether "صورة توضيحية" visuals are acceptable on the portals.

---

**Verdict: not ready.** The ad license numbers are missing (gate C00), the flyers need reissuing (M3, plus the known Block 32 errors), and M1, M2 and M4-M11 need fixing in the files.

---
## Fixes applied after this review (2026-11-27, marketing director)
- M1: TT-3, SNAP-3, IG-ST-3 now carry both blocks' license placeholders in the text.
- M2: calendar.md/.csv now use X-1V/X-2V/X-3V, VID2-CAP, TRUST-1, X-4; stale "not in copy.md" notes removed; C29 and C43 gated on C00b; C52 Bayut gate removed.
- M3: flyers not editable here. Gate C00b now covers both flyers (illustration label, mosque, ad license, «للاستثمار» spelling). Owner must reissue.
- M4: BRAND.md now allows the local form 0555282922 (same number, as on the company's own flyers).
- M5: unsourced 3,800, 2,500 and Nov 2024 items marked "not to be used" in research.md.
- M6: "2026" → "recent" wording; both leads.md price replies gated on the Bayut check.
- M7: drainage → «أحياء شمال جدة». M8: road line gated on owner confirmation.
- M9: «مناسبة للتطوير العقاري» removed from Block 35 / both-block use (video-plan.md, leads.md).
- M10: IG-2 uses the strict line. M11: «متصل/متصلة» removed (IG-1, PORTAL-32, PORTAL-35, HOOK-8).
- Should-fix items were not changed.
