-- Samat Alsakan: database for listings and offers you post from the app.
-- Run this once in Supabase: Dashboard > SQL Editor > New query > paste > Run.

-- Who may post: add your own account here after you create it (see README).
create table if not exists public.admins (
  user_id uuid primary key references auth.users (id) on delete cascade,
  note text
);
alter table public.admins enable row level security;
-- No policies: the admins list can't be read or changed from the app, only from the dashboard.

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.admins where user_id = auth.uid());
$$;

create table if not exists public.listings (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  published boolean not null default true,     -- false = hidden from the public app
  pinned boolean not null default false,       -- shown first
  title text not null check (length(title) between 3 and 200),
  type text not null,                          -- أرض، فيلا، شقة، عمارة ...
  purpose text not null default 'sale' check (purpose in ('sale', 'rent', 'wanted')),
  city text not null default 'جدة',
  location text not null default '',           -- district, e.g. حي الشاطئ
  price numeric check (price is null or price >= 0),
  price_text text not null default '',         -- e.g. "7,000 ريال للمتر" when there is no single price
  area numeric check (area is null or area >= 0),
  rooms integer check (rooms is null or rooms >= 0),
  baths integer check (baths is null or baths >= 0),
  description text not null default '',
  details text[] not null default '{}',
  photos text[] not null default '{}',         -- public photo URLs, first one is the cover
  photo_ratio numeric,                          -- width / height of the cover
  is_offer boolean not null default false,     -- special offer
  offer_text text not null default '',         -- e.g. "خصم لفترة محدودة"
  old_price numeric,                            -- shown crossed out
  offer_ends date
);

create or replace function public.touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists listings_touch on public.listings;
create trigger listings_touch before update on public.listings for each row execute function public.touch_updated_at();

alter table public.listings enable row level security;
drop policy if exists "public reads published" on public.listings;
create policy "public reads published" on public.listings for select using (published or public.is_admin());
drop policy if exists "admins insert" on public.listings;
create policy "admins insert" on public.listings for insert with check (public.is_admin());
drop policy if exists "admins update" on public.listings;
create policy "admins update" on public.listings for update using (public.is_admin()) with check (public.is_admin());
drop policy if exists "admins delete" on public.listings;
create policy "admins delete" on public.listings for delete using (public.is_admin());

-- Photos: anyone can view, only admins can upload or delete.
insert into storage.buckets (id, name, public) values ('listing-photos', 'listing-photos', true)
on conflict (id) do update set public = true;
drop policy if exists "admins upload photos" on storage.objects;
create policy "admins upload photos" on storage.objects for insert
  with check (bucket_id = 'listing-photos' and public.is_admin());
drop policy if exists "admins change photos" on storage.objects;
create policy "admins change photos" on storage.objects for update
  using (bucket_id = 'listing-photos' and public.is_admin());
drop policy if exists "admins delete photos" on storage.objects;
create policy "admins delete photos" on storage.objects for delete
  using (bucket_id = 'listing-photos' and public.is_admin());
