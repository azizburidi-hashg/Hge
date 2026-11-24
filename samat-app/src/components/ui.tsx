import { Pressable, StyleSheet, Text, TextProps, View, ViewStyle } from 'react-native';
import { colors, radius } from '../theme';
import { Listing, TYPE_ICON, TYPE_LABEL } from '../data/listings';

// Arabic text, right-aligned.
export function T({ style, ...rest }: TextProps) {
  return <Text {...rest} style={[styles.text, style]} />;
}

export function Chip({ label, active, onPress }: { label: string; active?: boolean; onPress: () => void }) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityState={{ selected: !!active }}
      style={[styles.chip, active && styles.chipActive]}
    >
      <T style={[styles.chipText, active && styles.chipTextActive]}>{label}</T>
    </Pressable>
  );
}

export function Button({
  label, onPress, color = colors.primary, outline, style,
}: { label: string; onPress: () => void; color?: string; outline?: boolean; style?: ViewStyle }) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      style={({ pressed }) => [
        styles.button,
        outline ? { borderColor: color, borderWidth: 1.5, backgroundColor: 'transparent' } : { backgroundColor: color },
        pressed && { opacity: 0.8 },
        style,
      ]}
    >
      <T style={[styles.buttonText, outline && { color }]}>{label}</T>
    </Pressable>
  );
}

// Stand-in for a property photo until real photos are added.
export function Photo({ listing, height }: { listing: Listing; height: number }) {
  return (
    <View style={[styles.photo, { height, backgroundColor: `hsl(${listing.hue}, 35%, 82%)` }]}>
      <Text style={{ fontSize: height * 0.32 }}>{TYPE_ICON[listing.type]}</Text>
      <T style={styles.photoLabel}>{TYPE_LABEL[listing.type]} · {listing.district}</T>
    </View>
  );
}

export function SectionTitle({ children }: { children: string }) {
  return <T style={styles.section}>{children}</T>;
}

const styles = StyleSheet.create({
  text: { color: colors.text, textAlign: 'right', writingDirection: 'rtl', fontSize: 15 },
  chip: {
    paddingHorizontal: 14, paddingVertical: 8, borderRadius: 999, backgroundColor: colors.card,
    borderWidth: 1, borderColor: colors.border, marginStart: 8,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { fontSize: 14, color: colors.text },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  button: { paddingVertical: 13, paddingHorizontal: 16, borderRadius: radius.md, alignItems: 'center', justifyContent: 'center' },
  buttonText: { color: '#fff', fontWeight: '700', fontSize: 16, textAlign: 'center' },
  photo: { width: '100%', alignItems: 'center', justifyContent: 'center' },
  photoLabel: { color: colors.primaryDark, fontSize: 13, marginTop: 4, textAlign: 'center' },
  section: { fontSize: 18, fontWeight: '700', marginBottom: 10, marginTop: 18, paddingHorizontal: 16 },
});
