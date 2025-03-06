import i18n from 'i18next';
import I18NextHttpBackend from 'i18next-http-backend';
import { initReactI18next } from 'react-i18next';

export const languageEn = 'en';
export const languageEnOverride = 'en-override';

const supportedLanguages = [languageEn, languageEnOverride]; // Add more languages here

export const defaultLanguage = languageEn;

const isDevMode = import.meta.env.MODE === 'development'; // If on dev and debug mode it will give us more insight on the translation

i18n
    // pass the i18n instance to react-i18next.
    .use(I18NextHttpBackend)
    .use(initReactI18next)
    // init i18next
    // for all options read: https://www.i18next.com/overview/configuration-options
    .init({
        lng: languageEnOverride,
        fallbackLng: defaultLanguage,
        supportedLngs: supportedLanguages,
        debug: isDevMode,
        nsSeparator: false,
        keySeparator: false,
        missingKeyNoValueFallbackToKey: true,
        interpolation: {
            escapeValue: false, // not needed for react as it escapes by default
        },
        react: {
            useSuspense: true,
        },
        returnEmptyString: false,
    })
    .catch(() => null);

export default i18n;
