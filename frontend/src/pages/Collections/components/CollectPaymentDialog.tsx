import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { chitCollectionApi } from '../../../core/chitCollectionApi';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';
import { MoneyText, formatINR } from '../../../components/common/MoneyText';
import { StatusChip } from '../../../components/common/StatusChip';

interface CollectPaymentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  due: any;
  onSuccess: (receipt: any, updatedDue: any) => void;
}

export const CollectPaymentDialog: React.FC<CollectPaymentDialogProps> = ({ isOpen, onClose, due, onSuccess }) => {
  const { t } = useTranslation(['collections', 'common']);

  const [amount, setAmount] = useState<string>('');
  const [method, setMethod] = useState<string>('CASH');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [reference, setReference] = useState<string>('');
  const [remarks, setRemarks] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen && due) {
      setAmount(String(due.remaining_amount || ''));
      setMethod('CASH');
      setReference('');
      setRemarks('');
      setDate(new Date().toISOString().split('T')[0]);
    }
  }, [isOpen, due]);

  if (!isOpen || !due) return null;

  const currentRemaining = parseFloat(due.remaining_amount) || 0;
  const inputAmount = parseFloat(amount) || 0;
  const remainingAfter = Math.max(0, currentRemaining - inputAmount);
  const newStatus = remainingAfter === 0 ? 'PAID' : inputAmount > 0 ? 'PARTIALLY_PAID' : 'PENDING';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputAmount <= 0) { toast.error(t('collections:collections_amount_gt_zero')); return; }
    if (inputAmount > currentRemaining) { toast.error(t('collections:collections_cannot_exceed')); return; }

    setIsSubmitting(true);
    try {
      const response = await chitCollectionApi.collectPayment(due.id, {
        payment_amount: inputAmount,
        payment_date: date,
        payment_method: method,
        transaction_reference: reference || null,
        remarks: remarks || null,
        client_request_id: `req-${due.id}-${Date.now()}`,
      });
      toast.success(t('collections:collections_payment_success'));
      onSuccess(response.receipt, response.due);
    } catch (error: any) {
      toast.error(error.response?.data?.message || t('collections:collections_payment_failed'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">{t('collections:collections_collect_payment')}</h2>
          <button
            onClick={onClose}
            className="touch-target p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-center"
            aria-label={t('common:close')}
          >
            <X size={18} className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        <div className="overflow-y-auto p-4 space-y-4">
          {/* Member Info */}
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-3 border border-purple-100 dark:border-purple-800">
            <p className="font-semibold text-purple-900 dark:text-purple-300 text-base">{due.member_name}</p>
            <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
              <div>
                <p className="text-gray-500 dark:text-gray-400">{t('collections:collections_amount_due')}</p>
                <MoneyText amount={due.net_payable_amount} size="sm" showPaise className="text-gray-800 dark:text-gray-200" />
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">{t('collections:collections_paid_status')}</p>
                <MoneyText amount={due.total_paid_amount} size="sm" showPaise className="text-gray-800 dark:text-gray-200" />
              </div>
              <div>
                <p className="text-gray-500 dark:text-gray-400">{t('collections:collections_remaining')}</p>
                <MoneyText amount={due.remaining_amount} size="sm" showPaise className="text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>

          <form id="payment-form" onSubmit={handleSubmit} className="space-y-3">
            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('collections:collections_payment_amount')}
              </label>
              <input
                type="number" step="0.01" min="1" max={currentRemaining} required
                value={amount}
                onChange={e => setAmount(e.target.value)}
                className="touch-target w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-2xl font-bold focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Method */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('collections:collections_method')}
                </label>
                <select
                  value={method} onChange={e => setMethod(e.target.value)}
                  className="touch-target w-full px-3 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="CASH">{t('collections:collections_method_cash')}</option>
                  <option value="UPI">{t('collections:collections_method_upi')}</option>
                  <option value="BANK_TRANSFER">{t('collections:collections_method_bank')}</option>
                  <option value="CARD">{t('collections:collections_method_card')}</option>
                </select>
              </div>
              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('collections:collections_date_label')}
                </label>
                <input
                  type="date" value={date} required onChange={e => setDate(e.target.value)}
                  className="touch-target w-full px-3 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            {method !== 'CASH' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('collections:collections_txn_ref')}
                </label>
                <input
                  type="text" value={reference} onChange={e => setReference(e.target.value)}
                  placeholder={t('collections:collections_txn_placeholder')}
                  className="touch-target w-full px-3 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('collections:collections_remarks')}
              </label>
              <textarea
                value={remarks} onChange={e => setRemarks(e.target.value)} rows={2}
                className="w-full px-3 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              />
            </div>
          </form>

          {/* Live Preview */}
          {inputAmount > 0 && inputAmount <= currentRemaining && (
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-3 border border-gray-200 dark:border-gray-600 text-sm space-y-1.5">
              <div className="flex justify-between text-gray-600 dark:text-gray-400 items-center">
                <span>{t('collections:collections_remaining_after')}</span>
                <MoneyText amount={remainingAfter} size="sm" showPaise className="text-gray-900 dark:text-white" />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">{t('collections:collections_new_status')}</span>
                <StatusChip status={newStatus} />
              </div>
            </div>
          )}
        </div>

        {/* Footer CTA */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="submit" form="payment-form"
            disabled={isSubmitting || inputAmount <= 0 || inputAmount > currentRemaining}
            className="touch-target w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3.5 rounded-xl transition-colors active:scale-95 text-base"
          >
            {isSubmitting
              ? t('collections:collections_processing')
              : t('collections:collections_collect_btn', { amount: formatINR(inputAmount > 0 ? inputAmount : 0, true) })}
          </button>
        </div>
      </div>
    </div>
  );
};
