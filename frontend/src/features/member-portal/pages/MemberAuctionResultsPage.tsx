import React from 'react';
import { useTranslation } from 'react-i18next';

export const MemberAuctionResultsPage: React.FC = () => {
  const { t } = useTranslation('common');
  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('auction_results')}</h1>
      <p className="mt-2 text-gray-500 dark:text-gray-400">{t('auction_results_coming_soon')}</p>
    </div>
  );
};
