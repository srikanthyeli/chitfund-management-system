import React, { useState, useEffect } from 'react';
import { X, Receipt, CornerUpLeft } from 'lucide-react';
import { chitCollectionApi } from '../../../core/chitCollectionApi';
import toast from 'react-hot-toast';

interface PaymentHistoryDialogProps {
  isOpen: boolean;
  onClose: () => void;
  dueId: string | null;
  onReceiptClick: (receipt: any) => void;
}

export const PaymentHistoryDialog: React.FC<PaymentHistoryDialogProps> = ({ isOpen, onClose, dueId, onReceiptClick }) => {
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [reversingReceiptId, setReversingReceiptId] = useState<string | null>(null);
  const [reversalReason, setReversalReason] = useState('');

  useEffect(() => {
    if (isOpen && dueId) fetchHistory();
  }, [isOpen, dueId]);

  const fetchHistory = async () => {
    if (!dueId) return;
    setIsLoading(true);
    try {
      const data = await chitCollectionApi.getPaymentHistory(dueId);
      setHistory(data);
    } catch {
      toast.error('Failed to load payment history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReverse = async (receiptId: string) => {
    if (!reversalReason.trim() || reversalReason.length < 5) {
      toast.error('Please provide a reason (min 5 characters)');
      return;
    }
    try {
      await chitCollectionApi.reversePayment(receiptId, { reversal_reason: reversalReason });
      toast.success('Payment reversed');
      setReversingReceiptId(null);
      setReversalReason('');
      fetchHistory();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to reverse payment');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Payment History</h2>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <X size={18} className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        <div className="overflow-y-auto p-4 space-y-3">
          {isLoading ? (
            Array.from({ length: 2 }).map((_, i) => (
              <div key={i} className="h-24 rounded-xl bg-gray-100 dark:bg-gray-700 animate-pulse" />
            ))
          ) : history.length === 0 ? (
            <p className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">No payments recorded yet.</p>
          ) : (
            history.map(receipt => (
              <div key={receipt.id} className={`rounded-xl border p-3 ${receipt.status === 'REVERSED' ? 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10' : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="text-xs font-mono text-gray-500 dark:text-gray-400">{receipt.receipt_number}</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">₹{receipt.payment_amount}</p>
                  </div>
                  {receipt.status === 'REVERSED' && (
                    <span className="text-xs font-bold bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-2 py-0.5 rounded">REVERSED</span>
                  )}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 space-y-0.5 mb-3">
                  <p>Date: {new Date(receipt.payment_date).toLocaleDateString('en-IN')}</p>
                  <p>Method: {receipt.payment_method}</p>
                  {receipt.status === 'REVERSED' && receipt.reversal_reason && (
                    <p className="text-red-600 dark:text-red-400 mt-1">Reason: {receipt.reversal_reason}</p>
                  )}
                </div>

                <div className="flex gap-2 border-t border-gray-100 dark:border-gray-700 pt-2">
                  <button
                    onClick={() => onReceiptClick(receipt)}
                    className="flex-1 flex justify-center items-center gap-1.5 py-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    <Receipt size={12} /> View Receipt
                  </button>
                  {receipt.status === 'SUCCESS' && (
                    <button
                      onClick={() => setReversingReceiptId(reversingReceiptId === receipt.id ? null : receipt.id)}
                      className="flex-1 flex justify-center items-center gap-1.5 py-1.5 text-xs font-semibold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                    >
                      <CornerUpLeft size={12} /> Reverse
                    </button>
                  )}
                </div>

                {reversingReceiptId === receipt.id && (
                  <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <p className="text-xs font-bold text-red-700 dark:text-red-400 mb-2">Confirm Reversal</p>
                    <input
                      type="text"
                      placeholder="Reason for reversal..."
                      value={reversalReason}
                      onChange={e => setReversalReason(e.target.value)}
                      className="w-full px-3 py-2 text-sm rounded-lg border border-red-200 dark:border-red-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white mb-2 focus:outline-none focus:ring-2 focus:ring-red-400"
                    />
                    <div className="flex gap-2 justify-end">
                      <button
                        onClick={() => setReversingReceiptId(null)}
                        className="px-3 py-1 text-xs font-semibold text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleReverse(receipt.id)}
                        className="px-3 py-1 text-xs font-bold text-white bg-red-600 hover:bg-red-700 rounded-lg"
                      >
                        Confirm Reversal
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
