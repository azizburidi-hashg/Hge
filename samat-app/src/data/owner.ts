// Talks to the Supabase project that holds the listings and offers the owner posts from the app.
// Uses Supabase's plain HTTP API (no SDK). The anon key is public by design; the database rules in
// supabase/schema.sql decide who may change what.
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import { SUPABASE } from '../config';
import type { Listing, Purpose } from './types';

export const ownerEnabled = () => !!(SUPABASE.url && SUPABASE.anonKey);
const BUCKET = 'listing-photos';
const SESSION_KEY = 'owner.session.v1';

export interface Row {
  id: string;
  created_at: string;
  updated_at: string;
  published: boolean;
  pinned: boolean;
  title: string;
  type: string;
  purpose: Purpose;
  city: string;
  location: string;
  price: number | null;
  price_text: string;
  area: number | null;
  rooms: number | null;
  baths: number | null;
  description: string;
  details: string[];
  photos: string[];
  photo_ratio: number | null;
  is_offer: boolean;
  offer_text: string;
  old_price: number | null;
  offer_ends: string | null;
}
export type RowInput = Omit<Row, 'id' | 'created_at' | 'updated_at'>;

interface Session { access_token: string; refresh_token: string; expires_at: number; email: string }

// ---- session storage (Keychain/Keystore on phones) ----
const store = {
  get: (k: string) => (Platform.OS === 'web' ? AsyncStorage.getItem(k) : SecureStore.getItemAsync(k)),
  set: (k: string, v: string) => (Platform.OS === 'web' ? AsyncStorage.setItem(k, v) : SecureStore.setItemAsync(k, v)),
  del: (k: string) => (Platform.OS === 'web' ? AsyncStorage.removeItem(k) : SecureStore.deleteItemAsync(k)),
};

let session: Session | null = null;

async function call<T>(path: string, init: RequestInit & { auth?: boolean } = {}): Promise<T> {
  const headers: Record<string, string> = { apikey: SUPABASE.anonKey, ...(init.headers as Record<string, string>) };
  if (init.auth) headers.Authorization = `Bearer ${(await token()) ?? ''}`;
  else headers.Authorization = `Bearer ${SUPABASE.anonKey}`;
  if (init.body && typeof init.body === 'string' && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 60000);
  try {
    const res = await fetch(`${SUPABASE.url}${path}`, { ...init, headers, signal: ctrl.signal });
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) throw new Error(friendlyError(res.status, data));
    return data as T;
  } finally {
    clearTimeout(timer);
  }
}

function friendlyError(status: number, data: { msg?: string; message?: string; error_description?: string } | null) {
  const raw = data?.error_description || data?.msg || data?.message || '';
  if (/invalid login|invalid_grant|Invalid login credentials/i.test(raw)) return 'البريد أو كلمة المرور غير صحيحة';
  if (status === 401 || status === 403 || /row-level security|permission/i.test(raw))
    return 'هذا الحساب غير مصرح له بالنشر. أضفه إلى قائمة المالكين (admins) في Supabase.';
  if (status === 413) return 'الصورة كبيرة جداً';
  return raw ? `خطأ: ${raw}` : `خطأ في الاتصال (${status})`;
}

// ---- sign in / out ----
async function saveSession(r: { access_token: string; refresh_token: string; expires_in: number; user?: { email?: string } }, email?: string) {
  session = {
    access_token: r.access_token,
    refresh_token: r.refresh_token,
    expires_at: Date.now() + r.expires_in * 1000,
    email: r.user?.email ?? email ?? session?.email ?? '',
  };
  await store.set(SESSION_KEY, JSON.stringify(session));
}

export async function signIn(email: string, password: string) {
  const r = await call<{ access_token: string; refresh_token: string; expires_in: number; user: { email: string } }>(
    '/auth/v1/token?grant_type=password', { method: 'POST', body: JSON.stringify({ email: email.trim(), password }) });
  await saveSession(r, email);
  return session!.email;
}

export async function signOut() {
  session = null;
  await store.del(SESSION_KEY);
}

/** The signed-in owner's email, or null. Restores a saved sign-in. */
export async function currentOwner(): Promise<string | null> {
  if (!ownerEnabled()) return null;
  if (!session) {
    const v = await store.get(SESSION_KEY).catch(() => null);
    if (v) session = JSON.parse(v);
  }
  return (await token()) ? session!.email : null;
}

async function token(): Promise<string | null> {
  if (!session) return null;
  if (Date.now() < session.expires_at - 60000) return session.access_token;
  try {
    const r = await call<{ access_token: string; refresh_token: string; expires_in: number }>(
      '/auth/v1/token?grant_type=refresh_token', { method: 'POST', body: JSON.stringify({ refresh_token: session.refresh_token }) });
    await saveSession(r);
    return session.access_token;
  } catch {
    await signOut();
    return null;
  }
}

// ---- listings ----
const ORDER = 'order=pinned.desc,created_at.desc';

/** Published listings, for everyone. */
export const fetchPublished = () => call<Row[]>(`/rest/v1/listings?select=*&published=eq.true&${ORDER}`);

/** Everything, including hidden listings (owner only). */
export const fetchAll = () => call<Row[]>(`/rest/v1/listings?select=*&${ORDER}`, { auth: true });

export async function saveListing(input: RowInput, id?: string): Promise<Row> {
  const body = JSON.stringify(input);
  const headers = { Prefer: 'return=representation' };
  const rows = id
    ? await call<Row[]>(`/rest/v1/listings?id=eq.${encodeURIComponent(id)}`, { method: 'PATCH', body, headers, auth: true })
    : await call<Row[]>('/rest/v1/listings', { method: 'POST', body, headers, auth: true });
  if (!rows?.length) throw new Error('لم يتم الحفظ. تأكد أن الحساب مصرح له بالنشر.');
  return rows[0];
}

export async function deleteListing(row: Row) {
  await call(`/rest/v1/listings?id=eq.${encodeURIComponent(row.id)}`, { method: 'DELETE', auth: true });
  const paths = row.photos.map(photoPath).filter((p): p is string => !!p);
  if (paths.length) {
    await call(`/storage/v1/object/${BUCKET}`, { method: 'DELETE', body: JSON.stringify({ prefixes: paths }), auth: true }).catch(() => {});
  }
}

// ---- photos ----
const publicPrefix = () => `${SUPABASE.url}/storage/v1/object/public/${BUCKET}/`;
const photoPath = (url: string) => (url.startsWith(publicPrefix()) ? url.slice(publicPrefix().length) : null);

/** Uploads a picked photo and returns its public URL. */
export async function uploadPhoto(localUri: string, mimeType = 'image/jpeg'): Promise<string> {
  const ext = mimeType.includes('png') ? 'png' : mimeType.includes('webp') ? 'webp' : 'jpg';
  const path = `${new Date().toISOString().slice(0, 10)}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${ext}`;
  const blob = await (await fetch(localUri)).blob();
  await call(`/storage/v1/object/${BUCKET}/${path}`, {
    method: 'POST', body: blob, headers: { 'Content-Type': mimeType, 'x-upsert': 'false', 'cache-control': '31536000' }, auth: true,
  });
  return publicPrefix() + path;
}

// ---- conversion for display ----
export function rowToListing(r: Row, order: number): Listing {
  const photos = r.photos.filter(Boolean);
  return {
    id: `owner-${r.id}`,
    source: 'owner',
    order,
    title: r.title,
    titleEn: '',
    type: r.type,
    city: r.city,
    location: r.location,
    purpose: r.purpose,
    price: r.price === null ? null : Number(r.price),
    priceText: r.price_text,
    area: r.area === null ? null : Number(r.area),
    rooms: r.rooms,
    baths: r.baths,
    description: r.description,
    details: r.details ?? [],
    url: '',
    image: photos[0] ? { uri: photos[0] } : require('../../assets/icon.png'),
    imageRatio: photos[0] ? Number(r.photo_ratio) || 0 : 1,
    gallery: photos.map((uri) => ({ uri })),
    isOffer: r.is_offer && (!r.offer_ends || r.offer_ends >= new Date().toISOString().slice(0, 10)),
    offerText: r.offer_text,
    oldPrice: r.old_price === null ? null : Number(r.old_price),
    offerEnds: r.offer_ends,
  };
}
