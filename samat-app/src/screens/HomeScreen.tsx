import { FlatList, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { BUSINESS } from '../config';
import { colors, radius } from '../theme';
import { LISTINGS, PropertyType, TYPE_ICON, TYPE_LABEL } from '../data/listings';
import { ListingCard } from '../components/ListingCard';
import { SectionTitle, T } from '../components/ui';
import type { ScreenProps } from './types';

const TYPES: PropertyType[] = ['apartment', 'villa', 'land', 'floor', 'commercial'];

export function HomeScreen({ openListing, fav, goSearch }: ScreenProps) {
  const featured = LISTINGS.filter((l) => l.featured);
  const latest = [...LISTINGS].sort((a, b) => a.addedDaysAgo - b.addedDaysAgo).slice(0, 4);

  return (
    <ScrollView contentContainerStyle={{ paddingBottom: 24 }}>
      <View style={styles.hero}>
        <T style={styles.brand}>{BUSINESS.nameAr}</T>
        <T style={styles.tagline}>{BUSINESS.taglineAr}</T>
        <View style={styles.searchBox}>
          <Text style={{ fontSize: 16 }}>🔍</Text>
          <TextInput
            placeholder="ابحث بالحي أو نوع العقار"
            placeholderTextColor={colors.muted}
            style={styles.searchInput}
            returnKeyType="search"
            onSubmitEditing={(e) => goSearch({ query: e.nativeEvent.text })}
          />
        </View>
      </View>

      <View style={styles.types}>
        {TYPES.map((t) => (
          <Pressable key={t} style={styles.typeItem} onPress={() => goSearch({ type: t })} accessibilityRole="button">
            <View style={styles.typeIcon}><Text style={{ fontSize: 24 }}>{TYPE_ICON[t]}</Text></View>
            <T style={styles.typeLabel}>{TYPE_LABEL[t]}</T>
          </Pressable>
        ))}
      </View>

      <SectionTitle>عقارات مميزة</SectionTitle>
      <FlatList
        horizontal
        data={featured}
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

      <SectionTitle>أحدث العروض</SectionTitle>
      {latest.map((l) => (
        <ListingCard
          key={l.id}
          listing={l}
          onPress={() => openListing(l.id)}
          isFavorite={fav.has(l.id)}
          onToggleFavorite={() => fav.toggle(l.id)}
        />
      ))}
      <Pressable onPress={() => goSearch({})} style={styles.more} accessibilityRole="button">
        <T style={styles.moreText}>عرض كل العقارات ←</T>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  hero: {
    backgroundColor: colors.primary, paddingHorizontal: 16, paddingTop: 20, paddingBottom: 22,
    borderBottomLeftRadius: radius.lg, borderBottomRightRadius: radius.lg,
  },
  brand: { color: '#fff', fontSize: 26, fontWeight: '800' },
  tagline: { color: '#D8E6E9', fontSize: 15, marginTop: 4, marginBottom: 16 },
  searchBox: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: radius.md,
    paddingHorizontal: 12, gap: 8,
  },
  searchInput: { flex: 1, paddingVertical: 12, fontSize: 15, textAlign: 'right', writingDirection: 'rtl', color: colors.text },
  types: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 12, paddingTop: 18 },
  typeItem: { alignItems: 'center', flex: 1 },
  typeIcon: {
    width: 54, height: 54, borderRadius: 16, backgroundColor: colors.card, alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: colors.border,
  },
  typeLabel: { fontSize: 13, marginTop: 6, textAlign: 'center' },
  more: { alignItems: 'center', paddingVertical: 8 },
  moreText: { color: colors.primary, fontWeight: '700', textAlign: 'center' },
});
