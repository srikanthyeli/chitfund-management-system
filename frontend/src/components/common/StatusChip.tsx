import React from 'react';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

export type PaymentStatusKey =
  | 'PAID'
  | 'PARTIALLY_PAID'
  | 'OVERDUE'
  | 'PENDING'
  | 'DUE'
  | 'LATE'
  | string;

interface StatusChipProps {
  status: PaymentStatusKey;
  className?: string;
  /** Optional count prefix e.g. "3 Paid" */
  count?: number;
}

const STATUS_STYLES: Record<string, string> = {
  PAID: 'bg-[var(--color-status-paid-bg)] text-[var(--color-status-paid)] border border-[var(--color-status-paid)]/20',
  PARTIALLY_PAID: 'bg-[var(--color-status-due-bg)] text-[var(--color-status-due)] border border-[var(--color-status-due)]/20',
  DUE: 'bg-[var(--color-status-due-bg)] text-[var(--color-status-due)] border border-[var(--color-status-due)]/20',
  OVERDUE: 'bg-[var(--color-status-late-bg)] text-[var(--color-status-late)] border border-[var(--color-status-late)]/20',
  LATE: 'bg-[var(--color-status-late-bg)] text-[var(--color-status-late)] border border-[var(--color-status-late)]/20',
  PENDING: 'bg-[var(--color-status-pending-bg)] text-[var(--color-status-pending)] border border-[var(--color-status-pending)]/20',
};

const STATUS_I18N: Record<string, string> = {
  PAID: 'status_paid',
  PARTIALLY_PAID: 'status_partial',
  DUE: 'status_due',
  OVERDUE: 'status_late',
  LATE: 'status_late',
  PENDING: 'status_pending',
};

export const StatusChip: React.FC<StatusChipProps> = ({ status, className, count }) => {
  const { t } = useTranslation('common');
  const key = (status || 'PENDING').toUpperCase();
  const style = STATUS_STYLES[key] || STATUS_STYLES.PENDING;
  const labelKey = STATUS_I18N[key] || 'status_pending';
  const label = t(labelKey);

  return (
    <span
      className={clsx(
        'inline-flex items-center justify-center px-2.5 py-1 rounded-full text-xs sm:text-sm font-semibold whitespace-nowrap',
        style,
        className
      )}
    >
      {typeof count === 'number' ? `${count} ${label}` : label}
    </span>
  );
};

export default StatusChip;
