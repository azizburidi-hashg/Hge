import { FlatList, Pressable, RefreshControl, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { BUSINESS } from '../config';
import { colors, radius } from '../theme';
import { Listing, typeIcon } from '../data/listings';
import { useListings } from '../data/store';
import { UpdatedNote } from '../components/UpdatedNote';
import { ListingCard } from '../components/ListingCard';
import { SectionTitle, T } from '../components/ui';
import type { ScreenProps } from './types';

export function HomeScreen({ openListing, fav, goSearch }: ScreenProps) {
  const { listings: LISTINGS, types: TYPES, refreshing, refresh } = useListings();
  const offers = LISTINGS.filter((l) => l.isOffer);
  const featured = LISTINGS.filter((l) => l.purpose !== 'wanted').slice(0, 8);
  const lands = LISTINGS.filter((l) => l.type === 'أرض' && l.purpose !== 'wanted');
  const count = (t: string) => LISTINGS.filter((l) => l.type === t).length;

  const row = (data: Listing[]) => (
    <FlatList
      horizontal
      data={data}
      keyExtractor={(l) => l.id}
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={{ paddingEnd: 16 }}
      renderItem={({ item }) => (
        <ListingCard
          compact
          listing={item}
          onPress={() => openListing(item.id)}
          isFavorite={fav.has(item.id)}
          onToggleFavorite={() => fav.toggle(item.id)}
        />
      )}
    />
  );

  return (
    <ScrollView
      contentContainerStyle={{ paddingBottom: 24 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={colors.accent} />}
    >
      <View style={styles.hero}>
        <T style={styles.brandSmall}>{BUSINESS.nameAr}</T>
        <T style={styles.brand}>{BUSINESS.subtitleAr}</T>
        <T style={styles.tagline}>{BUSINESS.taglineAr}</T>
        <View style={styles.searchBox}>
          <Text style={{ fontSize: 16 }}>🔍</Text>
          <TextInput
            placeholder="ابحث بالحي أو المدينة أو نوع العقار"
            placeholderTextColor={colors.muted}
            style={styles.searchInput}
            returnKeyType="search"
            onSubmitEditing={(e) => goSearch({ query: e.nativeEvent.text })}
          />
        </View>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.types}>
        {TYPES.map((t) => (
          <Pressable key={t} style={styles.typeItem} onPress={() => goSearch({ type: t })} accessibilityRole="button">
            <View style={styles.typeIcon}><Text style={{ fontSize: 24 }}>{typeIcon(t)}</Text></View>
            <T style={styles.typeLabel}>{t}</T>
            <T style={styles.typeCount}>{count(t)}</T>
          </Pressable>
        ))}
      </ScrollView>

      {offers.length ? (
        <>
          <SectionTitle>{`🏷️ عروض خاصة (${offers.length})`}</SectionTitle>
          {row(offers)}
        </>
      ) : null}

      <SectionTitle>عقارات مميزة</SectionTitle>
      {row(featured)}

      <SectionTitle>{`أراضٍ للبيع (${lands.length})`}</SectionTitle>
      {row(lands)}

      <Pressable onPress={() => goSearch({})} style={styles.all} accessibilityRole="button">
        <T style={styles.allText}>{`عرض كل العقارات (${LISTINGS.length}) ←`}</T>
      </Pressable>
      <UpdatedNote />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  hero: {
    backgroundColor: colors.primary, paddingHorizontal: 16, paddingTop: 18, paddingBottom: 22,
    borderBottomLeftRadius: radius.lg, borderBottomRightRadius: radius.lg,
  },
  brandSmall: { color: '#DCE3EA', fontSize: 15 },
  brand: { color: '#fff', fontSize: 28, fontWeight: '800', marginTop: 2 },
  tagline: { color: '#C9D3DD', fontSize: 14, marginTop: 8, marginBottom: 16, lineHeight: 22 },
  searchBox: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: radius.md,
    paddingHorizontal: 12, gap: 8,
  },
  searchInput: { flex: 1, paddingVertical: 12, fontSize: 15, textAlign: 'right', writingDirection: 'rtl', color: colors.text },
  types: { paddingHorizontal: 8, paddingTop: 18, gap: 6 },
  typeItem: { alignItems: 'center', width: 76 },
  typeIcon: {
    width: 56, height: 56, borderRadius: 16, backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: colors.border,
  },
  typeLabel: { fontSize: 13, marginTop: 6, textAlign: 'center' },
  typeCount: { fontSize: 11, color: colors.muted, textAlign: 'center' },
  all: {
    marginHorizontal: 16, marginTop: 22, paddingVertical: 14, borderRadius: radius.md, backgroundColor: colors.accent,
    alignItems: 'center',
  },
  allText: { color: colors.primary, fontWeight: '800', textAlign: 'center', fontSize: 16 },
});
