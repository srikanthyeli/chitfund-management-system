import React, { useState } from 'react';
import { X, AlertTriangle, Trophy, IndianRupee, TrendingDown, Users } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';

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
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center" style={{ background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(4px)' }}>
      <div
        className="w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl border p-6"
        style={{ background: 'var(--surface-card)', borderColor: 'var(--border-subtle)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: '#f59e0b20', color: '#f59e0b' }}>
              <AlertTriangle size={20} />
            </div>
            <div>
              <h2 className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>Finalize Auction</h2>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Month {auctionMonth} — This cannot be undone</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-xl hover:bg-white/10">
            <X size={18} style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>

        {/* Winner card */}
        <div className="rounded-xl p-4 mb-4 border" style={{ background: '#10b98115', borderColor: '#10b98130' }}>
          <div className="flex items-center gap-2 mb-3">
            <Trophy size={16} className="text-yellow-400" />
            <span className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Winner</span>
          </div>
          <p className="font-bold text-base" style={{ color: 'var(--text-primary)' }}>{winnerName}</p>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>Highest bid: {fmt(winningDiscount)}</p>
        </div>

        {/* Summary table */}
        <div className="space-y-2 mb-5">
          {[
            { label: 'Gross Chit Amount', value: fmt(grossAmount), icon: <IndianRupee size={13} /> },
            { label: 'Maintenance Charge', value: `- ${fmt(maintenanceCharge)}`, icon: <TrendingDown size={13} /> },
            { label: 'Auction Discount', value: `- ${fmt(winningDiscount)}`, icon: <TrendingDown size={13} /> },
          ].map(row => (
            <div key={row.label} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
                {row.icon} {row.label}
              </div>
              <span style={{ color: 'var(--text-primary)' }}>{row.value}</span>
            </div>
          ))}
          <div className="border-t pt-2 flex items-center justify-between font-bold text-sm" style={{ borderColor: 'var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-primary)' }}>Winner Payout</span>
            <span className="text-emerald-400">{fmt(winnerPayout)}</span>
          </div>
          <div className="flex items-center justify-between text-sm pt-1">
            <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
              <Users size={13} /> Bonus / Share ({totalShares} shares)
            </div>
            <span className="font-semibold" style={{ color: 'var(--accent-primary)' }}>{fmt(bonusPerShare)}</span>
          </div>
        </div>

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="flex-1 py-3 rounded-xl border text-sm font-semibold" style={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}>
            Cancel
          </button>
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
