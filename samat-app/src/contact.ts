import { Alert, Linking, Platform, Share } from 'react-native';
import { BUSINESS } from './config';
import { formatPrice, Listing } from './data/listings';

async function open(url: string) {
  try {
    await Linking.openURL(url);
  } catch {
    if (Platform.OS === 'web') window.alert('تعذّر فتح الرابط');
    else Alert.alert('تعذّر فتح الرابط');
  }
}

export function whatsapp(message: string) {
  return open(`https://wa.me/${BUSINESS.whatsapp}?text=${encodeURIComponent(message)}`);
}

export function call() {
  return open(`tel:${BUSINESS.phone}`);
}

export function email() {
  return open(`mailto:${BUSINESS.email}`);
}

export function listingMessage(l: Listing) {
  return `السلام عليكم، أرغب بالاستفسار عن: ${l.title} في ${l.district} (${formatPrice(l)}) - رقم الإعلان ${l.id}`;
}

export async function shareListing(l: Listing) {
  const text = `${l.title}\n📍 ${l.district}، ${BUSINESS.city}\n💰 ${formatPrice(l)}\n📐 ${l.area} م²\n\n${BUSINESS.nameAr}`;
  try {
    await Share.share({ message: text });
  } catch {
    // user cancelled
  }
}
