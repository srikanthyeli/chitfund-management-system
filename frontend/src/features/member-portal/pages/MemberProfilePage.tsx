import React from 'react';
import { useTranslation } from 'react-i18next';

export const MemberProfilePage: React.FC = () => {
  const { t } = useTranslation(['common']);

  return <div className="p-4 sm:p-6 max-w-7xl mx-auto"><h1 className="text-2xl font-bold">{t('common:navigation_profile')}</h1><p>Profile coming soon.</p></div>;
};
