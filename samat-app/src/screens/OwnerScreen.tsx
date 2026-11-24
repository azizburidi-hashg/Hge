// The owner's private area: sign in, then add, edit, hide or delete listings and offers.
// Changes go to Supabase and appear in everyone's app on their next refresh. No app update needed.
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Alert, Image, Platform, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { colors, radius } from '../theme';
import { PURPOSE_LABEL, Purpose } from '../data/listings';
import { useListings } from '../data/store';
import {
  currentOwner, deleteListing, fetchAll, ownerEnabled, Row, RowInput, saveListing, signIn, signOut, uploadPhoto,
} from '../data/owner';
import { Button, Chip, T } from '../components/ui';

const COMMON_TYPES = ['أرض', 'فيلا', 'شقة', 'عمارة', 'دور', 'فندق', 'تجاري'];
const CITIES = ['جدة', 'مكة المكرمة', 'المدينة المنورة', 'الطائف', 'الرياض'];

function confirm(message: string): Promise<boolean> {
  if (Platform.OS === 'web') return Promise.resolve(window.confirm(message));
  return new Promise((done) =>
    Alert.alert(message, undefined, [
      { text: 'إلغاء', style: 'cancel', onPress: () => done(false) },
      { text: 'نعم', style: 'destructive', onPress: () => done(true) },
    ]));
}
function notify(message: string) {
  if (Platform.OS === 'web') window.alert(message);
  else Alert.alert(message);
}

export function OwnerScreen({ onClose }: { onClose: () => void }) {
  const [email, setEmail] = useState<string | null | undefined>(undefined);
  const [editing, setEditing] = useState<Row | 'new' | null>(null);

  useEffect(() => {
    currentOwner().then(setEmail).catch(() => setEmail(null));
  }, []);

  let body;
  if (!ownerEnabled()) body = <NotSetUp />;
  else if (email === undefined) body = <ActivityIndicator style={{ marginTop: 40 }} color={colors.primary} />;
  else if (!email) body = <Login onDone={setEmail} />;
  else if (editing) body = <Editor row={editing === 'new' ? null : editing} onDone={() => setEditing(null)} />;
  else body = <MyListings email={email} onEdit={setEditing} onSignOut={async () => { await signOut(); setEmail(null); }} />;

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={styles.header}>
        <Pressable onPress={editing ? () => setEditing(null) : onClose} accessibilityRole="button" accessibilityLabel="رجوع" hitSlop={10}>
          <Text style={{ fontSize: 22, color: colors.primary }}>→</Text>
        </Pressable>
        <T style={styles.headerText}>{editing === 'new' ? 'إضافة عقار' : editing ? 'تعديل العقار' : 'لوحة المالك'}</T>
      </View>
      {body}
    </View>
  );
}

function NotSetUp() {
  return (
    <View style={styles.pad}>
      <T style={styles.p}>لوحة المالك غير مفعّلة بعد. أضف بيانات مشروع Supabase في الملف src/config.ts (راجع README).</T>
    </View>
  );
}

function Login({ onDone }: { onDone: (email: string) => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const go = async () => {
    setBusy(true);
    setError('');
    try {
      onDone(await signIn(email, password));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <ScrollView contentContainerStyle={styles.pad} keyboardShouldPersistTaps="handled">
      <View style={styles.card}>
        <T style={styles.h}>تسجيل دخول المالك</T>
        <T style={styles.p}>لإضافة العقارات والعروض وتعديلها.</T>
        <Field label="البريد الإلكتروني" value={email} onChange={setEmail} keyboard="email-address" />
        <Field label="كلمة المرور" value={password} onChange={setPassword} secure />
        {error ? <T style={styles.error}>{error}</T> : null}
        <Button label={busy ? 'جارٍ الدخول…' : 'دخول'} onPress={busy ? () => {} : go} style={{ marginTop: 16 }} />
      </View>
    </ScrollView>
  );
}

function MyListings({ email, onEdit, onSignOut }: { email: string; onEdit: (r: Row | 'new') => void; onSignOut: () => void }) {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [error, setError] = useState('');
  const load = useCallback(() => {
    setError('');
    fetchAll().then(setRows).catch((e) => setError((e as Error).message));
  }, []);
  useEffect(load, [load]);

  return (
    <ScrollView contentContainerStyle={styles.pad}>
      <Button label="＋ إضافة عقار أو عرض جديد" color={colors.accent} onPress={() => onEdit('new')} />
      {error ? <T style={styles.error}>{error}</T> : null}
      {!rows && !error ? <ActivityIndicator style={{ marginTop: 24 }} color={colors.primary} /> : null}
      {rows && !rows.length ? <T style={[styles.p, { textAlign: 'center', marginTop: 24 }]}>لم تضف أي عقار بعد.</T> : null}
      {rows?.map((r) => (
        <Pressable key={r.id} onPress={() => onEdit(r)} style={styles.item} accessibilityRole="button">
          {r.photos[0] ? <Image source={{ uri: r.photos[0] }} style={styles.thumb} /> : <View style={[styles.thumb, { backgroundColor: colors.border }]} />}
          <View style={{ flex: 1 }}>
            <T style={styles.itemTitle} numberOfLines={2}>{r.title}</T>
            <T style={styles.itemMeta}>
              {[PURPOSE_LABEL[r.purpose], r.type, r.published ? 'منشور' : 'مخفي', r.is_offer ? 'عرض خاص' : '', r.pinned ? 'مثبّت' : '']
                .filter(Boolean).join(' · ')}
            </T>
          </View>
        </Pressable>
      ))}
      <T style={[styles.p, { marginTop: 24, textAlign: 'center' }]}>
        العقارات المنشورة هنا تظهر في التطبيق أولاً، قبل عقارات الموقع. {'\n'}مسجّل باسم {email}
      </T>
      <Button label="تسجيل الخروج" outline onPress={onSignOut} style={{ marginTop: 10 }} />
    </ScrollView>
  );
}

const EMPTY: RowInput = {
  published: true, pinned: false, title: '', type: 'أرض', purpose: 'sale', city: 'جدة', location: '',
  price: null, price_text: '', area: null, rooms: null, baths: null, description: '', details: [], photos: [],
  photo_ratio: null, is_offer: false, offer_text: '', old_price: null, offer_ends: null,
};

const numOrNull = (s: string) => {
  const t = s.replace(/[,\s]/g, '').replace(/[٠-٩]/g, (d) => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d)));
  return t && !Number.isNaN(Number(t)) ? Number(t) : null;
};
const str = (n: number | null) => (n === null || n === undefined ? '' : String(n));

function Editor({ row, onDone }: { row: Row | null; onDone: () => void }) {
  const { refresh } = useListings();
  const init = row ? { ...EMPTY, ...row } : EMPTY;
  const [f, setF] = useState<RowInput>(init);
  const [nums, setNums] = useState({
    price: str(init.price), area: str(init.area), rooms: str(init.rooms), baths: str(init.baths), old_price: str(init.old_price),
  });
  const [detailsText, setDetailsText] = useState(init.details.join('\n'));
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const set = <K extends keyof RowInput>(k: K, v: RowInput[K]) => setF((x) => ({ ...x, [k]: v }));
  const setNum = (k: keyof typeof nums, v: string) => setNums((x) => ({ ...x, [k]: v }));

  const suggestTitle = () => {
    const what = f.purpose === 'wanted' ? `${f.type} مطلوب` : `${f.type} ${PURPOSE_LABEL[f.purpose]}`;
    set('title', `${what}${f.location ? ` في ${f.location}` : ''}${f.city ? ` – ${f.city}` : ''}`);
  };

  const addPhotos = async () => {
    if (Platform.OS !== 'web') {
      const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!perm.granted) return notify('اسمح للتطبيق بالوصول إلى الصور من الإعدادات.');
    }
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'], allowsMultipleSelection: true, selectionLimit: 10, quality: 0.7,
    });
    if (res.canceled) return;
    setBusy('جارٍ رفع الصور…');
    setError('');
    try {
      const urls: string[] = [];
      for (const a of res.assets) urls.push(await uploadPhoto(a.uri, a.mimeType ?? 'image/jpeg'));
      setF((x) => {
        const first = res.assets[0];
        const ratio = x.photos.length ? x.photo_ratio : first.width && first.height ? +(first.width / first.height).toFixed(4) : null;
        return { ...x, photos: [...x.photos, ...urls], photo_ratio: ratio };
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy('');
    }
  };

  const removePhoto = (i: number) =>
    setF((x) => ({ ...x, photos: x.photos.filter((_, j) => j !== i), photo_ratio: i === 0 ? null : x.photo_ratio }));
  const makeCover = (i: number) =>
    setF((x) => ({ ...x, photos: [x.photos[i], ...x.photos.filter((_, j) => j !== i)], photo_ratio: null }));

  const save = async () => {
    const data: RowInput = {
      ...f,
      title: f.title.trim(),
      price: numOrNull(nums.price), area: numOrNull(nums.area), rooms: numOrNull(nums.rooms), baths: numOrNull(nums.baths),
      old_price: f.is_offer ? numOrNull(nums.old_price) : null,
      offer_text: f.is_offer ? f.offer_text.trim() : '',
      offer_ends: f.is_offer && /^\d{4}-\d{2}-\d{2}$/.test(f.offer_ends ?? '') ? f.offer_ends : null,
      details: detailsText.split('\n').map((s) => s.trim()).filter(Boolean),
    };
    if (data.title.length < 3) return setError('اكتب عنواناً للعقار');
    if (!data.type.trim()) return setError('اختر نوع العقار');
    if (data.published && !data.photos.length && !(await confirm('لا توجد صور. نشر العقار بدون صور؟'))) return;
    setBusy('جارٍ الحفظ…');
    setError('');
    try {
      await saveListing(data, row?.id);
      refresh();
      notify(data.published ? 'تم الحفظ والنشر. سيظهر لكل المستخدمين خلال دقائق.' : 'تم الحفظ (مخفي).');
      onDone();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy('');
    }
  };

  const remove = async () => {
    if (!row || !(await confirm('حذف هذا العقار نهائياً مع صوره؟'))) return;
    setBusy('جارٍ الحذف…');
    try {
      await deleteListing(row);
      refresh();
      onDone();
    } catch (e) {
      setError((e as Error).message);
      setBusy('');
    }
  };

  return (
    <ScrollView contentContainerStyle={[styles.pad, { paddingBottom: 60 }]} keyboardShouldPersistTaps="handled">
      <View style={styles.card}>
        <T style={styles.label}>العرض</T>
        <View style={styles.chips}>
          {(['sale', 'rent', 'wanted'] as Purpose[]).map((p) => (
            <Chip key={p} label={PURPOSE_LABEL[p]} active={f.purpose === p} onPress={() => set('purpose', p)} />
          ))}
        </View>
        <T style={styles.label}>نوع العقار</T>
        <View style={styles.chips}>
          {COMMON_TYPES.map((t) => <Chip key={t} label={t} active={f.type === t} onPress={() => set('type', t)} />)}
        </View>
        <Field label="أو اكتب نوعاً آخر" value={COMMON_TYPES.includes(f.type) ? '' : f.type} onChange={(v) => set('type', v || 'أرض')} />
        <T style={styles.label}>المدينة</T>
        <View style={styles.chips}>
          {CITIES.map((c) => <Chip key={c} label={c} active={f.city === c} onPress={() => set('city', c)} />)}
        </View>
        <Field label="الحي أو الموقع" value={f.location} onChange={(v) => set('location', v)} placeholder="مثال: حي الشاطئ" />
        <Field label="العنوان" value={f.title} onChange={(v) => set('title', v)} />
        <Pressable onPress={suggestTitle} accessibilityRole="button"><T style={styles.link}>اقتراح عنوان تلقائي</T></Pressable>
      </View>

      <View style={styles.card}>
        <T style={styles.h2}>الصور</T>
        <T style={styles.p}>الصورة الأولى هي الغلاف. اضغط على صورة لجعلها الغلاف.</T>
        <ScrollView horizontal contentContainerStyle={{ gap: 8, paddingVertical: 10 }}>
          {f.photos.map((u, i) => (
            <View key={u}>
              <Pressable onPress={() => makeCover(i)} accessibilityLabel={`صورة ${i + 1}`}>
                <Image source={{ uri: u }} style={[styles.photo, i === 0 && { borderColor: colors.accent, borderWidth: 3 }]} />
              </Pressable>
              <Pressable onPress={() => removePhoto(i)} style={styles.x} accessibilityRole="button" accessibilityLabel="حذف الصورة">
                <Text style={{ color: '#fff', fontWeight: '800' }}>×</Text>
              </Pressable>
            </View>
          ))}
        </ScrollView>
        <Button label="＋ إضافة صور" outline onPress={busy ? () => {} : addPhotos} />
      </View>

      <View style={styles.card}>
        <T style={styles.h2}>السعر والمساحة</T>
        <Field label="السعر (ريال)" value={nums.price} onChange={(v) => setNum('price', v)} numeric placeholder="اتركه فارغاً = السعر عند الطلب" />
        <Field label="أو نص السعر" value={f.price_text} onChange={(v) => set('price_text', v)} placeholder="مثال: 7,000 ريال للمتر" />
        <Field label="المساحة (م²)" value={nums.area} onChange={(v) => setNum('area', v)} numeric />
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <View style={{ flex: 1 }}><Field label="الغرف" value={nums.rooms} onChange={(v) => setNum('rooms', v)} numeric /></View>
          <View style={{ flex: 1 }}><Field label="دورات المياه" value={nums.baths} onChange={(v) => setNum('baths', v)} numeric /></View>
        </View>
      </View>

      <View style={styles.card}>
        <Toggle label="🏷️ عرض خاص" value={f.is_offer} onChange={(v) => set('is_offer', v)} />
        {f.is_offer ? (
          <>
            <Field label="نص العرض" value={f.offer_text} onChange={(v) => set('offer_text', v)} placeholder="مثال: خصم لفترة محدودة" />
            <Field label="السعر قبل العرض (يظهر مشطوباً)" value={nums.old_price} onChange={(v) => setNum('old_price', v)} numeric />
            <Field label="ينتهي العرض في (YYYY-MM-DD)" value={f.offer_ends ?? ''} onChange={(v) => set('offer_ends', v)} placeholder="اختياري، مثال: 2026-12-31" />
          </>
        ) : null}
      </View>

      <View style={styles.card}>
        <Field label="الوصف" value={f.description} onChange={(v) => set('description', v)} multiline />
        <Field label="تفاصيل إضافية (كل سطر نقطة)" value={detailsText} onChange={setDetailsText} multiline />
      </View>

      <View style={styles.card}>
        <Toggle label="منشور (يظهر للجميع)" value={f.published} onChange={(v) => set('published', v)} />
        <Toggle label="تثبيت في الأعلى" value={f.pinned} onChange={(v) => set('pinned', v)} />
      </View>

      {error ? <T style={styles.error}>{error}</T> : null}
      {busy ? <T style={[styles.p, { textAlign: 'center' }]}>{busy}</T> : null}
      <Button label="حفظ" onPress={busy ? () => {} : save} style={{ marginTop: 6 }} />
      {row ? <Button label="حذف العقار" outline color={colors.danger} onPress={busy ? () => {} : remove} style={{ marginTop: 10 }} /> : null}
    </ScrollView>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <View style={styles.toggle}>
      <T style={{ fontWeight: '700', flex: 1 }}>{label}</T>
      <Switch value={value} onValueChange={onChange} trackColor={{ true: colors.accent, false: colors.border }} accessibilityLabel={label} />
    </View>
  );
}

function Field({ label, value, onChange, numeric, multiline, secure, keyboard, placeholder }: {
  label: string; value: string; onChange: (v: string) => void; numeric?: boolean; multiline?: boolean; secure?: boolean;
  keyboard?: 'email-address'; placeholder?: string;
}) {
  return (
    <View>
      <T style={styles.label}>{label}</T>
      <TextInput
        value={value}
        onChangeText={onChange}
        keyboardType={numeric ? 'decimal-pad' : keyboard ?? 'default'}
        autoCapitalize={keyboard || secure ? 'none' : 'sentences'}
        secureTextEntry={secure}
        multiline={multiline}
        placeholder={placeholder}
        placeholderTextColor={colors.muted}
        accessibilityLabel={label}
        style={[styles.input, multiline && { minHeight: 90, textAlignVertical: 'top' }, (keyboard || secure) && { textAlign: 'left', writingDirection: 'ltr' }]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 16, paddingVertical: 14,
    backgroundColor: colors.card, borderBottomWidth: 1, borderColor: colors.border,
  },
  headerText: { fontSize: 20, fontWeight: '800' },
  pad: { padding: 16 },
  card: { backgroundColor: colors.card, borderRadius: radius.lg, padding: 16, marginBottom: 14, borderWidth: 1, borderColor: colors.border },
  h: { fontSize: 19, fontWeight: '800', color: colors.primary },
  h2: { fontSize: 16, fontWeight: '800', color: colors.primary },
  p: { color: colors.muted, marginTop: 4, lineHeight: 22 },
  error: { color: colors.danger, marginTop: 10, fontWeight: '600' },
  label: { fontSize: 13, color: colors.muted, marginTop: 12, marginBottom: 6 },
  link: { color: colors.teal, fontWeight: '700', marginTop: 8 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginStart: -8 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: radius.sm, paddingHorizontal: 12, paddingVertical: 10,
    fontSize: 15, textAlign: 'right', writingDirection: 'rtl', color: colors.text, backgroundColor: colors.bg,
  },
  item: {
    flexDirection: 'row', gap: 12, alignItems: 'center', backgroundColor: colors.card, borderRadius: radius.md, padding: 10,
    marginTop: 10, borderWidth: 1, borderColor: colors.border,
  },
  thumb: { width: 64, height: 64, borderRadius: radius.sm },
  itemTitle: { fontWeight: '700', color: colors.primary },
  itemMeta: { fontSize: 12, color: colors.muted, marginTop: 4 },
  photo: { width: 110, height: 110, borderRadius: radius.sm, backgroundColor: colors.border },
  x: {
    position: 'absolute', top: 4, end: 4, width: 26, height: 26, borderRadius: 999, backgroundColor: 'rgba(0,0,0,0.6)',
    alignItems: 'center', justifyContent: 'center',
  },
  toggle: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6 },
});
