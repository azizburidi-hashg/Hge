// Listings come from samat-alsakan.com via scripts/sync_listings.py (see listings.generated.ts).
import { LISTINGS } from './listings.generated';
import type { Listing, Purpose } from './types';

export { LISTINGS };
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
export const TYPES = byCount(LISTINGS.map((l) => l.type));
export const CITIES = byCount(LISTINGS.map((l) => l.city));
export const PURPOSES = (['sale', 'rent', 'wanted'] as Purpose[]).filter((p) => LISTINGS.some((l) => l.purpose === p));

const fmt = (n: number) => n.toLocaleString('en-US', { maximumFractionDigits: 2 });

export function formatPrice(l: Listing): string {
  if (l.price !== null) return `${fmt(l.price)} ريال${l.purpose === 'rent' ? ' / سنوياً' : ''}`;
  if (l.priceText) return l.priceText;
  return l.purpose === 'wanted' ? 'طلب شراء' : 'السعر عند الطلب';
}

export const formatArea = (a: number) => `${fmt(a)} م²`;

export function place(l: Listing): string {
  return [l.location, l.city].filter(Boolean).join('، ');
}
