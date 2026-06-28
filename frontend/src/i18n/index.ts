import './config';
import i18n from 'i18next';

const updateDocumentLanguage = (lang: string) => {
  document.documentElement.lang = lang;
  document.documentElement.dir = ['ar', 'he', 'fa', 'ur'].includes(lang) ? 'rtl' : 'ltr';
};

updateDocumentLanguage(i18n.language || 'en');
i18n.on('languageChanged', updateDocumentLanguage);

export default i18n;
