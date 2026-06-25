import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payoutApi } from '../../core/payoutApi';
import toast from 'react-hot-toast';
import { ArrowLeft, CheckCircle2, IndianRupee, Printer, Share2, Receipt } from 'lucide-react';

export const WinnerPayoutDetailPage: React.FC = () => {
  const { payoutId } = useParams<{ payoutId: string }>();
  const navigate = useNavigate();
  const [payout, setPayout] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showMarkPaid, setShowMarkPaid] = useState(false);

  // Mark Paid form state
  const [paymentMode, setPaymentMode] = useState('BANK_TRANSFER');
  const [transactionRef, setTransactionRef] = useState('');
  const [paidAt, setPaidAt] = useState(new Date().toISOString().slice(0, 16));
  const [paymentNotes, setPaymentNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadPayout();
  }, [payoutId]);

  const loadPayout = async () => {
    try {
      setLoading(true);
      const res = await payoutApi.getPayout(payoutId!);
      setPayout(res);
    } catch (err: any) {
      toast.error('Failed to load payout details');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkPaid = async () => {
    try {
      setSubmitting(true);
      await payoutApi.markPaid(payoutId!, {
        payment_mode: paymentMode,
        transaction_reference: transactionRef,
        paid_at: new Date(paidAt).toISOString(),
        payment_notes: paymentNotes
      });
      toast.success('Payout marked as paid!');
      setShowMarkPaid(false);
      loadPayout();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to mark as paid');
    } finally {
      setSubmitting(false);
    }
  };

  const handleShare = async () => {
    try {
      const res = await payoutApi.shareReceipt(payoutId!);
      window.open(res.whatsapp_share_url, '_blank');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to generate share link');
    }
  };

  const handleConfirmReceived = async () => {
    try {
      await payoutApi.confirmReceived(payoutId!, { confirmation_note: 'Received successfully' });
      toast.success('Confirmed successfully');
      loadPayout();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to confirm');
    }
  };

  const fmt = (v: any) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(v || 0));

  if (loading) return <div className="p-4 text-center">Loading...</div>;
  if (!payout) return null;

  return (
    <div className="p-4 max-w-3xl mx-auto pb-24">
      <button onClick={() => navigate('/organizer/winner-payouts')} className="flex items-center gap-2 text-gray-500 mb-6 hover:text-gray-900">
        <ArrowLeft size={20} /> Back to Payouts
      </button>

      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Winner Payout Details</h1>
          <p className="text-gray-500 text-sm mt-1">{payout.chit_name} - Month {payout.month_number}</p>
        </div>
        <div className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-bold uppercase">
          {payout.status.replace('_', ' ')}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 className="font-bold border-b pb-2 mb-4">Calculation</h2>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Gross Chit Amount</span>
            <span>{fmt(payout.gross_chit_amount)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Winning Discount</span>
            <span className="text-red-500">-{fmt(payout.winning_bid_discount_amount)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Maintenance</span>
            <span className="text-red-500">-{fmt(payout.maintenance_charge_amount)}</span>
          </div>
          <div className="pt-3 border-t font-bold flex justify-between text-lg">
            <span>Net Payout</span>
            <span className="text-emerald-600">{fmt(payout.payout_amount)}</span>
          </div>
        </div>
      </div>

      {payout.status === 'DRAFT' || payout.status === 'PENDING_PAYMENT' ? (
        <div className="flex gap-3">
          <button 
            onClick={() => setShowMarkPaid(true)}
            className="flex-1 py-3 bg-emerald-600 text-white rounded-xl font-bold flex justify-center items-center gap-2"
          >
            <CheckCircle2 size={18} /> Mark as Paid
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <h2 className="font-bold border-b pb-2 mb-4">Payment Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500">Receipt No</p>
              <p className="font-medium">{payout.payout_receipt_number}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Payment Mode</p>
              <p className="font-medium">{payout.payment_method}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Transaction Ref</p>
              <p className="font-medium">{payout.transaction_reference || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Paid Date</p>
              <p className="font-medium">{new Date(payout.payout_date).toLocaleDateString()}</p>
            </div>
          </div>
          
          <div className="mt-6 flex gap-3">
            <a 
              href={payout.receipt_html_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium flex justify-center items-center gap-2 border border-gray-200"
            >
              <Receipt size={16} /> View Receipt
            </a>
            <button 
              onClick={handleShare}
              className="flex-1 py-2 bg-[#25D366] text-white rounded-lg font-medium flex justify-center items-center gap-2"
            >
              <Share2 size={16} /> Share via WhatsApp
            </button>
          </div>
        </div>
      )}

      {['PAID', 'COMPLETED'].includes(payout.status) && (
        <button 
          onClick={handleConfirmReceived}
          className="mt-6 w-full py-3 bg-purple-600 text-white rounded-xl font-bold"
        >
          Confirm Money Received
        </button>
      )}

      {/* Mark Paid Modal */}
      {showMarkPaid && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4">Mark Payout as Paid</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Payment Mode</label>
                <select value={paymentMode} onChange={(e) => setPaymentMode(e.target.value)} className="w-full p-2 border rounded-lg">
                  <option value="BANK_TRANSFER">Bank Transfer</option>
                  <option value="UPI">UPI</option>
                  <option value="CHEQUE">Cheque</option>
                  <option value="CASH">Cash</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Transaction Ref</label>
                <input type="text" value={transactionRef} onChange={(e) => setTransactionRef(e.target.value)} className="w-full p-2 border rounded-lg" placeholder="UTR/Ref Number" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Paid At</label>
                <input type="datetime-local" value={paidAt} onChange={(e) => setPaidAt(e.target.value)} className="w-full p-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Notes</label>
                <input type="text" value={paymentNotes} onChange={(e) => setPaymentNotes(e.target.value)} className="w-full p-2 border rounded-lg" placeholder="Optional notes" />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowMarkPaid(false)} className="flex-1 py-2 border rounded-lg font-medium">Cancel</button>
              <button onClick={handleMarkPaid} disabled={submitting} className="flex-1 py-2 bg-emerald-600 text-white rounded-lg font-medium disabled:opacity-50">
                {submitting ? 'Saving...' : 'Confirm Paid'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
