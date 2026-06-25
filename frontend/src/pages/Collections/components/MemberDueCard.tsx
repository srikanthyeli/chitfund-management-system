import React from 'react';
import { IndianRupee, CheckCircle2 } from 'lucide-react';

interface MemberDueCardProps {
  due: any;
  onCollect: (due: any) => void;
  onHistory: (due: any) => void;
}

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  PAID:          { label: 'Paid',         color: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400' },
  PARTIALLY_PAID:{ label: 'Partial',      color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' },
  OVERDUE:       { label: 'Overdue',      color: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' },
  PENDING:       { label: 'Pending',      color: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400' },
};

const fmt = (v: any) => {
  if (v == null) return '₹0';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(v));
};

export const MemberDueCard: React.FC<MemberDueCardProps> = ({ due, onCollect, onHistory }) => {
  const cfg = STATUS_CONFIG[due.payment_status] || STATUS_CONFIG.PENDING;
  const isPaid = due.payment_status === 'PAID';

  return (
    <div className="rounded-2xl border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 overflow-hidden transition-all">
      {/* Top row */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <p className="font-semibold text-gray-900 dark:text-white">{due.member_name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{due.member_phone || due.member_code}</p>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-semibold flex-shrink-0 ${cfg.color}`}>
            {cfg.label}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Gross</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">{fmt(due.gross_installment_amount)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Bonus</p>
            <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">- {fmt(due.bonus_per_share * due.share_count)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Net Due</p>
            <p className="text-sm font-bold text-purple-600 dark:text-purple-400">{fmt(due.net_payable_amount)}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-center mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Paid</p>
            <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{fmt(due.total_paid_amount)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Remaining</p>
            <p className={`text-sm font-bold ${isPaid ? 'text-emerald-500' : 'text-red-500 dark:text-red-400'}`}>
              {fmt(due.remaining_amount)}
            </p>
          </div>
        </div>
      </div>

      {/* Action row */}
      <div className="px-4 pb-4 flex items-center justify-end gap-2 border-t border-gray-100 dark:border-gray-700 pt-3">
        {due.total_paid_amount > 0 && (
          <button
            onClick={() => onHistory(due)}
            className="px-3 py-1.5 text-xs font-semibold text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-colors"
          >
            History
          </button>
        )}
        {isPaid ? (
          <span className="flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400 font-semibold px-3 py-1.5">
            <CheckCircle2 size={14} /> Fully Paid
          </span>
        ) : (
          <button
            onClick={() => onCollect(due)}
            className="flex items-center gap-1.5 px-4 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-semibold transition-colors active:scale-95"
          >
            <IndianRupee size={14} /> Collect
          </button>
        )}
      </div>
    </div>
  );
};
