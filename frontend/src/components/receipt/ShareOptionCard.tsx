import React, { useState, forwardRef } from 'react';
import type { ShareApp } from '../../services/shareService';

interface ShareOption {
  id: ShareApp;
  label: string;
  icon: React.ReactNode;
  bgColor: string;
  textColor: string;
}

interface ShareOptionCardProps {
  option: ShareOption;
  onClick: (app: ShareApp) => void;
  disabled?: boolean;
}

export const ShareOptionCard = forwardRef<HTMLButtonElement, ShareOptionCardProps>(({ option, onClick, disabled }, ref) => {
  const [pressed, setPressed] = useState(false);

  const handleClick = () => {
    if (disabled) return;
    setPressed(true);
    setTimeout(() => setPressed(false), 200);
    onClick(option.id);
  };

  return (
    <button
      ref={ref}
      onClick={handleClick}
      disabled={disabled}
      aria-label={`Share via ${option.label}`}
      className={`
        relative flex flex-col items-center justify-center w-full min-h-[110px] gap-2 p-4 rounded-3xl
        border border-gray-100 dark:border-gray-700
        bg-white dark:bg-gray-800
        shadow-sm hover:shadow-md
        transition-all duration-150
        hover:-translate-y-0.5
        focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-500
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0
        ${pressed ? 'scale-95' : 'scale-100'}
      `}
    >
      <div
        className={`w-12 h-12 rounded-xl flex items-center justify-center ${option.bgColor} transition-transform`}
      >
        {option.icon}
      </div>
      <span className={`text-xs font-semibold ${option.textColor} dark:text-gray-200`}>
        {option.label}
      </span>
    </button>
  );
});

ShareOptionCard.displayName = 'ShareOptionCard';
export type { ShareOption };
