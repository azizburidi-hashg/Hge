import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, radius } from '../theme';
import { formatPrice, Listing, PURPOSE_LABEL } from '../data/listings';
import { Photo, T } from './ui';

interface Props {
  listing: Listing;
  onPress: () => void;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  compact?: boolean;
}

export function ListingCard({ listing: l, onPress, isFavorite, onToggleFavorite, compact }: Props) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={`${l.title}، ${l.district}، ${formatPrice(l)}`}
      style={({ pressed }) => [styles.card, compact && styles.compact, pressed && { opacity: 0.9 }]}
    >
      <View>
        <Photo listing={l} height={compact ? 120 : 170} />
        <View style={styles.badge}>
          <T style={styles.badgeText}>{PURPOSE_LABEL[l.purpose]}</T>
        </View>
        <Pressable
          onPress={onToggleFavorite}
          hitSlop={10}
          accessibilityRole="button"
          accessibilityLabel={isFavorite ? 'إزالة من المفضلة' : 'إضافة إلى المفضلة'}
          style={styles.fav}
        >
          <Text style={{ fontSize: 20, color: isFavorite ? colors.danger : colors.muted }}>{isFavorite ? '♥' : '♡'}</Text>
        </Pressable>
      </View>
      <View style={styles.body}>
        <T style={styles.price}>{formatPrice(l)}</T>
        <T style={styles.title} numberOfLines={1}>{l.title}</T>
        <T style={styles.meta} numberOfLines={1}>
          📍 {l.district} · {l.area} م²{l.rooms ? ` · ${l.rooms} غرف` : ''}
        </T>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card, borderRadius: radius.lg, overflow: 'hidden', marginHorizontal: 16, marginBottom: 14,
    borderWidth: 1, borderColor: colors.border,
  },
  compact: { width: 230, marginHorizontal: 0, marginStart: 16, marginBottom: 4 },
  badge: {
    position: 'absolute', top: 10, start: 10, backgroundColor: colors.primary, borderRadius: 999,
    paddingHorizontal: 10, paddingVertical: 3,
  },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  fav: {
    position: 'absolute', top: 8, end: 8, backgroundColor: 'rgba(255,255,255,0.92)', borderRadius: 999,
    width: 36, height: 36, alignItems: 'center', justifyContent: 'center',
  },
  body: { padding: 12, gap: 3 },
  price: { fontSize: 17, fontWeight: '800', color: colors.primary },
  title: { fontSize: 15, fontWeight: '600' },
  meta: { fontSize: 13, color: colors.muted },
});
