import { useEffect, useState } from 'react';
import { BackHandler, Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { colors } from './src/theme';
import { ListingsProvider, useListings } from './src/data/store';
import { useFavorites } from './src/favorites';
import { T } from './src/components/ui';
import { HomeScreen } from './src/screens/HomeScreen';
import { SearchScreen } from './src/screens/SearchScreen';
import { DetailScreen } from './src/screens/DetailScreen';
import { FavoritesScreen } from './src/screens/FavoritesScreen';
import { ContactScreen } from './src/screens/ContactScreen';
import type { SearchParams } from './src/screens/types';

type Tab = 'home' | 'search' | 'favorites' | 'contact';
const TABS: { key: Tab; label: string; icon: string }[] = [
  { key: 'home', label: 'الرئيسية', icon: '🏠' },
  { key: 'search', label: 'العقارات', icon: '🔍' },
  { key: 'favorites', label: 'المفضلة', icon: '♥' },
  { key: 'contact', label: 'تواصل', icon: '💬' },
];

if (Platform.OS === 'web' && typeof document !== 'undefined') {
  document.documentElement.dir = 'rtl';
  document.documentElement.lang = 'ar';
}

export default function App() {
  return (
    <ListingsProvider>
      <Main />
    </ListingsProvider>
  );
}

function Main() {
  const { listings } = useListings();
  const [tab, setTab] = useState<Tab>('home');
  const [openId, setOpenId] = useState<string | null>(null);
  const [search, setSearch] = useState<{ params: SearchParams; key: number }>({ params: {}, key: 0 });
  const fav = useFavorites();

  // Android back button closes a listing before leaving the app.
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (openId) { setOpenId(null); return true; }
      if (tab !== 'home') { setTab('home'); return true; }
      return false;
    });
    return () => sub.remove();
  }, [openId, tab]);

  const goSearch = (params: SearchParams) => {
    setSearch((s) => ({ params, key: s.key + 1 }));
    setOpenId(null);
    setTab('search');
  };
  const props = { openListing: setOpenId, fav, goSearch };
  const listing = openId ? listings.find((l) => l.id === openId) : undefined;

  return (
    <SafeAreaProvider>
      <StatusBar style={listing ? 'dark' : tab === 'home' ? 'light' : 'dark'} />
      <SafeAreaView
        edges={['top']}
        style={[styles.root, { backgroundColor: !listing && tab === 'home' ? colors.primary : colors.bg }]}
      >
        <View style={styles.content}>
          {listing ? (
            <DetailScreen listing={listing} fav={fav} onBack={() => setOpenId(null)} />
          ) : (
            <>
              {tab !== 'home' && (
                <View style={styles.header}>
                  <T style={styles.headerText}>{TABS.find((t) => t.key === tab)!.label}</T>
                </View>
              )}
              {tab === 'home' && <HomeScreen {...props} />}
              {tab === 'search' && <SearchScreen key={search.key} initial={search.params} {...props} />}
              {tab === 'favorites' && <FavoritesScreen {...props} />}
              {tab === 'contact' && <ContactScreen />}
            </>
          )}
        </View>
        {!listing && (
          <SafeAreaView edges={['bottom']} style={styles.tabBar}>
            {TABS.map((t) => {
              const active = t.key === tab;
              return (
                <Pressable
                  key={t.key}
                  onPress={() => setTab(t.key)}
                  style={styles.tab}
                  accessibilityRole="tab"
                  accessibilityState={{ selected: active }}
                  accessibilityLabel={t.label}
                >
                  <Text style={[styles.tabIcon, { opacity: active ? 1 : 0.45 }]}>{t.icon}</Text>
                  <T style={[styles.tabLabel, active && { color: colors.primary, fontWeight: '700' }]}>
                    {t.label}
                    {t.key === 'favorites' && fav.ids.length ? ` (${fav.ids.length})` : ''}
                  </T>
                </Pressable>
              );
            })}
          </SafeAreaView>
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, direction: 'rtl' },
  content: { flex: 1, backgroundColor: colors.bg },
  header: { paddingHorizontal: 16, paddingVertical: 14, backgroundColor: colors.card, borderBottomWidth: 1, borderColor: colors.border },
  headerText: { fontSize: 20, fontWeight: '800' },
  tabBar: { flexDirection: 'row', backgroundColor: colors.card, borderTopWidth: 1, borderColor: colors.border },
  tab: { flex: 1, alignItems: 'center', paddingTop: 8, paddingBottom: 6 },
  tabIcon: { fontSize: 20, color: colors.primary },
  tabLabel: { fontSize: 12, color: colors.muted, textAlign: 'center', marginTop: 2 },
});
