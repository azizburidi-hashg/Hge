# سمات السكن للاستثمار العقاري: brand brief for the marketing team

Every marketing agent reads this file first. The facts here come from `samat-app/src/config.ts` and samat-alsakan.com.
If anything changes, change it here and in `config.ts`. Agents must not invent facts that aren't in this file, in a listing, or given by the owner in chat.

## Who we are
- **Name:** سمات السكن للاستثمار العقاري (Samat Alsakan Real Estate Investment)
- **Tagline:** نقدم العقار بصورة تليق بقيمته، ونصنع لكل فرصة حضوراً يلفت الانتباه ويقود إلى القرار الصحيح.
- **Base:** Jeddah. Some listings in Makkah and Taif.
- **FAL license (رخصة فال):** 1100304235
- **Commercial registration (السجل التجاري):** 7052161564

## Contact (exactly as written, never changed)
- WhatsApp: +966 55 528 2922 (wa.me/966555282922). The local form 0555282922 (or 055 528 2922) is the same number and is fine in Saudi-facing posts.
- Phones: +966555282922, +966559955075
- Email: Sematalsakan@hotmail.com
- Website: https://samat-alsakan.com
- Map: https://maps.app.goo.gl/Evt2CyFEZKeCjdh99
- Instagram @samatalsakan · X @samatAlsakan · Snapchat samatalsakan · TikTok @samatalsakan · Telegram t.me/jeddah3qarat

## Look
- Navy `#00264D` (dark `#001A36`), gold `#C8A45D`, teal `#006D7A`, background `#F4F6F5`, text `#16363B`
- Logos: `samat-app/brand/` (`logo-navy.png`, `logo-transparent.png`, `mark-gold-transparent.png`, `mark.svg`)
- Feel: calm, premium, trustworthy. Navy and gold, plenty of space, real photos. No loud colors, no clip-art, no fake luxury stock that isn't the property.

## Voice
- Arabic first, in Saudi (Hijazi-friendly) white dialect for social and WhatsApp, in clear Modern Standard Arabic for the website, PDFs and formal posts. English only when asked or for investor-facing pieces.
- Confident, short, specific: location, area, price, why it's a good deal. No exaggeration ("أفضل فرصة في التاريخ"), no pressure tactics, no guaranteed returns.
- Always end with one clear call to action, usually WhatsApp.

## What we sell (from the current listings)
- Mostly **land (أرض)** for sale, then villas, apartments, buildings, hotels and a villa design service. Also "wanted" (مطلوب) requests.
- Strongest areas: North Obhur (أبحر الشمالية), South Obhur, Sharm Obhur, Al Shati, Al Fayhaa, the waterfront, plus Makkah and Taif.
- Listing data: live on samat-alsakan.com; the app's copy is in `samat-app/src/data/listings.generated.ts`; owner-posted listings and offers are in the Supabase `listings` table (see `samat-app/supabase/schema.sql`).

## Rules for every ad (Saudi real estate advertising)
- Every property ad shows the **FAL license number** and the listing's **REGA ad license number (رقم ترخيص الإعلان)** when the listing has one. If an ad needs an ad license number and we don't have it, the agent says so and leaves a clear placeholder `[رقم ترخيص الإعلان]`. It never makes one up.
- Price, area, location and features come only from the listing or the owner. "Price on request" stays "على السوم" / "السعر عند التواصل".
- No promised returns or yields unless the owner gives the numbers and their source; mark estimates as estimates.
- REGA rules change. Before a paid campaign, the compliance reviewer reminds the owner to check the current rules on rega.gov.sa.

## Hard limits (from CLAUDE.md, apply to every agent)
- Nothing is posted, sent, uploaded or boosted, and no money is spent, without the owner saying yes in chat for that specific item.
- No buying assets or starting paid AI-generation services without a yes and a price quote first.
- No messages to real leads or customers without approval. Agents draft; the owner sends.
