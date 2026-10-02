import React from 'react';
import clsx from 'clsx';

export type MoneyTextSize = 'sm' | 'md' | 'lg';

interface MoneyTextProps {
  amount: number | string | null | undefined;
  className?: string;
  size?: MoneyTextSize;
  /** Show fraction digits (default false for village readability) */
  showPaise?: boolean;
  /** Prefix like "-" for bonus subtraction */
  prefix?: string;
}

const sizeClass: Record<MoneyTextSize, string> = {
  sm: 'text-base font-bold',
  md: 'money-text',
  lg: 'money-text-lg',
};

export function formatINR(
  amount: number | string | null | undefined,
  showPaise = false
): string {
  if (amount == null || amount === '') {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: showPaise ? 2 : 0,
      minimumFractionDigits: showPaise ? 2 : 0,
    }).format(0);
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: showPaise ? 2 : 0,
    minimumFractionDigits: showPaise ? 2 : 0,
  }).format(Number(amount));
}

export const MoneyText: React.FC<MoneyTextProps> = ({
  amount,
  className,
  size = 'md',
  showPaise = false,
  prefix = '',
}) => {
  return (
    <span className={clsx(sizeClass[size], 'tabular-nums', className)}>
      {prefix}
      {formatINR(amount, showPaise)}
    </span>
  );
};

export default MoneyText;
