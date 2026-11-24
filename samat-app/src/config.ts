// Your Supabase project (Dashboard > Project Settings > API). Both values are safe to ship in the app.
// Paste them in place of the '' below (or set them in .env, see .env.example). Empty = owner section off.
export const SUPABASE = {
  url: process.env.EXPO_PUBLIC_SUPABASE_URL || '', // e.g. https://abcdefgh.supabase.co
  anonKey: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '', // the "anon public" key
};

// Business details, as shown on samat-alsakan.com.
export const BUSINESS = {
  appName: 'Samat Alsakan',
  nameAr: 'سمات السكن',
  subtitleAr: 'للاستثمار العقاري',
  taglineAr: 'نقدم العقار بصورة تليق بقيمته، ونصنع لكل فرصة حضوراً يلفت الانتباه ويقود إلى القرار الصحيح.',
  whatsapp: '966555282922', // digits only, international format
  phones: ['+966555282922', '+966559955075'],
  email: 'Sematalsakan@hotmail.com',
  website: 'https://samat-alsakan.com',
  falLicense: '1100304235',
  commercialRegistration: '7052161564',
  mapUrl: 'https://maps.app.goo.gl/Evt2CyFEZKeCjdh99',
  social: [
    { label: 'Instagram', url: 'https://www.instagram.com/samatalsakan' },
    { label: 'X', url: 'https://x.com/samatAlsakan' },
    { label: 'Snapchat', url: 'https://www.snapchat.com/add/samatalsakan' },
    { label: 'TikTok', url: 'https://www.tiktok.com/@samatalsakan' },
    { label: 'Telegram', url: 'https://t.me/jeddah3qarat' },
  ],
};
