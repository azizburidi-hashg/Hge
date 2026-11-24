# Samat Alsakan: the app

An iPhone and Android app (built with Expo / React Native) for Samat Al-Sakan real estate in Jeddah. Arabic, right-to-left.

## What it does
- **Home:** search box, property types, featured listings, latest listings
- **Properties:** search with filters (sale/rent, type, district, highest price) and sorting
- **Property page:** price, details, description, share, and **WhatsApp** and **Call** buttons with the property already named in the message
- **Favorites:** saved on the phone
- **Contact:** WhatsApp, both phone numbers, email, map, social accounts, FAL license, plus a form to **request a property** or **list your property**, sent to you on WhatsApp

## Listings update automatically
The app reads the listings straight from samat-alsakan.com every time it opens, when it comes back to the screen
(at most every 5 minutes), and when the user pulls down to refresh. Add, edit or remove a listing on the website and
the app shows it. **No new app version needed.** The last listings are saved on the phone, so the app still works
offline. A line at the bottom of the home screen says when the listings were last updated.

How it works: `src/data/remote.ts` reads the listings from the website's `app.js` (the same data the website itself
shows) and its photos from the website's `assets/` folder. If the website's code is ever restructured so the listings
can't be found, the app keeps showing the last listings it saved; tell your developer to update `remote.ts`.

`scripts/sync_listings.py` refreshes the copy built into the app. It is only shown on a phone's very first launch
while offline, so run it now and then before releasing a new version, but it is not needed for listing changes.

Contact details, the FAL license and CR number are in `src/config.ts`.

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
