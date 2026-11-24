# Samat Alsakan: the app

An iPhone and Android app (built with Expo / React Native) for Samat Al-Sakan real estate in Jeddah. Arabic, right-to-left.

## What it does
- **Home:** search box, property types, featured listings, latest listings
- **Properties:** search with filters (sale/rent, type, district, highest price) and sorting
- **Property page:** price, details, description, share, and **WhatsApp** and **Call** buttons with the property already named in the message
- **Favorites:** saved on the phone
- **Contact:** WhatsApp, both phone numbers, email, map, social accounts, FAL license, plus a form to **request a property** or **list your property**, sent to you on WhatsApp

## Listings come from the website
All listings and their posters are copied from samat-alsakan.com. When you add or change listings on the website, run:
```
python3 scripts/sync_listings.py
```
then build and submit a new version of the app. Contact details, the FAL license and CR number are in `src/config.ts`.

## Before publishing
- `assets/icon.png` is a simple "SA" placeholder icon. Replace it with your logo (1024x1024 PNG).

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
