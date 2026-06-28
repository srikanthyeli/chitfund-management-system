export type ShareApp = 'whatsapp' | 'telegram' | 'gmail' | 'chrome' | 'more';

export interface SharePayload {
  file: File;
  title: string;
  text: string;
}

const downloadFile = (file: File) => {
  const url = URL.createObjectURL(file);
  const a = document.createElement('a');
  a.href = url;
  a.download = file.name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

const nativeShare = async (payload: SharePayload): Promise<boolean> => {
  if (!navigator.share) return false;
  const shareData: ShareData = {
    title: payload.title,
    text: payload.text,
  };

  const canShareFiles = navigator.canShare?.({ files: [payload.file] });
  if (canShareFiles || navigator.canShare === undefined) {
    shareData.files = [payload.file];
  }

  try {
    await navigator.share(shareData);
    return true;
  } catch {
    return false;
  }
};

const openFallbackUrl = (url: string) => {
  window.open(url, '_blank');
};

export const shareService = {
  async shareToWhatsApp(payload: SharePayload): Promise<void> {
    if (await nativeShare(payload)) return;

    downloadFile(payload.file);
    const link = `https://wa.me/?text=${encodeURIComponent(
      `${payload.text}\n\n(Receipt image downloaded. Attach it manually from your downloads if WhatsApp did not open the image directly.)`
    )}`;
    setTimeout(() => openFallbackUrl(link), 400);
  },

  async shareToTelegram(payload: SharePayload): Promise<void> {
    if (await nativeShare(payload)) return;

    downloadFile(payload.file);
    const link = `https://t.me/share/url?url=${encodeURIComponent(payload.text)}`;
    setTimeout(() => openFallbackUrl(link), 400);
  },

  async shareToGmail(payload: SharePayload): Promise<void> {
    downloadFile(payload.file);
    const link = `https://mail.google.com/mail/?view=cm&fs=1&su=${encodeURIComponent(payload.title)}&body=${encodeURIComponent(payload.text)}`;
    setTimeout(() => openFallbackUrl(link), 400);
  },

  async shareToChrome(payload: SharePayload): Promise<void> {
    downloadFile(payload.file);
  },

  async openSystemShare(payload: SharePayload): Promise<void> {
    if (await nativeShare(payload)) return;
    downloadFile(payload.file);
  },
};
