import { Image, Pressable, ScrollView, StyleSheet, Text, useWindowDimensions, View } from 'react-native';
import { colors, radius } from '../theme';
import { formatArea, formatOldPrice, formatPrice, Listing, place, PURPOSE_LABEL } from '../data/listings';
import { Button, Photo, T } from '../components/ui';
import { call, listingMessage, open, shareListing, whatsapp } from '../contact';
import type { ScreenProps } from './types';

export function DetailScreen({ listing: l, fav, onBack }: Pick<ScreenProps, 'fav'> & { listing: Listing; onBack: () => void }) {
  const specs: [string, string | null][] = [
    ['النوع', l.type],
    ['العرض', PURPOSE_LABEL[l.purpose]],
    ['المدينة', l.city || null],
    ['الموقع', l.location || null],
    ['المساحة', l.area ? formatArea(l.area) : null],
    ['الغرف', l.rooms ? String(l.rooms) : null],
    ['دورات المياه', l.baths ? String(l.baths) : null],
  ];
  const isFav = fav.has(l.id);
  const { width } = useWindowDimensions();
  const extra = (l.gallery ?? []).slice(1);

  return (
    <View style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ paddingBottom: 110 }}>
        <View>
          <Photo listing={l} full />
          <Pressable onPress={onBack} style={[styles.round, { start: 14 }]} accessibilityRole="button" accessibilityLabel="رجوع">
            <Text style={{ fontSize: 20 }}>→</Text>
          </Pressable>
          <Pressable
            onPress={() => fav.toggle(l.id)}
            style={[styles.round, { end: 14 }]}
            accessibilityRole="button"
            accessibilityLabel={isFav ? 'إزالة من المفضلة' : 'إضافة إلى المفضلة'}
          >
            <Text style={{ fontSize: 20, color: isFav ? colors.danger : colors.muted }}>{isFav ? '♥' : '♡'}</Text>
          </Pressable>
        </View>

        {extra.length ? (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.thumbs}>
            {extra.map((src, i) => (
              <Image key={i} source={src} style={{ width: width * 0.6, height: width * 0.45, borderRadius: radius.sm }} resizeMode="cover" />
            ))}
          </ScrollView>
        ) : null}

        <View style={styles.body}>
          {l.isOffer ? (
            <View style={styles.offer}>
              <T style={styles.offerText}>
                {`🏷️ ${l.offerText || 'عرض خاص'}${l.offerEnds ? ` · حتى ${l.offerEnds}` : ''}`}
              </T>
            </View>
          ) : null}
          <T style={styles.title}>{l.title}</T>
          <T style={styles.price}>{formatPrice(l)}</T>
          {formatOldPrice(l) ? <T style={styles.old}>بدلاً من {formatOldPrice(l)}</T> : null}
          {place(l) ? <T style={styles.meta}>📍 {place(l)}</T> : null}

          <View style={styles.grid}>
            {specs.filter(([, v]) => v).map(([k, v]) => (
              <View key={k} style={styles.spec}>
                <View style={styles.specBox}>
                  <T style={styles.specKey}>{k}</T>
                  <T style={styles.specVal}>{v}</T>
                </View>
              </View>
            ))}
          </View>

          {l.description ? (
            <>
              <T style={styles.h}>الوصف</T>
              <T style={styles.desc}>{l.description}</T>
            </>
          ) : null}

          {l.details.length ? (
            <>
              <T style={styles.h}>التفاصيل</T>
              {l.details.map((d, i) => (
                <T key={i} style={styles.detail}>• {d}</T>
              ))}
            </>
          ) : null}

          <View style={styles.row}>
            <Button label="مشاركة" outline onPress={() => shareListing(l)} style={{ flex: 1 }} />
            {l.url ? <Button label="عرض في الموقع" outline onPress={() => open(l.url)} style={{ flex: 1 }} /> : null}
          </View>
        </View>
      </ScrollView>

      <View style={styles.bar}>
        <Button label="واتساب" color={colors.whatsapp} onPress={() => whatsapp(listingMessage(l))} style={{ flex: 1 }} />
        <Button label="اتصال" onPress={() => call()} style={{ flex: 1 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  round: {
    position: 'absolute', top: 14, width: 42, height: 42, borderRadius: 999, backgroundColor: 'rgba(255,255,255,0.95)',
    alignItems: 'center', justifyContent: 'center',
  },
  body: { padding: 16 },
  title: { fontSize: 21, fontWeight: '800', color: colors.primary, lineHeight: 30 },
  price: { fontSize: 20, fontWeight: '800', color: colors.accent, marginTop: 6 },
  meta: { color: colors.muted, marginTop: 6 },
  old: { color: colors.muted, textDecorationLine: 'line-through', marginTop: 2 },
  thumbs: { gap: 8, paddingHorizontal: 16, paddingTop: 12 },
  offer: { alignSelf: 'flex-start', backgroundColor: colors.accent, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 5, marginBottom: 10 },
  offerText: { color: colors.primary, fontWeight: '800', fontSize: 13 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 16, marginHorizontal: -5 },
  spec: { width: '50%', padding: 5 },
  specBox: {
    backgroundColor: colors.card, borderRadius: radius.sm, paddingHorizontal: 12, paddingVertical: 10,
    borderWidth: 1, borderColor: colors.border,
  },
  specKey: { fontSize: 12, color: colors.muted },
  specVal: { fontSize: 15, fontWeight: '700', marginTop: 2 },
  h: { fontSize: 17, fontWeight: '800', marginTop: 20, marginBottom: 6, color: colors.primary },
  desc: { lineHeight: 25 },
  detail: { lineHeight: 25, marginBottom: 2 },
  row: { flexDirection: 'row', gap: 10, marginTop: 22 },
  bar: {
    position: 'absolute', bottom: 0, left: 0, right: 0, flexDirection: 'row', gap: 10, padding: 12,
    backgroundColor: colors.card, borderTopWidth: 1, borderColor: colors.border,
  },
});
