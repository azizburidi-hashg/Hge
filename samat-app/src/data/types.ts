import type { ImageSourcePropType } from 'react-native';

export type Purpose = 'sale' | 'rent' | 'wanted';

export interface Listing {
  id: string;
  order: number; // position on the website (newest additions are last)
  title: string;
  titleEn: string;
  type: string; // as written on the website: أرض، فيلا، شقة، عمارة، فندق ...
  city: string;
  location: string; // district or area, when the title names one
  purpose: Purpose;
  price: number | null; // SAR; null = price on request, or see priceText
  priceText: string; // e.g. "7,000 ريال للمتر المربع"
  area: number | null; // m²
  rooms: number | null;
  baths: number | null;
  description: string;
  details: string[];
  url: string; // the listing on samat-alsakan.com
  image: ImageSourcePropType;
  imageRatio: number; // width / height
}
