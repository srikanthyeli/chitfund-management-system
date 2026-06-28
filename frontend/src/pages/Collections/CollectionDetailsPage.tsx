import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Search, IndianRupee, TrendingUp, CheckCircle2, Clock, X, Share2 } from 'lucide-react';
import { chitCollectionApi } from '../../core/chitCollectionApi';
import { MemberDueCard } from './components/MemberDueCard';
import { CollectPaymentDialog } from './components/CollectPaymentDialog';
import { PaymentHistoryDialog } from './components/PaymentHistoryDialog';
import { PaymentReceiptTemplate } from './components/PaymentReceiptTemplate';
import { ReceiptShareModal } from '../../components/receipt/ReceiptShareModal';
import toast from 'react-hot-toast';

export const CollectionDetailsPage: React.FC = () => {
  const { chitGroupId, auctionId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedDue, setSelectedDue] = useState<any>(null);
  const [isCollectOpen, setIsCollectOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [viewReceiptData, setViewReceiptData] = useState<any>(null);
  const [isShareOpen, setIsShareOpen] = useState(false);

  useEffect(() => {
    if (chitGroupId && auctionId) fetchData();
  }, [chitGroupId, auctionId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await chitCollectionApi.getCollectionSummary(chitGroupId!, auctionId!);
      setData(result);
    } catch {
      toast.error('Failed to load collections data');
    } finally {
      setLoading(false);
    }
  };

  const handleCollectSuccess = (receipt: any, updatedDue: any) => {
    setIsCollectOpen(false);
    setViewReceiptData({
      receipt_number: receipt.receipt_number,
      payment_amount: receipt.payment_amount,
      payment_date: receipt.payment_date,
      status: receipt.status,
      member_name: updatedDue.member_name,
      member_phone: updatedDue.member_phone,
      chit_name: data?.chit_name || 'Chit Fund',
      month_number: data?.month_number,
      share_count: updatedDue.share_count,
      gross_installment_amount: updatedDue.gross_installment_amount,
      bonus_per_share: updatedDue.bonus_per_share,
      total_bonus_amount: (updatedDue.bonus_per_share * updatedDue.share_count),
      net_payable: updatedDue.net_payable_amount,
      remaining_balance: updatedDue.remaining_amount,
      payment_method: receipt.payment_method,
      collected_by: 'Organizer',
      payment_status: updatedDue.payment_status,
    });
    fetchData();
  };

  const handleReceiptClickFromHistory = (receipt: any) => {
    const due = data?.dues.find((d: any) => d.id === selectedDue?.id);
    if (!due) return;
    setViewReceiptData({
      receipt_number: receipt.receipt_number,
      payment_amount: receipt.payment_amount,
      payment_date: receipt.payment_date,
      status: receipt.status,
      member_name: due.member_name,
      member_phone: due.member_phone,
      chit_name: data?.chit_name || 'Chit Fund',
      month_number: data?.month_number,
      share_count: due.share_count,
      gross_installment_amount: due.gross_installment_amount,
      bonus_per_share: due.bonus_per_share,
      total_bonus_amount: (due.bonus_per_share * due.share_count),
      net_payable: due.net_payable_amount,
      remaining_balance: due.remaining_amount,
      payment_method: receipt.payment_method,
      collected_by: 'Organizer',
      payment_status: due.payment_status,
    });
    setIsHistoryOpen(false);
  };

  const fmt = (v: any) => {
    if (v == null) return '₹0';
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(v));
  };

  if (loading) {
    return (
      <div className="p-4 space-y-3 max-w-2xl mx-auto">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-2xl bg-gray-200 dark:bg-gray-700 animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data) return (
    <div className="p-4 text-center mt-10 text-red-500 dark:text-red-400">
      Failed to load collection data.
    </div>
  );

  const filteredDues = (data.dues || []).filter((d: any) =>
    d.member_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.member_phone?.includes(searchQuery)
  );

  const summary = data.summary || {};

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
      {/* Header — matches AuctionsPage style */}
      <div className="sticky top-0 z-10 px-4 py-3 border-b bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-center gap-3 max-w-2xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-600 dark:text-gray-400" />
          </button>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{data.chit_name || 'Chit Fund'}</p>
            <h1 className="font-bold text-lg leading-tight text-gray-900 dark:text-white">
              Month {data.month_number} Collections
            </h1>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-600 dark:text-blue-400 border border-blue-500/30">
            FINALIZED
          </span>
        </div>
      </div>

      <div className="p-4 max-w-2xl mx-auto space-y-4">
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Expected', value: fmt(summary.total_net_payable), icon: <IndianRupee size={14} />, color: 'text-purple-600 dark:text-purple-400', bg: 'bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800' },
            { label: 'Collected', value: fmt(summary.total_collected), icon: <CheckCircle2 size={14} />, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' },
            { label: 'Remaining', value: fmt(summary.total_remaining), icon: <Clock size={14} />, color: 'text-red-500 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' },
          ].map(card => (
            <div key={card.label} className={`rounded-2xl p-3 ${card.bg}`}>
              <div className={`flex items-center gap-1 mb-1 ${card.color}`}>
                {card.icon}
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">{card.label}</span>
              </div>
              <p className={`font-bold text-sm ${card.color}`}>{card.value}</p>
            </div>
          ))}
        </div>

        {/* Status pills */}
        <div className="flex gap-2 text-xs flex-wrap">
          {[
            { label: `${summary.paid_count || 0} Paid`, color: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400' },
            { label: `${summary.partial_count || 0} Partial`, color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' },
            { label: `${summary.pending_count || 0} Pending`, color: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400' },
          ].map(pill => (
            <span key={pill.label} className={`px-2 py-1 rounded-full font-semibold ${pill.color}`}>{pill.label}</span>
          ))}
        </div>

        {/* Search */}
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or phone..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        {/* Member Dues List */}
        {filteredDues.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <TrendingUp size={32} className="text-gray-300 dark:text-gray-600" />
            <p className="text-sm text-gray-500 dark:text-gray-400">No dues found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredDues.map((due: any) => (
              <MemberDueCard
                key={due.id}
                due={due}
                onCollect={() => { setSelectedDue(due); setIsCollectOpen(true); }}
                onHistory={() => { setSelectedDue(due); setIsHistoryOpen(true); }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Dialogs */}
      <CollectPaymentDialog
        isOpen={isCollectOpen}
        onClose={() => setIsCollectOpen(false)}
        due={selectedDue}
        onSuccess={handleCollectSuccess}
      />

      <PaymentHistoryDialog
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        dueId={selectedDue?.id || null}
        onReceiptClick={handleReceiptClickFromHistory}
      />

      {viewReceiptData && (
        <div className="fixed inset-0 z-[60] bg-black/80 flex flex-col items-center p-4 overflow-y-auto">
          <button 
            onClick={() => { setViewReceiptData(null); setIsShareOpen(false); }} 
            className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors z-[70]"
          >
            <X size={24} />
          </button>
          <div className="my-auto w-full flex flex-col items-center py-10 relative">
            <PaymentReceiptTemplate receiptData={viewReceiptData} />
            <div className="w-full max-w-sm mx-auto mt-4 px-4 pb-4">
              <button
                onClick={() => setIsShareOpen(true)}
                className="w-full flex items-center justify-center gap-2 px-5 py-4 rounded-2xl font-semibold text-base bg-purple-600 hover:bg-purple-700 active:scale-95 text-white shadow-md shadow-purple-200 transition-all"
              >
                <Share2 size={18} />
                Share Receipt
              </button>
            </div>
          </div>
        </div>
      )}

      {viewReceiptData && (
        <ReceiptShareModal
          isOpen={isShareOpen}
          onClose={() => setIsShareOpen(false)}
          captureElementId="receipt-capture-area"
          receiptNumber={viewReceiptData.receipt_number}
          memberName={viewReceiptData.member_name}
          amount={viewReceiptData.payment_amount}
          chitName={viewReceiptData.chit_name}
        />
      )}
    </div>
  );
};
