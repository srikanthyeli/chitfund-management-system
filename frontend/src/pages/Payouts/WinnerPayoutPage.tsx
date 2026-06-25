import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { IndianRupee, AlertCircle, CheckCircle2, Calculator, Wallet, ArrowLeft } from 'lucide-react';
import { payoutApi } from '../../core/payoutApi';
import type { PayoutPreviewResponse } from '../../core/payoutApi';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

export const WinnerPayoutPage: React.FC = () => {
  const { chitGroupId, monthNumber } = useParams<{ chitGroupId: string; monthNumber: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [data, setData] = useState<PayoutPreviewResponse | null>(null);

  // Form State
  const [payoutDate, setPayoutDate] = useState(new Date().toISOString().split('T')[0]);
  const [paymentMethod, setPaymentMethod] = useState('BANK_TRANSFER');
  const [transactionRef, setTransactionRef] = useState('');
  const [remarks, setRemarks] = useState('');
  const [allowContribution, setAllowContribution] = useState(false);

  useEffect(() => {
    fetchData();
  }, [chitGroupId, monthNumber]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await payoutApi.getPayoutPreview(chitGroupId!, parseInt(monthNumber!));
      setData(res);
      if (res.payout_eligibility.minimum_organizer_contribution_required > 0) {
        setAllowContribution(true);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to load payout preview');
    } finally {
      setLoading(false);
    }
  };

  const handlePayWinner = async () => {
    if (!data) return;

    if (!data.payout_eligibility.can_pay_from_collection && !allowContribution) {
      toast.error('Insufficient collection. You must allow organizer contribution.');
      return;
    }

    try {
      setSubmitting(true);
      await payoutApi.createPayout(chitGroupId!, parseInt(monthNumber!), {
        payout_date: payoutDate,
        payment_method: paymentMethod,
        transaction_reference: transactionRef,
        remarks: remarks,
        allow_organizer_contribution: allowContribution,
        client_request_id: uuidv4()
      });
      toast.success('Winner payout successful!');
      navigate(`/organizer/chit-groups/${chitGroupId}/financial-summary`);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to process payout');
    } finally {
      setSubmitting(false);
    }
  };

  const fmt = (v: any) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(v || 0));

  if (loading) {
    return <div className="p-4 flex justify-center items-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  if (!data) return null;

  const isShort = !data.payout_eligibility.can_pay_from_collection;
  const shortAmount = data.payout_eligibility.minimum_organizer_contribution_required;

  if (data.payout_eligibility.payout_exists) {
    return (
      <div className="p-4 max-w-4xl mx-auto flex flex-col items-center justify-center py-20 text-center">
        <CheckCircle2 size={64} className="text-emerald-500 mb-4" />
        <h2 className="text-2xl font-bold">Payout Already Completed</h2>
        <p className="text-gray-500 mt-2">The winner for month {monthNumber} has already been paid.</p>
        <button onClick={() => navigate(`/organizer/chit-groups/${chitGroupId}/financial-summary`)} className="mt-6 px-6 py-2 bg-purple-600 text-white rounded-lg font-bold">
          View Financial Summary
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-4xl mx-auto pb-24">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 font-medium">
        <ArrowLeft size={20} /> Back
      </button>

      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Process Winner Payout</h1>
      <p className="text-gray-500 mb-6">Review the financials and pay the auction winner for Month {monthNumber}.</p>

      {isShort && (
        <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl flex items-start gap-3">
          <AlertCircle className="text-amber-600 shrink-0 mt-0.5" />
          <div>
            <h3 className="font-bold text-amber-800 dark:text-amber-400">Collection Shortfall</h3>
            <p className="text-amber-700 dark:text-amber-500 text-sm mt-1">
              Collection is {fmt(shortAmount)} short of the payout amount. You can wait for more payments or contribute the balance as the organizer.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Payout Calculation Card */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h2 className="font-bold flex items-center gap-2 mb-4 border-b pb-2"><Calculator size={18} /> Payout Calculation</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Gross Chit Amount</span>
              <span className="font-medium">{fmt(data.auction.gross_chit_amount)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Winning Bid Discount</span>
              <span className="font-medium text-red-500">-{fmt(data.auction.winning_bid_discount_amount)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Maintenance Charge</span>
              <span className="font-medium text-red-500">-{fmt(data.auction.maintenance_charge_amount)}</span>
            </div>
            <div className="pt-3 mt-3 border-t border-gray-100 flex justify-between font-bold text-lg">
              <span>Final Payout Amount</span>
              <span className="text-purple-600">{fmt(data.auction.payout_amount)}</span>
            </div>
          </div>
        </div>

        {/* Collection Status Card */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h2 className="font-bold flex items-center gap-2 mb-4 border-b pb-2"><Wallet size={18} /> Collection Status</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Expected Collection</span>
              <span className="font-medium">{fmt(data.collection.expected_collection_amount)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Collected Amount</span>
              <span className="font-medium text-emerald-600">{fmt(data.collection.actual_collection_amount)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Pending Dues</span>
              <span className="font-medium text-amber-500">{fmt(data.collection.pending_collection_amount)}</span>
            </div>
            <div className="pt-3 mt-3 border-t border-gray-100 flex justify-between font-bold">
              <span>Organizer Contribution</span>
              <span className={isShort ? "text-amber-600" : "text-gray-400"}>
                {isShort ? fmt(shortAmount) : '₹0'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Details Form */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h2 className="font-bold mb-4">Record Payment Details</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Payout Date</label>
            <input type="date" value={payoutDate} onChange={(e) => setPayoutDate(e.target.value)} className="w-full p-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method</label>
            <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)} className="w-full p-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 outline-none">
              <option value="BANK_TRANSFER">Bank Transfer (NEFT/IMPS/RTGS)</option>
              <option value="UPI">UPI</option>
              <option value="CASH">Cash</option>
              <option value="CHEQUE">Cheque</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Transaction Reference</label>
            <input type="text" placeholder="UTR / UPI Ref Number" value={transactionRef} onChange={(e) => setTransactionRef(e.target.value)} className="w-full p-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 outline-none" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Remarks (Optional)</label>
            <input type="text" placeholder="Any additional notes" value={remarks} onChange={(e) => setRemarks(e.target.value)} className="w-full p-2.5 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 outline-none" />
          </div>
        </div>

        {isShort && (
          <div className="mt-6 pt-4 border-t border-gray-100">
            <label className="flex items-center gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                checked={allowContribution} 
                onChange={(e) => setAllowContribution(e.target.checked)}
                className="w-5 h-5 text-purple-600 rounded border-gray-300 focus:ring-purple-600"
              />
              <span className="font-medium text-gray-900">Use organizer funds ({fmt(shortAmount)}) to cover collection shortage</span>
            </label>
          </div>
        )}

        <button 
          onClick={handlePayWinner} 
          disabled={submitting || (isShort && !allowContribution)}
          className="mt-6 w-full flex items-center justify-center gap-2 py-3.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Processing...' : (
            <>
              <IndianRupee size={18} />
              Pay Winner {fmt(data.auction.payout_amount)}
            </>
          )}
        </button>
      </div>

    </div>
  );
};
