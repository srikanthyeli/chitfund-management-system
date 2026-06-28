import React, { useState } from 'react';
import { X, Share2 } from 'lucide-react';
import { WinnerPayoutReceiptTemplate, type WinnerPayoutReceiptData } from './WinnerPayoutReceiptTemplate';
import { ReceiptShareModal } from '../../../components/receipt/ReceiptShareModal';
import { useTranslation } from 'react-i18next';

interface Props {
  receiptData: WinnerPayoutReceiptData;
  onClose: () => void;
}

export const WinnerPayoutReceiptModal: React.FC<Props> = ({ receiptData, onClose }) => {
  const { t } = useTranslation(['common']);

  const [isShareOpen, setIsShareOpen] = useState(false);
  const isReversed = receiptData.status === 'REVERSED';

  return (
    <div className="fixed inset-0 z-[60] bg-black/80 flex flex-col items-center p-4 overflow-y-auto">
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white transition-colors z-[70]"
        aria-label="Close"
      >
        <X size={24} />
      </button>

      <div className="my-auto w-full flex flex-col items-center py-10">
        <WinnerPayoutReceiptTemplate receiptData={receiptData} />

        <div className="w-full max-w-sm mx-auto mt-4 px-4 pb-4 flex flex-col gap-3">
          <button
            onClick={() => setIsShareOpen(true)}
            disabled={isReversed}
            className={`w-full flex items-center justify-center gap-2 px-5 py-4 rounded-2xl font-semibold text-base transition-all ${
              isReversed
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white shadow-md shadow-emerald-200'
            }`}
          >
            <Share2 size={18} />
            Share Receipt
          </button>

          <button
            onClick={onClose}
            className="w-full py-3.5 rounded-2xl font-semibold text-sm text-gray-500 bg-gray-100 hover:bg-gray-200 active:scale-95 transition-all"
          >{t('common:close')}</button>
        </div>
      </div>

      <ReceiptShareModal
        isOpen={isShareOpen}
        onClose={() => setIsShareOpen(false)}
        captureElementId="winner-receipt-capture-area"
        receiptNumber={receiptData.payout_receipt_number}
        memberName={receiptData.winner_name}
        amount={Number(receiptData.payout_amount)}
        chitName={receiptData.chit_name}
      />
    </div>
  );
};
