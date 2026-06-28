import { useState, useCallback } from 'react';
import html2canvas from 'html2canvas';
import { shareService, type ShareApp } from '../services/shareService';
import toast from 'react-hot-toast';

interface UseReceiptShareOptions {
  captureElementId: string;
  receiptNumber: string;
  memberName: string;
  amount: number;
  chitName?: string;
}

export const useReceiptShare = ({
  captureElementId,
  receiptNumber,
  memberName,
  amount,
  chitName = 'Chit Fund',
}: UseReceiptShareOptions) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [receiptBlob, setReceiptBlob] = useState<Blob | null>(null);

  const safeMemberName = memberName?.trim() ? memberName : 'Member';

  const captureReceipt = useCallback(async (): Promise<Blob | null> => {
    if (receiptBlob) return receiptBlob;
    const el = document.getElementById(captureElementId);
    if (!el) throw new Error('Receipt element not found');

    const canvas = await html2canvas(el, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false,
      useCORS: true,
      width: el.scrollWidth,
      height: el.scrollHeight,
      windowWidth: el.scrollWidth,
      windowHeight: el.scrollHeight,
    });

    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (!blob) return reject(new Error('Canvas to blob failed'));
        setReceiptBlob(blob);
        resolve(blob);
      }, 'image/png');
    });
  }, [captureElementId, receiptBlob]);

  const shareText =
    `Hello ${safeMemberName},\n\nYour chit payment receipt is ready.\n\nReceipt No: ${receiptNumber}\nPaid: ₹${amount.toLocaleString('en-IN')}\nChit: ${chitName}\n\nThank you!`;

  const handleShare = useCallback(async (app: ShareApp): Promise<boolean> => {
    setIsCapturing(true);
    try {
      const blob = await captureReceipt();
      if (!blob) return false;
      const file = new File([blob], `Receipt_${receiptNumber}.png`, { type: 'image/png' });
      const payload = { file, title: `Receipt - ${receiptNumber}`, text: shareText };

      switch (app) {
        case 'whatsapp': await shareService.shareToWhatsApp(payload); break;
        case 'telegram': await shareService.shareToTelegram(payload); break;
        case 'gmail':    await shareService.shareToGmail(payload);    break;
        case 'chrome':   await shareService.shareToChrome(payload);   break;
        case 'more':     await shareService.openSystemShare(payload); break;
      }
      return true;
    } catch (err: any) {
      if (err?.name !== 'AbortError') {
        toast.error('Failed to share receipt. Please try again.');
      }
      return false;
    } finally {
      setIsCapturing(false);
    }
  }, [captureReceipt, receiptNumber, shareText]);

  const resetBlob = useCallback(() => setReceiptBlob(null), []);

  return { handleShare, isCapturing, resetBlob };
};
