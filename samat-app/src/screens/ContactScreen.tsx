import { useState } from 'react';
import { ScrollView, StyleSheet, TextInput, View } from 'react-native';
import { BUSINESS } from '../config';
import { colors, radius } from '../theme';
import { PropertyType, TYPE_LABEL } from '../data/listings';
import { Button, Chip, T } from '../components/ui';
import { call, email, whatsapp } from '../contact';

// "Request a property": the buyer describes what they want and it is sent to you on WhatsApp. No server needed.
export function ContactScreen() {
  const [name, setName] = useState('');
  const [type, setType] = useState<PropertyType>('apartment');
  const [district, setDistrict] = useState('');
  const [budget, setBudget] = useState('');
  const [notes, setNotes] = useState('');

  const send = () => {
    const lines = [
      'السلام عليكم، أبحث عن عقار:',
      name && `الاسم: ${name}`,
      `النوع: ${TYPE_LABEL[type]}`,
      district && `الحي المفضل: ${district}`,
      budget && `الميزانية: ${budget} ريال`,
      notes && `ملاحظات: ${notes}`,
    ].filter(Boolean);
    whatsapp(lines.join('\n'));
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 32 }} keyboardShouldPersistTaps="handled">
      <View style={styles.card}>
        <T style={styles.h}>{BUSINESS.nameAr}</T>
        <T style={styles.p}>تواصل معنا مباشرة وسيقوم فريقنا بخدمتك.</T>
        {BUSINESS.falLicense ? <T style={styles.p}>رخصة فال: {BUSINESS.falLicense}</T> : null}
        <View style={styles.row}>
          <Button label="واتساب" color={colors.whatsapp} onPress={() => whatsapp('السلام عليكم')} style={{ flex: 1 }} />
          <Button label="اتصال" onPress={call} style={{ flex: 1 }} />
        </View>
        <Button label="البريد الإلكتروني" outline onPress={email} style={{ marginTop: 10 }} />
      </View>

      <View style={styles.card}>
        <T style={styles.h}>اطلب عقارك</T>
        <T style={styles.p}>لم تجد ما تبحث عنه؟ أخبرنا بطلبك وسنبحث لك.</T>
        <Field label="الاسم" value={name} onChange={setName} />
        <T style={styles.label}>نوع العقار</T>
        <View style={styles.chips}>
          {(Object.keys(TYPE_LABEL) as PropertyType[]).map((t) => (
            <Chip key={t} label={TYPE_LABEL[t]} active={type === t} onPress={() => setType(t)} />
          ))}
        </View>
        <Field label="الحي المفضل" value={district} onChange={setDistrict} />
        <Field label="الميزانية (ريال)" value={budget} onChange={setBudget} numeric />
        <Field label="ملاحظات" value={notes} onChange={setNotes} multiline />
        <Button label="إرسال الطلب عبر واتساب" color={colors.whatsapp} onPress={send} style={{ marginTop: 14 }} />
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
  p: { color: colors.muted, marginTop: 4, lineHeight: 22 },
  row: { flexDirection: 'row', gap: 10, marginTop: 14 },
  label: { fontSize: 13, color: colors.muted, marginTop: 12, marginBottom: 6 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginStart: -8 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: radius.sm, paddingHorizontal: 12, paddingVertical: 10,
    fontSize: 15, textAlign: 'right', writingDirection: 'rtl', color: colors.text, backgroundColor: colors.bg,
  },
});
