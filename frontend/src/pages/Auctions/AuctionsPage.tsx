import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Plus, Gavel, Calendar, TrendingUp, CheckCircle2,
  XCircle, Clock, ChevronRight, AlertCircle, ArrowLeft,
  IndianRupee
} from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';
import CreateAuctionDialog from './CreateAuctionDialog';
import { useTranslation } from 'react-i18next';

interface Auction {
  id: string;
  auction_month_number: number;
  auction_date: string;
  status: string;
  gross_chit_amount: string;
  maintenance_charge: string;
  maximum_bid_discount: string;
  bid_count: number;
  highest_bid: string | null;
  winner_payout_amount: string | null;
  finalized_at: string | null;
  created_at: string;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  OPEN: { label: 'Open', color: 'bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/20 dark:text-emerald-400 dark:border-emerald-500/30', icon: <Clock size={12} /> },
  FINALIZED: { label: 'Finalized', color: 'bg-blue-100 text-blue-700 border border-blue-200 dark:bg-blue-500/20 dark:text-blue-400 dark:border-blue-500/30', icon: <CheckCircle2 size={12} /> },
  CANCELLED: { label: 'Cancelled', color: 'bg-red-100 text-red-700 border border-red-200 dark:bg-red-500/20 dark:text-red-400 dark:border-red-500/30', icon: <XCircle size={12} /> },
  DRAFT: { label: 'Draft', color: 'bg-gray-100 text-gray-600 border border-gray-200 dark:bg-gray-500/20 dark:text-gray-400 dark:border-gray-500/30', icon: <AlertCircle size={12} /> },
};

const fmt = (v: string | number | null | undefined) => {
  if (v == null) return '—';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(v));
};

export const AuctionsPage: React.FC = () => {
  const { t } = useTranslation(['auctions', 'reports']);

  const { id: chitGroupId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [chitName, setChitName] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(async () => {
    if (!chitGroupId) return;
    setLoading(true);
    try {
      const [aRes, cRes] = await Promise.all([
        api.get(`/chit-groups/${chitGroupId}/auctions`),
        api.get(`/chit-groups/${chitGroupId}`),
      ]);
      setAuctions(aRes.data.items || []);
      setChitName(cRes.data.chit_name || '');
    } catch {
      toast.error('Failed to load auctions');
    } finally {
      setLoading(false);
    }
  }, [chitGroupId]);

  useEffect(() => { load(); }, [load]);

  const handleCreated = () => { setShowCreate(false); load(); };

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <div className="sticky top-0 z-10 px-4 py-3 border-b" style={{ background: 'var(--surface-card)', borderColor: 'var(--border-subtle)' }}>
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/organizer/chit-groups/${chitGroupId}`)} className="p-1.5 rounded-lg hover:bg-white/10 transition-colors">
            <ArrowLeft size={20} style={{ color: 'var(--text-secondary)' }} />
          </button>
          <div className="flex-1 min-w-0">
            <p className="text-xs truncate" style={{ color: 'var(--text-secondary)' }}>{chitName}</p>
            <h1 className="font-bold text-lg leading-tight" style={{ color: 'var(--text-primary)' }}>Monthly Auctions</h1>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all active:scale-95 bg-purple-600 hover:bg-purple-700 text-white"
          >
            <Plus size={16} />
            <span>New Auction</span>
          </button>
        </div>
      </div>

      <div className="p-4 max-w-2xl mx-auto space-y-3">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-28 rounded-2xl animate-pulse" style={{ background: 'var(--surface-card)' }} />
          ))
        ) : auctions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-4">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'var(--surface-card)' }}>
              <Gavel size={28} style={{ color: 'var(--text-secondary)' }} />
            </div>
            <p className="text-sm text-center" style={{ color: 'var(--text-secondary)' }}>No auctions yet. Create the first monthly auction.</p>
            <button
              onClick={() => setShowCreate(true)}
              className="px-4 py-2 rounded-xl text-sm font-semibold"
              style={{ background: 'var(--accent-primary)', color: '#fff' }}
            >
              Create First Auction
            </button>
          </div>
        ) : (
          auctions.map(auction => {
            const cfg = STATUS_CONFIG[auction.status] || STATUS_CONFIG.DRAFT;
            return (
              <Link key={auction.id} to={`/organizer/chit-groups/${chitGroupId}/auctions/${auction.id}`}>
                <div
                  className="rounded-2xl p-4 border transition-all hover:scale-[1.01] active:scale-[0.99] cursor-pointer"
                  style={{ background: 'var(--surface-card)', borderColor: 'var(--border-subtle)' }}
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm" style={{ background: 'var(--accent-primary)20', color: 'var(--accent-primary)' }}>
                        M{auction.auction_month_number}
                      </div>
                      <div>
                        <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>Month {auction.auction_month_number}</p>
                        <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
                          <Calendar size={11} />
                          {new Date(auction.auction_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                        </div>
                      </div>
                    </div>
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${cfg.color}`}>
                      {cfg.icon}
                      {cfg.label}
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="text-center">
                      <p className="text-xs mb-0.5" style={{ color: 'var(--text-secondary)' }}>Gross</p>
                      <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{fmt(auction.gross_chit_amount)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs mb-0.5" style={{ color: 'var(--text-secondary)' }}>{t('auctions:auctions_bids')}</p>
                      <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{auction.bid_count}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs mb-0.5" style={{ color: 'var(--text-secondary)' }}>{t('reports:reports_highest')}</p>
                      <p className="text-sm font-semibold" style={{ color: auction.highest_bid ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>
                        {auction.highest_bid ? fmt(auction.highest_bid) : '—'}
                      </p>
                    </div>
                  </div>
                  {auction.status === 'FINALIZED' && auction.winner_payout_amount && (
                    <div className="mt-3 pt-3 border-t flex items-center gap-2" style={{ borderColor: 'var(--border-subtle)' }}>
                      <CheckCircle2 size={14} className="text-emerald-400" />
                      <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Winner payout: <span className="font-semibold text-emerald-400">{fmt(auction.winner_payout_amount)}</span>
                      </span>
                    </div>
                  )}
                </div>
              </Link>
            );
          })
        )}
      </div>

      {showCreate && chitGroupId && (
        <CreateAuctionDialog
          chitGroupId={chitGroupId}
          onClose={() => setShowCreate(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
};
