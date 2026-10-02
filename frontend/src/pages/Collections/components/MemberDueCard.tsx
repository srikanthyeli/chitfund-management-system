import React from 'react';
import { IndianRupee, CheckCircle2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { MoneyText } from '../../../components/common/MoneyText';
import { StatusChip } from '../../../components/common/StatusChip';

interface MemberDueCardProps {
  due: any;
  onCollect: (due: any) => void;
  onHistory: (due: any) => void;
}

export const MemberDueCard: React.FC<MemberDueCardProps> = ({ due, onCollect, onHistory }) => {
  const { t } = useTranslation(['collections', 'common']);

  const isPaid = due.payment_status === 'PAID';
  const bonusTotal = (due.bonus_per_share || 0) * (due.share_count || 0);

  return (
    <div className="rounded-2xl border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 overflow-hidden transition-all">
      {/* Top row */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0">
            <p className="font-semibold text-gray-900 dark:text-white text-base">{due.member_name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{due.member_phone || due.member_code}</p>
          </div>
          <StatusChip status={due.payment_status || 'PENDING'} />
        </div>

        {/* Plain words — not Gross/Net */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{t('collections:collections_installment')}</p>
            <MoneyText amount={due.gross_installment_amount} size="sm" showPaise className="text-gray-900 dark:text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{t('collections:collections_bonus')}</p>
            <MoneyText amount={bonusTotal} size="sm" showPaise prefix="- " className="text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{t('collections:collections_amount_to_pay')}</p>
            <MoneyText amount={due.net_payable_amount} size="sm" showPaise className="text-purple-600 dark:text-purple-400" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-center mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{t('collections:collections_paid_status')}</p>
            <MoneyText amount={due.total_paid_amount} size="sm" showPaise className="text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">{t('collections:collections_remaining')}</p>
            <MoneyText
              amount={due.remaining_amount}
              size="sm"
              showPaise
              className={isPaid ? 'text-emerald-500' : 'text-red-500 dark:text-red-400'}
            />
          </div>
        </div>
      </div>

      {/* Action row */}
      <div className="px-4 pb-4 flex items-center justify-end gap-2 border-t border-gray-100 dark:border-gray-700 pt-3">
        {due.total_paid_amount > 0 && (
          <button
            onClick={() => onHistory(due)}
            className="touch-target px-4 py-2 text-sm font-semibold text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-colors"
          >
            {t('collections:collections_history')}
          </button>
        )}
        {isPaid ? (
          <span className="flex items-center gap-1 text-sm text-emerald-600 dark:text-emerald-400 font-semibold px-3 py-2">
            <CheckCircle2 size={16} /> {t('collections:collections_fully_paid')}
          </span>
        ) : (
          <button
            onClick={() => onCollect(due)}
            className="touch-target flex items-center gap-1.5 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-semibold transition-colors active:scale-95"
          >
            <IndianRupee size={16} /> {t('collections:collections_collect')}
          </button>
        )}
      </div>
    </div>
  );
};
