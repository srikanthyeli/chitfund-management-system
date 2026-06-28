import React from 'react';
import { useTranslation } from 'react-i18next';

export const MyWinnerPayoutsPage: React.FC = () => {
  const { t } = useTranslation(['payouts']);

  return <div className="p-4 sm:p-6 max-w-7xl mx-auto"><h1 className="text-2xl font-bold">{t('payouts:payouts_title')}</h1><p>Winner Payouts coming soon.</p></div>;
};
