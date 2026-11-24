// SAMPLE DATA ONLY. These listings are made up so the app can be tried out.
// Replace them with your real listings (or connect the app to your website) before publishing.

export type Purpose = 'sale' | 'rent';
export type PropertyType = 'apartment' | 'villa' | 'land' | 'floor' | 'commercial';

export interface Listing {
  id: string;
  title: string;
  purpose: Purpose;
  type: PropertyType;
  district: string;
  price: number; // SAR (for rent: per year)
  area: number; // m²
  rooms?: number;
  baths?: number;
  ageYears?: number;
  streetWidth?: number; // m
  facing?: string;
  description: string;
  featured?: boolean;
  addedDaysAgo: number;
  hue: number; // placeholder photo colour until real photos are added
}

export const PURPOSE_LABEL: Record<Purpose, string> = { sale: 'للبيع', rent: 'للإيجار' };

export const TYPE_LABEL: Record<PropertyType, string> = {
  apartment: 'شقة',
  villa: 'فيلا',
  land: 'أرض',
  floor: 'دور',
  commercial: 'تجاري',
};

export const TYPE_ICON: Record<PropertyType, string> = {
  apartment: '🏢',
  villa: '🏡',
  land: '📐',
  floor: '🏠',
  commercial: '🏬',
};

export const LISTINGS: Listing[] = [
  {
    id: '1', title: 'فيلا دوبلكس حديثة', purpose: 'sale', type: 'villa', district: 'أبحر الشمالية',
    price: 2850000, area: 400, rooms: 6, baths: 5, ageYears: 1, streetWidth: 20, facing: 'شمالية',
    description: 'فيلا دوبلكس بتشطيب حديث، مجلس رجال ومجلس نساء، مسبح خارجي، ملحق علوي، قريبة من الخدمات.',
    featured: true, addedDaysAgo: 2, hue: 190,
  },
  {
    id: '2', title: 'شقة 4 غرف بمدخل خاص', purpose: 'sale', type: 'apartment', district: 'الصفا',
    price: 720000, area: 170, rooms: 4, baths: 3, ageYears: 3, streetWidth: 15, facing: 'شرقية',
    description: 'شقة واسعة بمدخل خاص، مطبخ راكب، مكيفات، موقف خاص، قريبة من المدارس والمساجد.',
    featured: true, addedDaysAgo: 4, hue: 30,
  },
  {
    id: '3', title: 'أرض سكنية على شارعين', purpose: 'sale', type: 'land', district: 'الياقوت',
    price: 1350000, area: 625, streetWidth: 32, facing: 'شمالية غربية',
    description: 'أرض سكنية زاوية على شارعين، صك إلكتروني، مناسبة لبناء فيلا أو عمارة.',
    featured: true, addedDaysAgo: 6, hue: 45,
  },
  {
    id: '4', title: 'شقة 3 غرف للإيجار', purpose: 'rent', type: 'apartment', district: 'الروضة',
    price: 42000, area: 140, rooms: 3, baths: 2, ageYears: 5, facing: 'جنوبية',
    description: 'شقة نظيفة في عمارة حديثة مع مصعد، قريبة من شارع الأمير سلطان.',
    addedDaysAgo: 1, hue: 210,
  },
  {
    id: '5', title: 'دور أرضي مع حوش', purpose: 'sale', type: 'floor', district: 'المروة',
    price: 980000, area: 300, rooms: 5, baths: 4, ageYears: 2, streetWidth: 15,
    description: 'دور أرضي مع حوش وغرفة سائق، مدخلين، مطبخ مجهز.',
    addedDaysAgo: 8, hue: 160,
  },
  {
    id: '6', title: 'معرض تجاري على شارع رئيسي', purpose: 'rent', type: 'commercial', district: 'الحمراء',
    price: 180000, area: 220, streetWidth: 40,
    description: 'معرض بواجهة زجاجية على شارع رئيسي، مناسب للمطاعم والمحلات.',
    addedDaysAgo: 3, hue: 0,
  },
  {
    id: '7', title: 'فيلا مستقلة مع مسبح', purpose: 'sale', type: 'villa', district: 'الشاطئ',
    price: 4600000, area: 600, rooms: 7, baths: 6, ageYears: 6, streetWidth: 20,
    description: 'فيلا مستقلة قريبة من الكورنيش، حديقة ومسبح، ملحق خارجي.',
    addedDaysAgo: 10, hue: 260,
  },
  {
    id: '8', title: 'شقة عائلية للإيجار', purpose: 'rent', type: 'apartment', district: 'النعيم',
    price: 55000, area: 180, rooms: 4, baths: 3, ageYears: 1,
    description: 'شقة جديدة أول ساكن، غرفة خادمة، موقع هادئ.',
    addedDaysAgo: 5, hue: 120,
  },
];

export const DISTRICTS = Array.from(new Set(LISTINGS.map((l) => l.district)));

export function formatPrice(l: Pick<Listing, 'price' | 'purpose'>): string {
  const n = l.price.toLocaleString('en-US');
  return l.purpose === 'rent' ? `${n} ريال / سنوياً` : `${n} ريال`;
}
