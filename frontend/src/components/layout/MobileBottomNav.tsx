import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import clsx from 'clsx';

interface BottomNavItem {
  path: string;
  label: string;
  icon: React.ElementType;
  matchPrefix?: string;
}

interface Props {
  items: BottomNavItem[];
}

export const MobileBottomNav: React.FC<Props> = ({ items }) => {
  const location = useLocation();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 overflow-x-auto shadow-[0_-4px_20px_rgba(0,0,0,0.08)] safe-area-pb">
      <div className="flex items-center justify-around gap-1 px-1 min-h-[var(--touch-min)] h-[3.75rem]">
        {items.map((item) => {
          const isActive = item.matchPrefix
            ? location.pathname.startsWith(item.matchPrefix)
            : location.pathname.startsWith(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={clsx(
                'touch-target flex flex-col items-center justify-center min-w-[72px] px-2 rounded-2xl transition-all duration-200 active:scale-95 whitespace-nowrap',
                isActive
                  ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
                  : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
              )}
            >
              <span className="flex items-center justify-center w-9 h-9 rounded-2xl transition-all duration-200">
                <item.icon size={20} strokeWidth={isActive ? 2.5 : 1.8} />
              </span>
              <span className={clsx('text-xs sm:text-sm mt-0.5 leading-tight', isActive ? 'font-semibold' : 'font-medium')}>
                {item.label}
              </span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};
