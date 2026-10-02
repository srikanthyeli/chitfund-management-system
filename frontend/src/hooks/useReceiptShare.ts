import { useState, useCallback } from 'react';
import html2canvas from 'html2canvas';
import { useTranslation } from 'react-i18next';
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
  chitName,
}: UseReceiptShareOptions) => {
  const { t } = useTranslation('common');
  const [isCapturing, setIsCapturing] = useState(false);
  const [receiptBlob, setReceiptBlob] = useState<Blob | null>(null);

  const safeMemberName = memberName?.trim() ? memberName : t('receipt_member');
  const safeChitName = chitName?.trim() ? chitName : t('receipt_chit_fund');
  const amountFormatted = Number(amount || 0).toLocaleString('en-IN');

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

  const shareText = t('receipt_share_text', {
    name: safeMemberName,
    receiptNumber,
    amount: amountFormatted,
    chitName: safeChitName,
  });

  const shareTitle = t('receipt_share_title', { receiptNumber });

  const handleShare = useCallback(async (app: ShareApp): Promise<boolean> => {
    setIsCapturing(true);
    try {
      const blob = await captureReceipt();
      if (!blob) return false;
      const file = new File([blob], `Receipt_${receiptNumber}.png`, { type: 'image/png' });
      const payload = {
        file,
        title: shareTitle,
        text: shareText,
        fallbackHint: t('receipt_share_fallback_hint'),
      };

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
        toast.error(t('receipt_share_failed'));
      }
      return false;
    } finally {
      setIsCapturing(false);
    }
  }, [captureReceipt, receiptNumber, shareText, shareTitle, t]);

  const resetBlob = useCallback(() => setReceiptBlob(null), []);

  return { handleShare, isCapturing, resetBlob };
};
