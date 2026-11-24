// Keeps the app's listings in sync with samat-alsakan.com, with no app update needed:
// 1. starts with the listings last saved on the phone (or, on first launch, the ones built into the app),
// 2. fetches the live listings when the app opens, when it comes back to the foreground, and on pull-to-refresh,
// 3. saves them on the phone so the app still works offline.
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { AppState } from 'react-native';
import { BUNDLED_LISTINGS, derive } from './listings';
import { fetchLiveListings } from './remote';
import type { Listing } from './types';

const KEY = 'listings.cache.v1';
const MIN_INTERVAL_MS = 5 * 60 * 1000; // re-check at most this often when the user returns to the app

// Known photo shapes, so cards and posters lay out without waiting for the photo.
const RATIOS = Object.fromEntries(BUNDLED_LISTINGS.map((l) => [l.id, l.imageRatio]));

type Saved = Omit<Listing, 'image'> & { imageUri: string };

interface State {
  listings: Listing[];
  updatedAt: number | null; // when the live listings were last fetched successfully
  refreshing: boolean;
  offline: boolean; // the last check failed; showing saved listings
  refresh: () => Promise<void>;
}

const Ctx = createContext<State | null>(null);

export function ListingsProvider({ children }: { children: ReactNode }) {
  const [listings, setListings] = useState<Listing[]>(BUNDLED_LISTINGS);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [offline, setOffline] = useState(false);
  const lastCheck = useRef(0);
  const busy = useRef(false);
  const gotLive = useRef(false);

  const refresh = useCallback(async () => {
    if (busy.current) return;
    busy.current = true;
    setRefreshing(true);
    lastCheck.current = Date.now();
    try {
      const live = await fetchLiveListings(RATIOS);
      gotLive.current = true;
      setListings(live);
      setUpdatedAt(Date.now());
      setOffline(false);
      const saved: Saved[] = live.map(({ image, ...l }) => ({ ...l, imageUri: (image as { uri: string }).uri }));
      AsyncStorage.setItem(KEY, JSON.stringify({ savedAt: Date.now(), listings: saved })).catch(() => {});
    } catch {
      setOffline(true); // keep showing what we have
    } finally {
      busy.current = false;
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    AsyncStorage.getItem(KEY)
      .then((v) => {
        if (!v || gotLive.current) return;
        const c = JSON.parse(v) as { savedAt: number; listings: Saved[] };
        if (!Array.isArray(c.listings) || !c.listings.length) return;
        setListings(c.listings.map(({ imageUri, ...l }) => ({ ...l, image: { uri: imageUri } })));
        setUpdatedAt(c.savedAt);
      })
      .catch(() => {});
    refresh();
    const sub = AppState.addEventListener('change', (s) => {
      if (s === 'active' && Date.now() - lastCheck.current > MIN_INTERVAL_MS) refresh();
    });
    return () => sub.remove();
  }, [refresh]);

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
