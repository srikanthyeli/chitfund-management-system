import React, { useState } from 'react';
import { X, AlertTriangle, Trophy, IndianRupee, TrendingDown, Users } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';

interface Props {
  auctionId: string;
  auctionMonth: number;
  winnerName: string;
  winningDiscount: number;
  grossAmount: number;
  maintenanceCharge: number;
  winnerPayout: number;
  bonusPerShare: number;
  totalShares: number;
  onClose: () => void;
  onFinalized: () => void;
}

const fmt = (v: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const FinalizeAuctionDialog: React.FC<Props> = ({
  auctionId, auctionMonth, winnerName, winningDiscount,
  grossAmount, maintenanceCharge, winnerPayout, bonusPerShare,
  totalShares, onClose, onFinalized,
}) => {
  const [loading, setLoading] = useState(false);

  const handleFinalize = async () => {
    setLoading(true);
    try {
      await api.post(`/chit-auctions/${auctionId}/finalize`);
      toast.success('Auction finalized successfully!');
      onFinalized();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to finalize auction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl border p-6 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400">
              <AlertTriangle size={20} />
            </div>
            <div>
              <h2 className="font-bold text-lg text-gray-900 dark:text-white">Finalize Auction</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">Month {auctionMonth} — This cannot be undone</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <X size={18} className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Winner card */}
        <div className="rounded-xl p-4 mb-4 border bg-emerald-50 dark:bg-emerald-900/20 border-emerald-100 dark:border-emerald-800/30">
          <div className="flex items-center gap-2 mb-3">
            <Trophy size={16} className="text-yellow-500" />
            <span className="font-semibold text-sm text-gray-900 dark:text-white">{t('common:receipt_winner')}</span>
          </div>
          <p className="font-bold text-base text-gray-900 dark:text-white">{winnerName}</p>
          <p className="text-xs mt-0.5 text-gray-600 dark:text-gray-400">Highest bid: {fmt(winningDiscount)}</p>
        </div>

        {/* Summary table */}
        <div className="space-y-2 mb-5">
          {[
            { label: 'Gross Chit Amount', value: fmt(grossAmount), icon: <IndianRupee size={13} /> },
            { label: 'Maintenance Charge', value: `- ${fmt(maintenanceCharge)}`, icon: <TrendingDown size={13} /> },
            { label: 'Auction Discount', value: `- ${fmt(winningDiscount)}`, icon: <TrendingDown size={13} /> },
          ].map(row => (
            <div key={row.label} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                {row.icon} {row.label}
              </div>
              <span className="text-gray-900 dark:text-white font-medium">{row.value}</span>
            </div>
          ))}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-2 flex items-center justify-between font-bold text-sm">
            <span className="text-gray-900 dark:text-white">Winner Payout</span>
            <span className="text-emerald-600 dark:text-emerald-400">{fmt(winnerPayout)}</span>
          </div>
          <div className="flex items-center justify-between text-sm pt-1">
            <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
              <Users size={13} /> Bonus / Share ({totalShares} shares)
            </div>
            <span className="font-semibold text-purple-600 dark:text-purple-400">{fmt(bonusPerShare)}</span>
          </div>
        </div>

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="flex-1 py-3 rounded-xl border border-gray-200 dark:border-gray-700 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">{t('common:cancel')}</button>
          <button
            onClick={handleFinalize}
            disabled={loading}
            className="flex-1 py-3 rounded-xl text-sm font-bold transition-all active:scale-95 disabled:opacity-50"
            style={{ background: '#10b981', color: '#fff' }}
          >
            {loading ? 'Finalizing...' : 'Confirm & Finalize'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FinalizeAuctionDialog;
