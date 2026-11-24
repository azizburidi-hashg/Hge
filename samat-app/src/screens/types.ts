import type { PropertyType, Purpose } from '../data/listings';
import type { useFavorites } from '../favorites';

export interface SearchParams {
  query?: string;
  type?: PropertyType;
  purpose?: Purpose;
}

export interface ScreenProps {
  openListing: (id: string) => void;
  fav: ReturnType<typeof useFavorites>;
  goSearch: (params: SearchParams) => void;
}
