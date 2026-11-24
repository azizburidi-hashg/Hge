import { useMemo, useState } from 'react';
import { FlatList, RefreshControl, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { colors, radius } from '../theme';
import { Listing, Purpose, PURPOSE_LABEL } from '../data/listings';
import { useListings } from '../data/store';
import { ListingCard } from '../components/ListingCard';
import { Chip, T } from '../components/ui';
import type { ScreenProps, SearchParams } from './types';

type Sort = 'site' | 'priceAsc' | 'priceDesc' | 'areaDesc';
const SORT_LABEL: Record<Sort, string> = {
  site: 'الترتيب الافتراضي', priceAsc: 'السعر: الأقل', priceDesc: 'السعر: الأعلى', areaDesc: 'المساحة: الأكبر',
};

export function SearchScreen({ openListing, fav, initial }: ScreenProps & { initial: SearchParams }) {
  const { listings: LISTINGS, types: TYPES, cities: CITIES, purposes: PURPOSES, refreshing, refresh } = useListings();
  const [query, setQuery] = useState(initial.query ?? '');
  const [purpose, setPurpose] = useState<Purpose | undefined>(initial.purpose);
  const [type, setType] = useState<string | undefined>(initial.type);
  const [city, setCity] = useState<string | undefined>();
  const [minArea, setMinArea] = useState('');
  const [sort, setSort] = useState<Sort>('site');

  const results = useMemo(() => {
    const q = query.trim();
    const min = Number(minArea.replace(/[^\d]/g, '')) || 0;
    const list = LISTINGS.filter(
      (l) =>
        (!purpose || l.purpose === purpose) &&
        (!type || l.type === type) &&
        (!city || l.city === city) &&
        (!min || (l.area ?? 0) >= min) &&
        (!q || [l.title, l.titleEn, l.location, l.city, l.type, l.description].some((s) => s.includes(q))),
    );
    // Listings without a number sort last.
    const val = (l: Listing, k: 'price' | 'area', dir: 1 | -1) => (l[k] === null ? Infinity : dir * (l[k] as number));
    const by: Record<Sort, (a: Listing, b: Listing) => number> = {
      site: (a, b) => a.order - b.order,
      priceAsc: (a, b) => val(a, 'price', 1) - val(b, 'price', 1),
      priceDesc: (a, b) => val(a, 'price', -1) - val(b, 'price', -1),
      areaDesc: (a, b) => val(a, 'area', -1) - val(b, 'area', -1),
    };
    return [...list].sort(by[sort]);
  }, [LISTINGS, query, purpose, type, city, minArea, sort]);

  const filters = (
    <View style={{ paddingTop: 12 }}>
      <View style={styles.searchBox}>
        <Text>🔍</Text>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="ابحث بالحي أو المدينة أو الوصف"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
      </View>
      <Row>
        <Chip label="الكل" active={!purpose} onPress={() => setPurpose(undefined)} />
        {PURPOSES.map((p) => (
          <Chip key={p} label={PURPOSE_LABEL[p]} active={purpose === p} onPress={() => setPurpose(p)} />
        ))}
      </Row>
      <Row>
        <Chip label="كل الأنواع" active={!type} onPress={() => setType(undefined)} />
        {TYPES.map((t) => <Chip key={t} label={t} active={type === t} onPress={() => setType(t)} />)}
      </Row>
      <Row>
        <Chip label="كل المدن" active={!city} onPress={() => setCity(undefined)} />
        {CITIES.map((c) => <Chip key={c} label={c} active={city === c} onPress={() => setCity(c)} />)}
      </Row>
      <View style={[styles.searchBox, { marginTop: 10 }]}>
        <T style={{ color: colors.muted, flexShrink: 0 }}>أقل مساحة</T>
        <TextInput
          value={minArea}
          onChangeText={setMinArea}
          keyboardType="number-pad"
          placeholder="مثال: 1000"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <T style={{ color: colors.muted }}>م²</T>
      </View>
      <Row>
        {(Object.keys(SORT_LABEL) as Sort[]).map((s) => (
          <Chip key={s} label={SORT_LABEL[s]} active={sort === s} onPress={() => setSort(s)} />
        ))}
      </Row>
      <T style={styles.count}>{results.length} عقار</T>
    </View>
  );

  return (
    <FlatList
      data={results}
      keyExtractor={(l) => l.id}
      ListHeaderComponent={filters}
      ListEmptyComponent={<T style={styles.empty}>لا توجد عقارات مطابقة. جرّب تغيير الفلاتر.</T>}
      contentContainerStyle={{ paddingBottom: 24 }}
      keyboardShouldPersistTaps="handled"
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={colors.accent} />}
      renderItem={({ item }) => (
        <ListingCard
          listing={item}
          onPress={() => openListing(item.id)}
          isFavorite={fav.has(item.id)}
          onToggleFavorite={() => fav.toggle(item.id)}
        />
      )}
    />
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      style={{ marginTop: 10 }}
      contentContainerStyle={{ paddingEnd: 16, paddingStart: 8 }}
    >
      {children}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  searchBox: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.card, borderRadius: radius.md, gap: 8,
    paddingHorizontal: 12, marginHorizontal: 16, borderWidth: 1, borderColor: colors.border,
  },
  input: { flex: 1, paddingVertical: 11, fontSize: 15, textAlign: 'right', writingDirection: 'rtl', color: colors.text },
  count: { paddingHorizontal: 16, marginTop: 14, marginBottom: 10, color: colors.muted },
  empty: { textAlign: 'center', color: colors.muted, marginTop: 30, paddingHorizontal: 16 },
});
