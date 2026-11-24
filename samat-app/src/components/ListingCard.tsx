import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, radius } from '../theme';
import { formatArea, formatOldPrice, formatPrice, Listing, place, PURPOSE_LABEL } from '../data/listings';
import { Photo, T } from './ui';

interface Props {
  listing: Listing;
  onPress: () => void;
  isFavorite: boolean;
  onToggleFavorite: () => void;
  compact?: boolean;
}

export function ListingCard({ listing: l, onPress, isFavorite, onToggleFavorite, compact }: Props) {
  const meta = [l.type, place(l), l.area ? formatArea(l.area) : '', l.rooms ? `${l.rooms} غرف` : '']
    .filter(Boolean)
    .join(' · ');
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={`${l.title}، ${formatPrice(l)}`}
      style={({ pressed }) => [styles.card, compact && styles.compact, pressed && { opacity: 0.9 }]}
    >
      <View>
        <Photo listing={l} height={compact ? 190 : 230} />
        <View style={styles.badges}>
          <View style={[styles.badge, l.purpose === 'wanted' && { backgroundColor: colors.teal }]}>
            <T style={styles.badgeText}>{PURPOSE_LABEL[l.purpose]}</T>
          </View>
          {l.isOffer ? (
            <View style={[styles.badge, { backgroundColor: colors.accent }]}>
              <T style={[styles.badgeText, { color: colors.primary }]}>{l.offerText || 'عرض خاص'}</T>
            </View>
          ) : null}
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
        <T style={styles.title} numberOfLines={2}>{l.title}</T>
        <View style={styles.priceRow}>
          <T style={styles.price} numberOfLines={1}>{formatPrice(l)}</T>
          {formatOldPrice(l) ? <T style={styles.old}>{formatOldPrice(l)}</T> : null}
        </View>
        <T style={styles.meta} numberOfLines={1}>{meta}</T>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card, borderRadius: radius.lg, overflow: 'hidden', marginHorizontal: 16, marginBottom: 14,
    borderWidth: 1, borderColor: colors.border,
  },
  compact: { width: 250, marginHorizontal: 0, marginStart: 16, marginBottom: 4 },
  badges: { position: 'absolute', bottom: 10, start: 10, end: 10, flexDirection: 'row', gap: 6, flexWrap: 'wrap' },
  badge: { backgroundColor: colors.primary, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 4 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  fav: {
    position: 'absolute', top: 8, end: 8, backgroundColor: 'rgba(255,255,255,0.95)', borderRadius: 999,
    width: 36, height: 36, alignItems: 'center', justifyContent: 'center',
  },
  body: { padding: 12, gap: 4 },
  title: { fontSize: 16, fontWeight: '700', color: colors.primary, lineHeight: 23 },
  priceRow: { flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  price: { fontSize: 16, fontWeight: '800', color: colors.accent, flexShrink: 1 },
  old: { fontSize: 13, color: colors.muted, textDecorationLine: 'line-through' },
  meta: { fontSize: 13, color: colors.muted },
});
