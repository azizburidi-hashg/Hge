# فريق التسويق - سمات السكن للاستثمار العقاري

You have a marketing director and 8 specialist agents. Open Claude in this folder and ask in Arabic or English. The director (`.claude/skills/marketing-team`) plans the work, gives it to the right people, and has every piece checked before you see it.

| Agent | What it does |
|---|---|
| market-researcher | Area prices (SAR/m²), demand, competing listings, with sources |
| buyer-strategist | Who the buyers are, the angle, the key message, channels |
| arabic-copywriter | Captions, hooks, ad copy, WhatsApp messages, listing descriptions |
| social-media-manager | 14-day posting calendar, times, weekly review |
| video-producer | Reel scripts, shot lists, 3D Blender shots (title, price reveal, map) |
| ads-manager | Paid ads plans and budget splits (never spends) |
| lead-handler | Reply scripts, follow-ups, lead tracking sheet |
| compliance-reviewer | Checks facts, prices, contact details, FAL and ad license |

## Try it
> سو لي حملة تسويقية كاملة لأرض أبحر الشمالية اللي في الموقع، الميزانية 3000 ريال لأسبوعين

> Make a full campaign for the North Obhur land listing, budget 3,000 SAR for two weeks.

> اكتب لي 5 كابشنات سناب لفيلا حي الشاطئ

> كم سعر المتر في حي الفيحاء؟ وهل سعر إعلاننا مناسب؟

> Plan this week's posts across all our accounts.

> عميل أرسل: "كم آخر سعر للأرض؟" اكتب لي الرد

Every job goes in `marketing/campaigns/<date>-<name>/`, with a `README.md` that says what's ready and what needs your OK.

## The rules the team follows
- Nothing is posted, sent, boosted or paid for until you say yes in chat.
- No facts are made up: prices, areas and districts come from your listings. Market numbers come with sources.
- Every property ad carries FAL 1100304235 and the ad license number. If it doesn't have that number yet, it shows `[رقم ترخيص الإعلان]` for you to fill in.
- Company details, colors and voice are in `marketing/BRAND.md`. Edit that file when something changes.
