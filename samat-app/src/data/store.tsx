// Keeps the app's listings up to date with no app update needed. Two sources:
//  - listings and offers the owner posts in the app (Supabase), shown first;
//  - listings on samat-alsakan.com.
// Starts with the copy last saved on the phone (or the one built into the app), fetches both sources when the app
// opens, when it comes back to the foreground, on pull-to-refresh and after the owner saves a change, and saves them
// so the app still works offline. If one source can't be reached, its last copy stays.
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { AppState } from 'react-native';
import { BUNDLED_LISTINGS, derive } from './listings';
import { fetchLiveListings } from './remote';
import { fetchPublished, ownerEnabled, rowToListing } from './owner';
import type { Listing } from './types';

const KEY = 'listings.cache.v2';
const MIN_INTERVAL_MS = 5 * 60 * 1000;
const RATIOS = Object.fromEntries(BUNDLED_LISTINGS.map((l) => [l.id, l.imageRatio]));

// Photos are saved as URLs; built-in photos (numbers) are matched back by id.
type Saved = Omit<Listing, 'image' | 'gallery'> & { imageUri?: string; galleryUris?: string[] };
const BUNDLED_BY_ID = new Map(BUNDLED_LISTINGS.map((l) => [l.id, l]));
const uriOf = (img: unknown) => (img && typeof img === 'object' && 'uri' in img ? String((img as { uri: string }).uri) : undefined);
const toSaved = (l: Listing): Saved => {
  const { image, gallery, ...rest } = l;
  return { ...rest, imageUri: uriOf(image), galleryUris: gallery?.map(uriOf).filter((u): u is string => !!u) };
};
const fromSaved = ({ imageUri, galleryUris, ...l }: Saved): Listing => ({
  ...l,
  image: imageUri ? { uri: imageUri } : BUNDLED_BY_ID.get(l.id)?.image ?? require('../../assets/icon.png'),
  gallery: galleryUris?.map((uri) => ({ uri })),
});

interface State {
  listings: Listing[];
  updatedAt: number | null;
  refreshing: boolean;
  offline: boolean;
  refresh: () => Promise<void>;
}
const Ctx = createContext<State | null>(null);

export function ListingsProvider({ children }: { children: ReactNode }) {
  const [site, setSite] = useState<Listing[]>(BUNDLED_LISTINGS);
  const [mine, setMine] = useState<Listing[]>([]);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [offline, setOffline] = useState(false);
  const lastCheck = useRef(0);
  const busy = useRef(false);
  const fetched = useRef(false);

  const refresh = useCallback(async () => {
    if (busy.current) return;
    busy.current = true;
    setRefreshing(true);
    lastCheck.current = Date.now();
    const [s, m] = await Promise.allSettled([
      fetchLiveListings(RATIOS),
      ownerEnabled() ? fetchPublished().then((rows) => rows.map(rowToListing)) : Promise.resolve([] as Listing[]),
    ]);
    if (s.status === 'fulfilled') setSite(s.value);
    if (m.status === 'fulfilled') setMine(m.value);
    if (s.status === 'fulfilled' || m.status === 'fulfilled') {
      fetched.current = true;
      setUpdatedAt(Date.now());
      const save = { savedAt: Date.now(), site: s.status === 'fulfilled' ? s.value : null, mine: m.status === 'fulfilled' ? m.value : null };
      AsyncStorage.getItem(KEY)
        .then((old) => {
          const prev = old ? JSON.parse(old) : {};
          return AsyncStorage.setItem(KEY, JSON.stringify({
            savedAt: save.savedAt,
            site: save.site ? save.site.map(toSaved) : prev.site,
            mine: save.mine ? save.mine.map(toSaved) : prev.mine,
          }));
        })
        .catch(() => {});
    }
    setOffline(s.status === 'rejected' || m.status === 'rejected');
    busy.current = false;
    setRefreshing(false);
  }, []);

  useEffect(() => {
    AsyncStorage.getItem(KEY)
      .then((v) => {
        if (!v || fetched.current) return;
        const c = JSON.parse(v) as { savedAt: number; site?: Saved[]; mine?: Saved[] };
        if (c.site?.length) setSite(c.site.map(fromSaved));
        if (c.mine?.length) setMine(c.mine.map(fromSaved));
        setUpdatedAt(c.savedAt);
      })
      .catch(() => {});
    refresh();
    const sub = AppState.addEventListener('change', (st) => {
      if (st === 'active' && Date.now() - lastCheck.current > MIN_INTERVAL_MS) refresh();
    });
    return () => sub.remove();
  }, [refresh]);

  const listings = useMemo(() => [...mine, ...site].map((l, i) => ({ ...l, order: i })), [mine, site]);
  const value = useMemo(
    () => ({ listings, updatedAt, refreshing, offline, refresh }),
    [listings, updatedAt, refreshing, offline, refresh],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useListings() {
  const s = useContext(Ctx);
  if (!s) throw new Error('useListings must be used inside ListingsProvider');
  const derived = useMemo(() => derive(s.listings), [s.listings]);
  return { ...s, ...derived };
}
