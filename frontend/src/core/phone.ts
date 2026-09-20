const INDIAN_MOBILE_BODY = /^[6-9]\d{9}$/;

/**
 * Normalize an Indian mobile number to 10 digits.
 * Numbers that are already 10 digits (including those starting with 91, e.g. 9110770030)
 * are accepted as-is. +91 / 91 / 0 prefixes are stripped only when extra digits are present.
 */
export function normalizeIndianMobile(mobile: string): string | null {
  if (!mobile) return null;

  let cleaned = mobile.trim().replace(/[\s\-()]/g, '');
  if (cleaned.startsWith('+')) {
    cleaned = cleaned.slice(1);
  }

  const candidates: string[] = [];
  if (cleaned.startsWith('91') && cleaned.length > 10) {
    candidates.push(cleaned.slice(2));
  }
  if (cleaned.startsWith('0') && cleaned.length === 11) {
    candidates.push(cleaned.slice(1));
  }
  candidates.push(cleaned);

  for (const candidate of candidates) {
    if (INDIAN_MOBILE_BODY.test(candidate)) {
      return candidate;
    }
  }
  return null;
}

export function isValidIndianMobile(mobile: string): boolean {
  return normalizeIndianMobile(mobile) !== null;
}
