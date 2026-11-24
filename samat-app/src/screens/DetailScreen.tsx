import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { BUSINESS } from '../config';
import { colors, radius } from '../theme';
import { formatPrice, Listing, PURPOSE_LABEL, TYPE_LABEL } from '../data/listings';
import { Button, Photo, T } from '../components/ui';
import { call, listingMessage, shareListing, whatsapp } from '../contact';
import type { ScreenProps } from './types';

export function DetailScreen({ listing: l, fav, onBack }: Pick<ScreenProps, 'fav'> & { listing: Listing; onBack: () => void }) {
  const specs: [string, string | undefined][] = [
    ['النوع', TYPE_LABEL[l.type]],
    ['الغرض', PURPOSE_LABEL[l.purpose]],
    ['المساحة', `${l.area} م²`],
    ['الغرف', l.rooms?.toString()],
    ['دورات المياه', l.baths?.toString()],
    ['عمر العقار', l.ageYears !== undefined ? ageText(l.ageYears) : undefined],
    ['عرض الشارع', l.streetWidth ? `${l.streetWidth} م` : undefined],
    ['الواجهة', l.facing],
  ];
  const isFav = fav.has(l.id);

  return (
    <View style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ paddingBottom: 110 }}>
        <View>
          <Photo listing={l} height={260} />
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

        <View style={styles.body}>
          <T style={styles.price}>{formatPrice(l)}</T>
          <T style={styles.title}>{l.title}</T>
          <T style={styles.meta}>📍 {l.district}، {BUSINESS.city} · رقم الإعلان {l.id}</T>

          <View style={styles.grid}>
            {specs.filter(([, v]) => v).map(([k, v]) => (
              <View key={k} style={styles.spec}>
                <T style={styles.specKey}>{k}</T>
                <T style={styles.specVal}>{v}</T>
              </View>
            ))}
          </View>

          <T style={styles.h}>الوصف</T>
          <T style={styles.desc}>{l.description}</T>

          <Button label="مشاركة العقار" outline onPress={() => shareListing(l)} style={{ marginTop: 20 }} />
        </View>
      </ScrollView>

      <View style={styles.bar}>
        <Button label="واتساب" color={colors.whatsapp} onPress={() => whatsapp(listingMessage(l))} style={{ flex: 1 }} />
        <Button label="اتصال" onPress={call} style={{ flex: 1 }} />
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
  price: { fontSize: 24, fontWeight: '800', color: colors.primary },
  title: { fontSize: 19, fontWeight: '700', marginTop: 4 },
  meta: { color: colors.muted, marginTop: 6 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 16, marginHorizontal: -5 },
  spec: {
    width: '50%', padding: 5,
  },
  specKey: {
    fontSize: 12, color: colors.muted, backgroundColor: colors.card, borderTopLeftRadius: radius.sm, borderTopRightRadius: radius.sm,
    paddingHorizontal: 12, paddingTop: 10, borderWidth: 1, borderBottomWidth: 0, borderColor: colors.border,
  },
  specVal: {
    fontSize: 15, fontWeight: '700', backgroundColor: colors.card, borderBottomLeftRadius: radius.sm,
    borderBottomRightRadius: radius.sm, paddingHorizontal: 12, paddingBottom: 10, paddingTop: 2, borderWidth: 1,
    borderTopWidth: 0, borderColor: colors.border,
  },
  h: { fontSize: 17, fontWeight: '700', marginTop: 20, marginBottom: 6 },
  desc: { lineHeight: 24, color: colors.text },
  bar: {
    position: 'absolute', bottom: 0, left: 0, right: 0, flexDirection: 'row', gap: 10, padding: 12,
    backgroundColor: colors.card, borderTopWidth: 1, borderColor: colors.border,
  },
});

function ageText(y: number) {
  if (y === 0) return 'جديد';
  if (y === 1) return 'سنة';
  if (y === 2) return 'سنتان';
  return y <= 10 ? `${y} سنوات` : `${y} سنة`;
}
