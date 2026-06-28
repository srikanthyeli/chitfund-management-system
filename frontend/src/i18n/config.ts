import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation resources
import enCommon from './locales/en/common.json';
import enAuth from './locales/en/auth.json';
import enDashboard from './locales/en/dashboard.json';
import enMembers from './locales/en/members.json';
import enOrganisers from './locales/en/organisers.json';
import enChitGroups from './locales/en/chitGroups.json';
import enCollections from './locales/en/collections.json';
import enAuctions from './locales/en/auctions.json';
import enPayouts from './locales/en/payouts.json';
import enReports from './locales/en/reports.json';
import enBondCalculator from './locales/en/bondCalculator.json';
import enSettings from './locales/en/settings.json';
import enValidation from './locales/en/validation.json';

import teCommon from './locales/te/common.json';
import teAuth from './locales/te/auth.json';
import teDashboard from './locales/te/dashboard.json';
import teMembers from './locales/te/members.json';
import teOrganisers from './locales/te/organisers.json';
import teChitGroups from './locales/te/chitGroups.json';
import teCollections from './locales/te/collections.json';
import teAuctions from './locales/te/auctions.json';
import tePayouts from './locales/te/payouts.json';
import teReports from './locales/te/reports.json';
import teBondCalculator from './locales/te/bondCalculator.json';
import teSettings from './locales/te/settings.json';
import teValidation from './locales/te/validation.json';

// Define supported languages
export const SUPPORTED_LANGUAGES = {
  en: { nativeName: 'English', code: 'en', isRTL: false },
  te: { nativeName: 'తెలుగు', code: 'te', isRTL: false },
} as const;

export type LanguageCode = keyof typeof SUPPORTED_LANGUAGES;

const resources = {
  en: {
    common: enCommon,
    auth: enAuth,
    dashboard: enDashboard,
    members: enMembers,
    organisers: enOrganisers,
    chitGroups: enChitGroups,
    collections: enCollections,
    auctions: enAuctions,
    payouts: enPayouts,
    reports: enReports,
    bondCalculator: enBondCalculator,
    settings: enSettings,
    validation: enValidation,
  },
  te: {
    common: teCommon,
    auth: teAuth,
    dashboard: teDashboard,
    members: teMembers,
    organisers: teOrganisers,
    chitGroups: teChitGroups,
    collections: teCollections,
    auctions: teAuctions,
    payouts: tePayouts,
    reports: teReports,
    bondCalculator: teBondCalculator,
    settings: teSettings,
    validation: teValidation,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    defaultNS: 'common',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
    react: {
      useSuspense: false, // Disable suspense to prevent hydration mismatch
    },
  });

export default i18n;
