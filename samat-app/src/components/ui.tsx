import { Image, Pressable, StyleSheet, Text, TextProps, useWindowDimensions, ViewStyle } from 'react-native';
import { colors, radius } from '../theme';
import type { Listing } from '../data/listings';

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

// The listing's photo (the poster from the website).
export function Photo({ listing, height, full }: { listing: Listing; height?: number; full?: boolean }) {
  const { width } = useWindowDimensions();
  if (full) {
    return (
      <Image
        source={listing.image}
        accessibilityLabel={listing.title}
        style={{ width: '100%', height: width / (listing.imageRatio || 3 / 4), backgroundColor: colors.border }}
        resizeMode="contain"
      />
    );
  }
  return (
    <Image
      source={listing.image}
      accessibilityLabel={listing.title}
      style={{ width: '100%', height, backgroundColor: colors.border }}
      resizeMode="cover"
    />
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
  section: { fontSize: 18, fontWeight: '700', marginBottom: 10, marginTop: 18, paddingHorizontal: 16 },
});
