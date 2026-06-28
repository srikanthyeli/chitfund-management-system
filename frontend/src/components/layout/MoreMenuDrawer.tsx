import React, { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { X, LogOut } from 'lucide-react';
import clsx from 'clsx';

export type MoreMenuItem = {
  path: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
};

export type MoreMenuGroup = {
  title: string;
  items: MoreMenuItem[];
};

interface Props {
  isOpen: boolean;
  onClose: () => void;
  groups: MoreMenuGroup[];
  onLogout: () => void;
  userName?: string;
  userRole?: string;
}

export const MoreMenuDrawer: React.FC<Props> = ({ isOpen, onClose, groups, onLogout, userName, userRole }) => {
  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  return (
    <>
      {/* Backdrop */}
      <div
        className={clsx(
          'md:hidden fixed inset-0 bg-black/40 z-40 transition-opacity duration-300',
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className={clsx(
          'md:hidden fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 rounded-b-3xl shadow-2xl transition-transform duration-300 ease-out max-h-[90vh] flex flex-col',
          isOpen ? 'translate-y-0' : '-translate-y-full'
        )}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1 shrink-0">
          <div className="w-10 h-1 rounded-full bg-gray-300 dark:bg-gray-600" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100 dark:border-gray-800 shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-full bg-purple-100 dark:bg-purple-900/40 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold text-sm">
              {userName?.charAt(0) || 'U'}
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white leading-tight">{userName}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500 capitalize">{userRole?.toLowerCase()}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 transition-colors"
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto flex-1 px-4 py-2 pb-6">
          {groups.map((group) => (
            <div key={group.title} className="mb-1">
              <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 dark:text-gray-500 px-3 pt-4 pb-1.5">
                {group.title}
              </p>
              <div className="space-y-0.5">
                {group.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      clsx(
                        'flex items-center space-x-3 px-3 py-3 rounded-xl transition-all duration-150 active:scale-[0.98]',
                        isActive
                          ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
                      )
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <span className={clsx(
                          'flex items-center justify-center w-9 h-9 rounded-xl shrink-0',
                          isActive
                            ? 'bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
                        )}>
                          <item.icon size={18} strokeWidth={isActive ? 2.5 : 1.8} />
                        </span>
                        <span className={clsx('text-sm flex-1', isActive ? 'font-semibold' : 'font-medium')}>
                          {item.label}
                        </span>
                        {item.badge ? (
                          <span className="bg-red-500 text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
                            {item.badge > 99 ? '99+' : item.badge}
                          </span>
                        ) : null}
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}

          {/* Logout */}
          <div className="mt-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <button
              onClick={() => { onClose(); onLogout(); }}
              className="flex items-center space-x-3 w-full px-3 py-3 rounded-xl text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all active:scale-[0.98]"
            >
              <span className="flex items-center justify-center w-9 h-9 rounded-xl bg-red-50 dark:bg-red-900/20 shrink-0">
                <LogOut size={18} />
              </span>
              <span className="text-sm font-semibold">Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
};
