// The listings built into the app (from scripts/sync_listings.py). They are only shown on first launch until the
// live listings arrive from samat-alsakan.com, or when the phone has never been online; see store.tsx.
import { LISTINGS as BUNDLED_LISTINGS } from './listings.generated';
import type { Listing, Purpose } from './types';

export { BUNDLED_LISTINGS };
export type { Listing, Purpose };

export const PURPOSE_LABEL: Record<Purpose, string> = { sale: 'للبيع', rent: 'للإيجار', wanted: 'مطلوب' };

const ICONS: Record<string, string> = {
  'أرض': '📐', 'فيلا': '🏡', 'شقة': '🏢', 'عمارة': '🏬', 'فندق': '🏨', 'تصميم فيلا': '✏️',
};
export const typeIcon = (t: string) => ICONS[t] ?? '🏠';

const byCount = (values: string[]) => {
  const n = new Map<string, number>();
  values.filter(Boolean).forEach((v) => n.set(v, (n.get(v) ?? 0) + 1));
  return [...n.entries()].sort((a, b) => b[1] - a[1]).map(([v]) => v);
};

/** Filter options built from whatever listings are current. */
export function derive(listings: Listing[]) {
  return {
    types: byCount(listings.map((l) => l.type)),
    cities: byCount(listings.map((l) => l.city)),
    purposes: (['sale', 'rent', 'wanted'] as Purpose[]).filter((p) => listings.some((l) => l.purpose === p)),
  };
}

const fmt = (n: number) => n.toLocaleString('en-US', { maximumFractionDigits: 2 });

export function formatPrice(l: Listing): string {
  if (l.price !== null) return `${fmt(l.price)} ريال${l.purpose === 'rent' ? ' / سنوياً' : ''}`;
  if (l.priceText) return l.priceText;
  return l.purpose === 'wanted' ? 'طلب شراء' : 'السعر عند الطلب';
}

export const formatOldPrice = (l: Listing) => (l.isOffer && l.oldPrice ? `${fmt(l.oldPrice)} ريال` : '');

export const formatArea = (a: number) => `${fmt(a)} م²`;

export function place(l: Listing): string {
  return [l.location, l.city].filter(Boolean).join('، ');
}
