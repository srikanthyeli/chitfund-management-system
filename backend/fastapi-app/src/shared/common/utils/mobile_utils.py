import re
from typing import Optional

# 10-digit Indian mobile numbers start with 6, 7, 8, or 9.
INDIAN_MOBILE_BODY = re.compile(r'^[6-9]\d{9}$')
NON_DIGIT_SEPARATORS = re.compile(r'[\s\-()]')


def normalize_indian_mobile(mobile: Optional[str]) -> Optional[str]:
    """Return a 10-digit Indian mobile number, or None if invalid.

    A 10-digit number starting with 6-9 is accepted as-is, including numbers
    that begin with 91 (e.g. 9110770030). Country-code prefixes (+91, 91, 0)
    are stripped only when extra digits are present.
    """
    if not mobile:
        return None

    cleaned = NON_DIGIT_SEPARATORS.sub('', mobile.strip())
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]

    candidates = []
    # 91 + 10-digit subscriber number (12 digits total)
    if cleaned.startswith('91') and len(cleaned) > 10:
        candidates.append(cleaned[2:])
    # Trunk prefix 0 + 10-digit subscriber number
    if cleaned.startswith('0') and len(cleaned) == 11:
        candidates.append(cleaned[1:])
    candidates.append(cleaned)

    for candidate in candidates:
        if INDIAN_MOBILE_BODY.fullmatch(candidate):
            return candidate
    return None
