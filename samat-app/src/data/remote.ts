// Reads the live listings from samat-alsakan.com. Mirrors scripts/sync_listings.py.
// The listings are read from the website's app.js as JSON text; nothing from the website is executed.
import type { Listing, Purpose } from './types';

export const SITE = 'https://samat-alsakan.com';

interface SiteListing {
  id?: string;
  titleAr?: string;
  titleEn?: string;
  typeAr?: string;
  cityAr?: string;
  area?: string | number;
  price?: string | number;
  rooms?: string | number;
  bathrooms?: string | number;
  transaction?: string;
  descriptionAr?: string;
  detailsAr?: unknown[];
  image?: string;
}

export function extractListings(js: string): SiteListing[] {
  const m = js.match(/const FEATURED_PROPERTIES=(\[[\s\S]*?\]\)?);\s*\n/);
  if (!m) throw new Error('listings not found in app.js');
  const text = m[1]
    .replace(/\]\s*\.concat\(\[/g, ',')
    .replace(/\]\)$/, ']')
    .replace(/,\s*([\]}])/g, '$1');
  const data = JSON.parse(text);
  if (!Array.isArray(data)) throw new Error('listings are not a list');
  return data;
}

function num(v: unknown): number | null {
  const s = String(v ?? '').replace(/,/g, '').trim();
  return /^\d+(\.\d+)?$/.test(s) ? Number(s) : null;
}

function purposeOf(p: SiteListing): Purpose {
  if ((p.transaction ?? '') === 'rent') return 'rent';
  if ((p.titleAr ?? '').includes('مطلوب')) return 'wanted';
  return 'sale';
}

function locationOf(title: string): string {
  const m = title.match(/(?:في\s+)?(حي\s+[^–\-(،]+)/);
  if (m) return m[1].trim();
  const m2 = title.match(/(أبحر\s+(?:الشمالية|الجنوبية)|شرم أبحر|طريق المدينة|ريع بخش|الواجهة البحرية)/);
  return m2 ? m2[1] : '';
}

function imageUrl(path: string): string {
  if (/^https?:\/\//.test(path)) return path;
  return `${SITE}/${path.replace(/^\/+/, '').split('/').map(encodeURIComponent).join('/')}`;
}

/** Converts the website's listings to the app's format. Listings missing an id, title or image are skipped. */
export function toAppListings(raw: SiteListing[], ratios: Record<string, number> = {}): Listing[] {
  return raw
    .filter((p) => p && p.id && p.titleAr && p.image)
    .map((p, i) => {
      const price = num(p.price);
      const title = String(p.titleAr).trim();
      return {
        id: String(p.id),
        source: 'site' as const,
        order: i,
        title,
        titleEn: String(p.titleEn ?? '').trim(),
        type: String(p.typeAr ?? '').trim(),
        city: String(p.cityAr ?? '').trim(),
        location: locationOf(title),
        purpose: purposeOf(p),
        price,
        priceText: price === null ? String(p.price ?? '').trim() : '',
        area: num(p.area),
        rooms: num(p.rooms),
        baths: num(p.bathrooms),
        description: String(p.descriptionAr ?? '').trim(),
        details: (Array.isArray(p.detailsAr) ? p.detailsAr : []).map((d) => String(d).trim()).filter(Boolean),
        url: `${SITE}/property.html?id=${encodeURIComponent(String(p.id))}`,
        image: { uri: imageUrl(String(p.image)) },
        imageRatio: ratios[String(p.id)] ?? 0, // 0 = unknown; measured when shown
      };
    });
}

export async function fetchLiveListings(ratios: Record<string, number>): Promise<Listing[]> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 20000);
  try {
    const res = await fetch(`${SITE}/app.js?t=${Date.now()}`, { signal: ctrl.signal, cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const list = toAppListings(extractListings(await res.text()), ratios);
    if (!list.length) throw new Error('no listings');
    return list;
  } finally {
    clearTimeout(timer);
  }
}
