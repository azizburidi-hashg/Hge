import { FlatList, StyleSheet, View } from 'react-native';
import { colors } from '../theme';
import { useListings } from '../data/store';
import { ListingCard } from '../components/ListingCard';
import { Button, T } from '../components/ui';
import type { ScreenProps } from './types';

export function FavoritesScreen({ openListing, fav, goSearch }: ScreenProps) {
  const { listings } = useListings();
  const items = listings.filter((l) => fav.has(l.id));
  return (
    <FlatList
      data={items}
      keyExtractor={(l) => l.id}
      contentContainerStyle={{ paddingVertical: 16, flexGrow: 1 }}
      ListEmptyComponent={
        <View style={styles.empty}>
          <T style={styles.heart}>♡</T>
          <T style={styles.emptyText}>لم تضف أي عقار للمفضلة بعد. اضغط على ♡ في أي عقار لحفظه هنا.</T>
          <Button label="تصفح العقارات" onPress={() => goSearch({})} style={{ marginTop: 16, alignSelf: 'stretch' }} />
        </View>
      }
      renderItem={({ item }) => (
        <ListingCard
          listing={item}
          onPress={() => openListing(item.id)}
          isFavorite
          onToggleFavorite={() => fav.toggle(item.id)}
        />
      )}
    />
  );
}

const styles = StyleSheet.create({
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  heart: { fontSize: 48, color: colors.muted, textAlign: 'center' },
  emptyText: { textAlign: 'center', color: colors.muted, marginTop: 8, lineHeight: 22 },
});
