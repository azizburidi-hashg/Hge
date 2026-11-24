# سمات السكن: the app

An iPhone and Android app (built with Expo / React Native) for Samat Al-Sakan real estate in Jeddah. Arabic, right-to-left.

## What it does
- **Home:** search box, property types, featured listings, latest listings
- **Properties:** search with filters (sale/rent, type, district, highest price) and sorting
- **Property page:** price, details, description, share, and **WhatsApp** and **Call** buttons with the property already named in the message
- **Favorites:** saved on the phone
- **Contact:** WhatsApp, call and email, plus a **"Request a property"** form that sends the buyer's request to you on WhatsApp

## Before publishing (must do)
1. `src/config.ts`: put in your real WhatsApp number, phone, email and FAL license number.
2. `src/data/listings.ts`: **the listings are made-up samples.** Replace them with your real listings and photos, or connect the app to your website.
3. `assets/`: replace the icon and splash images with your logo.

## Try it
```
npm install
npx expo start        # scan the QR code with the Expo Go app on your phone
```

## Publish to the App Store and Google Play
You need (and pay for) these accounts yourself:
- **Apple Developer Program**: $99 / year (developer.apple.com). Enroll as an organization with your commercial registration, which needs a D-U-N-S number.
- **Google Play Console**: $25 one time (play.google.com/console).
- **Expo account** (free, expo.dev). Its EAS service builds the iPhone app in the cloud, so you don't need a Mac.

Then:
```
npm install -g eas-cli
eas login
eas build:configure
eas build --platform all
eas submit --platform ios
eas submit --platform android
```
Apple reviews real estate apps more strictly when the app only repeats the website, so the native features here (favorites, request form, WhatsApp/call) help it pass review.
