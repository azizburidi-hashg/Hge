import type { ImageSourcePropType } from 'react-native';

export type Purpose = 'sale' | 'rent' | 'wanted';

export interface Listing {
  id: string;
  source: 'site' | 'owner'; // from the website, or posted by the owner in the app
  order: number; // position (lower first)
  title: string;
  titleEn: string;
  type: string; // as written: أرض، فيلا، شقة، عمارة، فندق ...
  city: string;
  location: string; // district or area
  purpose: Purpose;
  price: number | null; // SAR; null = price on request, or see priceText
  priceText: string; // e.g. "7,000 ريال للمتر المربع"
  area: number | null; // m²
  rooms: number | null;
  baths: number | null;
  description: string;
  details: string[];
  url: string; // web page for the listing ('' when none)
  image: ImageSourcePropType; // cover
  imageRatio: number; // width / height; 0 = unknown
  gallery?: ImageSourcePropType[]; // all photos, cover first
  isOffer?: boolean;
  offerText?: string;
  oldPrice?: number | null;
  offerEnds?: string | null; // YYYY-MM-DD
}
