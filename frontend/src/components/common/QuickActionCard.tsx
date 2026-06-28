import React from 'react';
import { Link } from 'react-router-dom';

interface QuickActionCardProps {
  title: string;
  description?: string;
  icon: React.ReactNode;
  to?: string;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  colorClass?: string;
}

export const QuickActionCard: React.FC<QuickActionCardProps> = ({
  title,
  description,
  icon,
  to,
  onClick,
  disabled = false,
  loading = false,
  colorClass = 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
}) => {
  const inner = (
    <div className="flex flex-col items-center justify-center gap-2.5 p-4 min-h-[96px] text-center select-none">
      <div className={`w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-110 ${colorClass}`}>
        {loading ? (
          <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
        ) : icon}
      </div>
      <div>
        <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 leading-tight">{title}</p>
        {description && <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5 leading-tight">{description}</p>}
      </div>
    </div>
  );

  const base =
    'group relative overflow-hidden rounded-2xl border bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-all duration-200 w-full active:scale-[0.97]';
  const activeClass = `${base} hover:shadow-lg hover:border-purple-300 dark:hover:border-purple-700 hover:-translate-y-0.5 cursor-pointer`;
  const disabledClass = `${base} opacity-50 cursor-not-allowed`;

  if (disabled) {
    return (
      <div className={disabledClass} title="Coming soon">
        {inner}
      </div>
    );
  }

  if (to) {
    return (
      <Link to={to} className={activeClass}>
        <Ripple />
        {inner}
      </Link>
    );
  }

  return (
    <button onClick={onClick} className={activeClass}>
      <Ripple />
      {inner}
    </button>
  );
};

const Ripple: React.FC = () => (
  <span
    className="absolute inset-0 pointer-events-none"
    aria-hidden
    onMouseDown={(e) => {
      const btn = e.currentTarget.parentElement as HTMLElement;
      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 1.4;
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      const ripple = document.createElement('span');
      ripple.style.cssText = `position:absolute;border-radius:50%;background:rgba(95,37,159,0.12);width:${size}px;height:${size}px;left:${x}px;top:${y}px;transform:scale(0);animation:ripple-anim 0.5s ease-out forwards;pointer-events:none`;
      if (!document.getElementById('ripple-style')) {
        const s = document.createElement('style');
        s.id = 'ripple-style';
        s.textContent = '@keyframes ripple-anim{to{transform:scale(1);opacity:0}}';
        document.head.appendChild(s);
      }
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 500);
    }}
  />
);
