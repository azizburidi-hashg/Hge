import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, TextInput, View } from 'react-native';
import { BUSINESS } from '../config';
import { colors, radius } from '../theme';
import { TYPES } from '../data/listings';
import { Button, Chip, T } from '../components/ui';
import { call, email, open, whatsapp } from '../contact';

type Mode = 'want' | 'offer';

// The buyer's request (or a property someone wants to list) is sent to the office on WhatsApp. No server needed.
export function ContactScreen() {
  const [mode, setMode] = useState<Mode>('want');
  const [name, setName] = useState('');
  const [type, setType] = useState(TYPES[0] ?? 'أرض');
  const [where, setWhere] = useState('');
  const [area, setArea] = useState('');
  const [budget, setBudget] = useState('');
  const [notes, setNotes] = useState('');

  const send = () => {
    const lines = [
      mode === 'want' ? 'السلام عليكم، أبحث عن عقار:' : 'السلام عليكم، أرغب بعرض عقاري لديكم:',
      name && `الاسم: ${name}`,
      `النوع: ${type}`,
      where && `${mode === 'want' ? 'الموقع المفضل' : 'الموقع'}: ${where}`,
      area && `المساحة: ${area} م²`,
      budget && `${mode === 'want' ? 'الميزانية' : 'السعر المطلوب'}: ${budget} ريال`,
      notes && `ملاحظات: ${notes}`,
    ].filter(Boolean);
    whatsapp(lines.join('\n'));
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 32 }} keyboardShouldPersistTaps="handled">
      <View style={styles.card}>
        <T style={styles.h}>{BUSINESS.nameAr} {BUSINESS.subtitleAr}</T>
        <T style={styles.p}>وساطة عقارية · تسويق عقاري · إدارة أملاك · تطوير عقاري</T>
        <View style={styles.row}>
          <Button label="واتساب" color={colors.whatsapp} onPress={() => whatsapp('السلام عليكم')} style={{ flex: 1 }} />
          <Button label="البريد" outline onPress={email} style={{ flex: 1 }} />
        </View>
        {BUSINESS.phones.map((p) => (
          <Button key={p} label={`اتصال  ${p.replace('+966', '0')}`} onPress={() => call(p)} style={{ marginTop: 10 }} />
        ))}
        <Button label="موقع المكتب على الخريطة" outline onPress={() => open(BUSINESS.mapUrl)} style={{ marginTop: 10 }} />
        <View style={styles.social}>
          {BUSINESS.social.map((s) => (
            <Pressable key={s.label} onPress={() => open(s.url)} style={styles.socialItem} accessibilityRole="link">
              <T style={styles.socialText}>{s.label}</T>
            </Pressable>
          ))}
        </View>
        <T style={styles.legal}>ترخيص فال: {BUSINESS.falLicense} · سجل تجاري: {BUSINESS.commercialRegistration}</T>
      </View>

      <View style={styles.card}>
        <View style={styles.tabs}>
          <Chip label="أبحث عن عقار" active={mode === 'want'} onPress={() => setMode('want')} />
          <Chip label="أضف عقارك" active={mode === 'offer'} onPress={() => setMode('offer')} />
        </View>
        <T style={styles.p}>
          {mode === 'want' ? 'لم تجد ما تبحث عنه؟ أخبرنا بطلبك وسنبحث لك.' : 'لديك عقار للبيع أو الإيجار؟ أرسل تفاصيله وسنتواصل معك.'}
        </T>
        <Field label="الاسم" value={name} onChange={setName} />
        <T style={styles.label}>نوع العقار</T>
        <View style={styles.chips}>
          {TYPES.map((t) => <Chip key={t} label={t} active={type === t} onPress={() => setType(t)} />)}
        </View>
        <Field label={mode === 'want' ? 'الحي أو المدينة المفضلة' : 'الحي والمدينة'} value={where} onChange={setWhere} />
        <Field label="المساحة (م²)" value={area} onChange={setArea} numeric />
        <Field label={mode === 'want' ? 'الميزانية (ريال)' : 'السعر المطلوب (ريال)'} value={budget} onChange={setBudget} numeric />
        <Field label="ملاحظات" value={notes} onChange={setNotes} multiline />
        <Button label="إرسال عبر واتساب" color={colors.whatsapp} onPress={send} style={{ marginTop: 14 }} />
      </View>
    </ScrollView>
  );
}

function Field({ label, value, onChange, numeric, multiline }: {
  label: string; value: string; onChange: (v: string) => void; numeric?: boolean; multiline?: boolean;
}) {
  return (
    <View>
      <T style={styles.label}>{label}</T>
      <TextInput
        value={value}
        onChangeText={onChange}
        keyboardType={numeric ? 'number-pad' : 'default'}
        multiline={multiline}
        accessibilityLabel={label}
        style={[styles.input, multiline && { minHeight: 80, textAlignVertical: 'top' }]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card, borderRadius: radius.lg, padding: 16, marginBottom: 16, borderWidth: 1, borderColor: colors.border,
  },
  h: { fontSize: 19, fontWeight: '800', color: colors.primary },
  p: { color: colors.muted, marginTop: 6, lineHeight: 22 },
  row: { flexDirection: 'row', gap: 10, marginTop: 14 },
  tabs: { flexDirection: 'row', marginStart: -8 },
  social: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 14 },
  socialItem: { paddingHorizontal: 12, paddingVertical: 7, borderRadius: 999, backgroundColor: colors.bg },
  socialText: { fontSize: 13, color: colors.primary, fontWeight: '600' },
  legal: { fontSize: 12, color: colors.muted, marginTop: 14 },
  label: { fontSize: 13, color: colors.muted, marginTop: 12, marginBottom: 6 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginStart: -8 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: radius.sm, paddingHorizontal: 12, paddingVertical: 10,
    fontSize: 15, textAlign: 'right', writingDirection: 'rtl', color: colors.text, backgroundColor: colors.bg,
  },
});
