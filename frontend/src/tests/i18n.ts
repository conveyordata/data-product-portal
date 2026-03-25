import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
    lng: 'en',
    fallbackLng: 'en',
    ns: ['translation'],
    defaultNS: 'translation',
    nsSeparator: false,
    keySeparator: false,
    interpolation: { escapeValue: false },
    resources: { en: { translation: {} } },
    react: { useSuspense: false },
});

export default i18n;
