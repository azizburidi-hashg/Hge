import { Alert, Linking, Platform, Share } from 'react-native';
import { BUSINESS } from './config';
import { formatArea, formatPrice, Listing, place } from './data/listings';

export async function open(url: string) {
  try {
    await Linking.openURL(url);
  } catch {
    if (Platform.OS === 'web') window.alert('تعذّر فتح الرابط');
    else Alert.alert('تعذّر فتح الرابط');
  }
}

export const whatsapp = (message: string) =>
  open(`https://wa.me/${BUSINESS.whatsapp}?text=${encodeURIComponent(message)}`);

export const call = (phone: string = BUSINESS.phones[0]) => open(`tel:${phone}`);

export const email = () => open(`mailto:${BUSINESS.email}`);

export function listingMessage(l: Listing) {
  return `السلام عليكم، أرغب بالاستفسار عن: ${l.title}\n${l.url}`;
}

export async function shareListing(l: Listing) {
  const lines = [l.title, `📍 ${place(l)}`, `💰 ${formatPrice(l)}`, l.area ? `📐 ${formatArea(l.area)}` : '', '', l.url,
    `${BUSINESS.nameAr} ${BUSINESS.subtitleAr}`];
  try {
    await Share.share({ message: lines.filter((x, i) => x || i === 4).join('\n') });
  } catch {
    // cancelled
  }
}
