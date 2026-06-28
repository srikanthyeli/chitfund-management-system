import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Plus, Gavel, Trophy, TrendingUp, IndianRupee,
  Calendar, Users, CheckCircle2, Clock, Crown, Percent
} from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';
import BidEntryDialog from './BidEntryDialog';
import FinalizeAuctionDialog from './FinalizeAuctionDialog';
import { payoutApi } from '../../core/payoutApi';
import { useTranslation } from 'react-i18next';

interface Bid {
  id: string;
  membership_id: string;
  member_id: string;
  member_name: string;
  member_code: string;
  share_count: number;
  bid_discount_amount: string;
  bid_time: string;
  status: string;
  is_highest: boolean;
}

interface EligibleMember {
  membership_id: string;
  member_id: string;
  member_code: string;
  full_name: string;
  share_count: number;
  has_won_auction: boolean;
}

interface Due {
  id: string;
  member_name: string;
  member_code: string;
  share_count: number;
  gross_installment_amount: string;
  total_bonus_amount: string;
  net_payable_amount: string;
  payment_status: string;
}

interface AuctionDetail {
  id: string;
  chit_name: string;
  chit_code: string;
  chit_group_id: string;
  monthly_installment_per_share: string;
  total_shares: number;
  auction_month_number: number;
  auction_date: string;
  status: string;
  gross_chit_amount: string;
  maintenance_charge: string;
  maximum_bid_discount: string;
  bids: Bid[];
  eligible_members: EligibleMember[];
  winner: {
    membership_id: string;
    member_id: string;
    member_name: string;
    member_code: string;
    winning_discount: string;
    winner_payout_amount: string;
    bonus_per_share: string;
  } | null;
  bonus_per_share: string | null;
  finalized_at: string | null;
}

const fmt = (v: string | number | null | undefined) => {
  if (v == null) return '—';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(v));
};

export const AuctionDetailPage: React.FC = () => {
  const { t } = useTranslation(['collections', 'reports']);

  const { id: chitGroupId, auctionId } = useParams<{ id: string; auctionId: string }>();
  const navigate = useNavigate();
  const [auction, setAuction] = useState<AuctionDetail | null>(null);
  const [dues, setDues] = useState<Due[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBid, setShowBid] = useState(false);
  const [showFinalize, setShowFinalize] = useState(false);
  const [creatingPayout, setCreatingPayout] = useState(false);

  const load = useCallback(async () => {
    if (!auctionId) return;
    setLoading(true);
    try {
      const res = await api.get(`/chit-auctions/${auctionId}`);
      setAuction(res.data);
      if (res.data.status === 'FINALIZED') {
        const dRes = await api.get(`/chit-auctions/${auctionId}/dues`);
        setDues(dRes.data);
      }
    } catch {
      toast.error('Failed to load auction');
    } finally {
      setLoading(false);
    }
  }, [auctionId]);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return (
      <div className="p-4 space-y-3 max-w-2xl mx-auto">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-2xl animate-pulse" style={{ background: 'var(--surface-card)' }} />
        ))}
      </div>
    );
  }

  if (!auction) return null;

  const activeBids = auction.bids.filter(b => b.status === 'ACTIVE');
  const highestBid = activeBids.length > 0 ? Math.max(...activeBids.map(b => Number(b.bid_discount_amount))) : null;
  const estimatedPayout = highestBid != null
    ? Number(auction.gross_chit_amount) - Number(auction.maintenance_charge) - highestBid
    : null;

  const isOpen = auction.status === 'OPEN';
  const isFinalized = auction.status === 'FINALIZED';

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="sticky top-0 z-10 px-4 py-3 border-b bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/organizer/chit-groups/${chitGroupId}/auctions`)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <ArrowLeft size={20} className="text-gray-500 dark:text-gray-400" />
          </button>
          <div className="flex-1 min-w-0">
            <p className="text-xs truncate text-gray-500 dark:text-gray-400">{auction.chit_name}</p>
            <h1 className="font-bold text-lg leading-tight text-gray-900 dark:text-white">
              Month {auction.auction_month_number} Auction
            </h1>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${isOpen ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' : isFinalized ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400 border border-blue-500/30' : 'bg-gray-500/20 text-gray-500 dark:text-gray-400'}`}>
            {auction.status}
          </span>
        </div>
      </div>

      <div className="p-4 max-w-2xl mx-auto space-y-4">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: 'Gross Amount', value: fmt(auction.gross_chit_amount), icon: <IndianRupee size={16} />, color: 'text-purple-600 dark:text-purple-400' },
            { label: 'Maintenance', value: fmt(auction.maintenance_charge), icon: <TrendingUp size={16} />, color: 'text-amber-600 dark:text-amber-400' },
            { label: 'Highest Bid', value: highestBid != null ? fmt(highestBid) : '—', icon: <Gavel size={16} />, color: 'text-emerald-600 dark:text-emerald-400' },
            { label: 'Est. Payout', value: estimatedPayout != null ? fmt(estimatedPayout) : '—', icon: <Crown size={16} />, color: 'text-pink-500 dark:text-pink-400' },
          ].map(card => (
            <div key={card.label} className="rounded-2xl p-4 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
              <div className={`flex items-center gap-2 mb-2 ${card.color}`}>
                {card.icon}
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">{card.label}</span>
              </div>
              <p className={`font-bold text-sm ${card.color}`}>{card.value}</p>
            </div>
          ))}
        </div>

        {/* Auction date */}
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Calendar size={14} />
          <span>Auction Date: {new Date(auction.auction_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}</span>
        </div>

        {/* Winner card (if finalized) */}
        {isFinalized && auction.winner && (
          <div className="rounded-2xl p-5 border border-yellow-400/30 bg-yellow-400/5 dark:bg-yellow-400/10">
            <div className="flex items-center gap-2 mb-3">
              <Trophy size={18} className="text-yellow-500" />
              <span className="font-bold text-gray-900 dark:text-white">Auction Winner</span>
            </div>
            <p className="font-bold text-xl mb-1 text-gray-900 dark:text-white">{auction.winner.member_name}</p>
            <p className="text-xs mb-3 text-gray-500 dark:text-gray-400">{auction.winner.member_code}</p>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <p className="text-xs mb-0.5 text-gray-500 dark:text-gray-400">Discount</p>
                <p className="font-semibold text-sm text-red-500 dark:text-red-400">{fmt(auction.winner.winning_discount)}</p>
              </div>
              <div>
                <p className="text-xs mb-0.5 text-gray-500 dark:text-gray-400">Payout</p>
                <p className="font-semibold text-sm text-emerald-600 dark:text-emerald-400">{fmt(auction.winner.winner_payout_amount)}</p>
              </div>
              <div>
                <p className="text-xs mb-0.5 text-gray-500 dark:text-gray-400">Bonus/Share</p>
                <p className="font-semibold text-sm text-purple-600 dark:text-purple-400">{fmt(auction.winner.bonus_per_share)}</p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons — OPEN state */}
        {isOpen && (
          <div className="flex gap-3">
            <button
              onClick={() => setShowBid(true)}
              className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all active:scale-95 bg-purple-600 hover:bg-purple-700 text-white"
            >
              <Plus size={16} /> Add Bid
            </button>
            {activeBids.length > 0 && (
              <button
                onClick={() => setShowFinalize(true)}
                className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all active:scale-95 bg-emerald-600 hover:bg-emerald-700 text-white"
              >
                <CheckCircle2 size={16} /> Finalize
              </button>
            )}
          </div>
        )}

        {isFinalized && (
          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/organizer/chit-groups/${chitGroupId}/auctions/${auctionId}/collections`)}
              className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all active:scale-95 bg-purple-600 hover:bg-purple-700 text-white shadow-sm"
            >
              <IndianRupee size={16} />{t('collections:collections_title')}</button>
            <button
              disabled={creatingPayout}
              onClick={async () => {
                try {
                  setCreatingPayout(true);
                  const res = await payoutApi.createDraft({ auction_id: auctionId });
                  navigate(`/organizer/winner-payouts/${res.id}`);
                } catch (err: any) {
                  if (err.response?.data?.detail?.includes('already exists')) {
                    toast.error('Payout already exists. Redirecting...');
                    navigate(`/organizer/winner-payouts`);
                  } else {
                    toast.error('Failed to create payout draft');
                  }
                } finally {
                  setCreatingPayout(false);
                }
              }}
              className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all active:scale-95 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm disabled:opacity-50"
            >
              <Trophy size={16} /> {creatingPayout ? 'Creating...' : 'Winner Payout'}
            </button>
          </div>
        )}

        {/* Bids List */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold" style={{ color: 'var(--text-primary)' }}>Bids ({activeBids.length})</h2>
            <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
              <Users size={12} /> {auction.total_shares} shares total
            </div>
          </div>

          {activeBids.length === 0 ? (
            <div className="rounded-2xl p-8 text-center border" style={{ background: 'var(--surface-card)', borderColor: 'var(--border-subtle)' }}>
              <Gavel size={24} className="mx-auto mb-2" style={{ color: 'var(--text-secondary)' }} />
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>No bids yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {activeBids.map((bid, idx) => (
                <div
                  key={bid.id}
                  className="rounded-2xl p-4 border flex items-center gap-4"
                  style={{
                    background: bid.is_highest ? '#10b98115' : 'var(--surface-card)',
                    borderColor: bid.is_highest ? '#10b98140' : 'var(--border-subtle)',
                  }}
                >
                  <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style={{ background: 'var(--accent-primary)30', color: 'var(--accent-primary)' }}>
                    {idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-sm truncate text-gray-900 dark:text-white">{bid.member_name}</p>
                      {bid.is_highest && <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-medium flex-shrink-0">{t('reports:reports_highest')}</span>}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {bid.member_code} · {bid.share_count} share{bid.share_count > 1 ? 's' : ''} · {new Date(bid.bid_time).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <p className={`font-bold text-sm flex-shrink-0 ${bid.is_highest ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-900 dark:text-white'}`}>
                    {fmt(bid.bid_discount_amount)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Monthly Dues (after finalization) */}
        {isFinalized && dues.length > 0 && (
          <div>
            <h2 className="font-bold mb-3 text-gray-900 dark:text-white">Monthly Dues ({dues.length} members)</h2>
            {/* Desktop table */}
            <div className="hidden sm:block rounded-2xl border overflow-hidden border-gray-200 dark:border-gray-700">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-700">
                    {['Member', 'Shares', 'Gross', 'Bonus', 'Net Payable'].map(h => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dues.map((due, i) => (
                    <tr key={due.id} className={`border-t border-gray-100 dark:border-gray-700 ${i % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700/50'}`}>
                      <td className="px-4 py-3">
                        <p className="font-medium text-gray-900 dark:text-white">{due.member_name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{due.member_code}</p>
                      </td>
                      <td className="px-4 py-3 text-gray-900 dark:text-white">{due.share_count}</td>
                      <td className="px-4 py-3 text-gray-900 dark:text-white">{fmt(due.gross_installment_amount)}</td>
                      <td className="px-4 py-3 text-red-500 dark:text-red-400">- {fmt(due.total_bonus_amount)}</td>
                      <td className="px-4 py-3 font-bold text-emerald-600 dark:text-emerald-400">{fmt(due.net_payable_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Mobile cards */}
            <div className="sm:hidden space-y-2">
              {dues.map(due => (
                <div key={due.id} className="rounded-xl p-4 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-sm text-gray-900 dark:text-white">{due.member_name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{due.member_code} · {due.share_count} shares</p>
                    </div>
                    <span className="font-bold text-sm text-emerald-600 dark:text-emerald-400">{fmt(due.net_payable_amount)}</span>
                  </div>
                  <div className="flex gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <span>Gross: {fmt(due.gross_installment_amount)}</span>
                    <span>Bonus: -{fmt(due.total_bonus_amount)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Dialogs */}
      {showBid && auction && (
        <BidEntryDialog
          auctionId={auction.id}
          maxBid={Number(auction.maximum_bid_discount)}
          auctionMonth={auction.auction_month_number}
          eligibleMembers={auction.eligible_members}
          onClose={() => setShowBid(false)}
          onBidPlaced={() => { setShowBid(false); load(); }}
        />
      )}

      {showFinalize && auction && highestBid != null && estimatedPayout != null && (
        <FinalizeAuctionDialog
          auctionId={auction.id}
          auctionMonth={auction.auction_month_number}
          winnerName={activeBids.find(b => b.is_highest)?.member_name || ''}
          winningDiscount={highestBid}
          grossAmount={Number(auction.gross_chit_amount)}
          maintenanceCharge={Number(auction.maintenance_charge)}
          winnerPayout={estimatedPayout}
          bonusPerShare={Math.round((highestBid / auction.total_shares) * 100) / 100}
          totalShares={auction.total_shares}
          onClose={() => setShowFinalize(false)}
          onFinalized={() => { setShowFinalize(false); load(); }}
        />
      )}
    </div>
  );
};
