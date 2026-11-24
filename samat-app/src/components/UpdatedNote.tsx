import { colors } from '../theme';
import { useListings } from '../data/store';
import { T } from './ui';

// Small line telling the user how fresh the listings are.
export function UpdatedNote() {
  const { updatedAt, offline, refreshing } = useListings();
  let text = 'جارٍ تحديث العقارات…';
  if (!refreshing) {
    if (updatedAt) {
      const d = new Date(updatedAt);
      const time = d.toLocaleString('ar-SA-u-nu-latn', { dateStyle: 'medium', timeStyle: 'short' });
      text = `${offline ? 'لا يوجد اتصال · ' : ''}آخر تحديث: ${time}`;
    } else if (offline) {
      text = 'لا يوجد اتصال، اسحب للأسفل للتحديث';
    }
  }
  return <T style={{ textAlign: 'center', color: colors.muted, fontSize: 12, marginTop: 14 }}>{text}</T>;
}
