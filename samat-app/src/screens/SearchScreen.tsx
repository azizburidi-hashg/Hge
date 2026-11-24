import { useMemo, useState } from 'react';
import { FlatList, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { colors, radius } from '../theme';
import { DISTRICTS, LISTINGS, PropertyType, Purpose, TYPE_LABEL } from '../data/listings';
import { ListingCard } from '../components/ListingCard';
import { Chip, T } from '../components/ui';
import type { ScreenProps, SearchParams } from './types';

type Sort = 'newest' | 'priceAsc' | 'priceDesc' | 'areaDesc';
const SORT_LABEL: Record<Sort, string> = {
  newest: 'الأحدث', priceAsc: 'السعر: الأقل', priceDesc: 'السعر: الأعلى', areaDesc: 'المساحة: الأكبر',
};

export function SearchScreen({ openListing, fav, initial }: ScreenProps & { initial: SearchParams }) {
  const [query, setQuery] = useState(initial.query ?? '');
  const [purpose, setPurpose] = useState<Purpose | undefined>(initial.purpose);
  const [type, setType] = useState<PropertyType | undefined>(initial.type);
  const [district, setDistrict] = useState<string | undefined>();
  const [maxPrice, setMaxPrice] = useState('');
  const [sort, setSort] = useState<Sort>('newest');

  const results = useMemo(() => {
    const q = query.trim();
    const max = Number(maxPrice.replace(/[^\d]/g, '')) || Infinity;
    const list = LISTINGS.filter(
      (l) =>
        (!purpose || l.purpose === purpose) &&
        (!type || l.type === type) &&
        (!district || l.district === district) &&
        l.price <= max &&
        (!q || l.title.includes(q) || l.district.includes(q) || TYPE_LABEL[l.type].includes(q) || l.description.includes(q)),
    );
    const by: Record<Sort, (a: typeof list[0], b: typeof list[0]) => number> = {
      newest: (a, b) => a.addedDaysAgo - b.addedDaysAgo,
      priceAsc: (a, b) => a.price - b.price,
      priceDesc: (a, b) => b.price - a.price,
      areaDesc: (a, b) => b.area - a.area,
    };
    return [...list].sort(by[sort]);
  }, [query, purpose, type, district, maxPrice, sort]);

  const filters = (
    <View style={{ paddingTop: 12 }}>
      <View style={styles.searchBox}>
        <Text>🔍</Text>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="ابحث بالحي أو الوصف"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
      </View>
      <Row>
        <Chip label="الكل" active={!purpose} onPress={() => setPurpose(undefined)} />
        <Chip label="للبيع" active={purpose === 'sale'} onPress={() => setPurpose('sale')} />
        <Chip label="للإيجار" active={purpose === 'rent'} onPress={() => setPurpose('rent')} />
      </Row>
      <Row>
        <Chip label="كل الأنواع" active={!type} onPress={() => setType(undefined)} />
        {(Object.keys(TYPE_LABEL) as PropertyType[]).map((t) => (
          <Chip key={t} label={TYPE_LABEL[t]} active={type === t} onPress={() => setType(t)} />
        ))}
      </Row>
      <Row>
        <Chip label="كل الأحياء" active={!district} onPress={() => setDistrict(undefined)} />
        {DISTRICTS.map((d) => (
          <Chip key={d} label={d} active={district === d} onPress={() => setDistrict(d)} />
        ))}
      </Row>
      <View style={[styles.searchBox, { marginTop: 10 }]}>
        <T style={{ color: colors.muted }} numberOfLines={1}>الحد الأعلى</T>
        <TextInput
          value={maxPrice}
          onChangeText={setMaxPrice}
          keyboardType="number-pad"
          placeholder="مثال: 1000000"
          placeholderTextColor={colors.muted}
          style={styles.input}
        />
        <T style={{ color: colors.muted }}>ريال</T>
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
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginTop: 10 }} contentContainerStyle={{ paddingEnd: 16, paddingStart: 8 }}>
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
