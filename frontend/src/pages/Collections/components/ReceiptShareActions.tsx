import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import { useTranslation } from 'react-i18next';

interface ReceiptShareActionsProps {
  receiptData: any;
  onClose?: () => void;
}

export const ReceiptShareActions: React.FC<ReceiptShareActionsProps> = ({ receiptData, onClose }) => {
  const { t } = useTranslation(['common']);

  const [isGenerating, setIsGenerating] = useState(false);
  const isReversed = receiptData.status === 'REVERSED';

  const generateAndShare = async () => {
    if (isReversed) return;
    setIsGenerating(true);
    try {
      const receiptElement = document.getElementById('receipt-capture-area');
      if (!receiptElement) throw new Error('Receipt element not found');

      const canvas = await html2canvas(receiptElement, {
        scale: 2,
        backgroundColor: '#ffffff',
        logging: false,
        useCORS: true,
        width: receiptElement.scrollWidth,
        height: receiptElement.scrollHeight,
        windowWidth: receiptElement.scrollWidth,
        windowHeight: receiptElement.scrollHeight,
      });

      canvas.toBlob(async (blob) => {
        if (!blob) throw new Error('Canvas to blob failed');
        const file = new File([blob], `Receipt_${receiptData.receipt_number}.png`, { type: 'image/png' });

        if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
          try {
            await navigator.share({ title: 'Chit Payment Receipt', text: `Receipt from ${receiptData.chit_name}`, files: [file] });
            return;
          } catch {
            // fall through to download
          }
        }

        // Desktop fallback: download image then open WhatsApp Web
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        if (waLink) {
          setTimeout(() => window.open(waLink, '_blank'), 400);
        }
      }, 'image/png');
    } catch (error) {
      console.error('Error generating receipt', error);
      alert('Failed to generate receipt image.');
    } finally {
      setIsGenerating(false);
    }
  };

  const waLink = (() => {
    let phone = (receiptData?.member_phone || '').replace(/\D/g, '');
    if (!phone) return null;
    if (phone.startsWith('91') && phone.length === 12) {
      // already has country code
    } else if (phone.length === 10) {
      phone = `91${phone}`;
    } else {
      return null;
    }
    const text =
      `Hello ${receiptData.member_name},\n\n` +
      `Your chit payment receipt is ready.\n\n` +
      `Receipt No: ${receiptData.receipt_number}\n` +
      `Paid: ₹${receiptData.payment_amount}\n` +
      `Date: ${new Date(receiptData.payment_date).toLocaleDateString('en-IN')}\n\n` +
      `Thank you!`;
    return `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
  })();

  return (
    <div className="w-full max-w-sm mx-auto mt-4 px-4 pb-4 flex flex-col gap-3">
      {/* Share Image Button */}
      <button
        onClick={generateAndShare}
        disabled={isGenerating || isReversed}
        className={`w-full flex items-center gap-3 px-5 py-4 rounded-2xl font-semibold text-base transition-all ${
          isReversed
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-purple-600 hover:bg-purple-700 active:scale-95 text-white shadow-md shadow-purple-200'
        }`}
      >
        {isGenerating ? (
          <>
            <svg className="animate-spin h-5 w-5 shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="flex-1 text-center">Generating…</span>
          </>
        ) : (
          <>
            {/* Image / Share icon */}
            <span className="bg-white/20 p-1.5 rounded-lg shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
            </span>
            <span className="flex-1 text-center">Share Receipt Image</span>
          </>
        )}
      </button>

      {/* WhatsApp Text Button */}
      {!isReversed && waLink && (
        <a
          href={waLink}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full flex items-center gap-3 px-5 py-4 rounded-2xl font-semibold text-base bg-[#25D366] hover:bg-[#1ebe5d] active:scale-95 text-white shadow-md shadow-green-200 transition-all"
        >
          {/* WhatsApp Icon */}
          <span className="bg-white/20 p-1.5 rounded-lg shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
            </svg>
          </span>
          <span className="flex-1 text-center">Send via WhatsApp</span>
        </a>
      )}

      {/* Close */}
      {onClose && (
        <button
          onClick={onClose}
          className="w-full py-3.5 rounded-2xl font-semibold text-sm text-gray-500 bg-gray-100 hover:bg-gray-200 active:scale-95 transition-all"
        >{t('common:close')}</button>
      )}
    </div>
  );
};
