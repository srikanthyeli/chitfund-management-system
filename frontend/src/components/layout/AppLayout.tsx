import React, { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import {
  Home, Users, Briefcase, IndianRupee, Bell, LogOut, Settings,
  ChevronLeft, ChevronRight, Wallet, Trophy, BarChart,
  Calculator, Receipt, BookOpen,
  Sun, Moon, Menu
} from 'lucide-react';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../core/AuthContext';
import { useTheme } from '../../core/useTheme';
import { MobileBottomNav } from './MobileBottomNav';
import { MoreMenuDrawer } from './MoreMenuDrawer';
import { LanguageSwitcher } from '../common/LanguageSwitcher';
import type { MoreMenuGroup } from './MoreMenuDrawer';

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { t } = useTranslation('common');
  const [isMoreOpen, setIsMoreOpen] = useState(false);
  const { theme, toggle: toggleTheme } = useTheme();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(
    () => localStorage.getItem('sidebar_collapsed') === 'true'
  );

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem('sidebar_collapsed', String(next));
      return next;
    });
  };

  // ── Organizer Nav Config ──────────────────────────────────────
  const organizerBottomItems = [
    { path: '/organizer/dashboard', label: t('navigation_dashboard'), icon: Home },
    { path: '/organizer/members', label: t('navigation_members'), icon: Users },
    { path: '/organizer/chit-groups', label: t('navigation_chitgroups'), icon: Briefcase },
    { path: '/organizer/collections', label: t('navigation_collections'), icon: Wallet },
    { path: '/organizer/winner-payouts', label: t('navigation_payouts'), icon: Trophy },
  ];

  const organizerMoreGroups: MoreMenuGroup[] = [
    {
      title: t('navigation_financial_utilities'),
      items: [
        { path: '/dashboard/bond-calculator', label: t('navigation_bondcalculator'), icon: Calculator },
        { path: '/organizer/reports', label: t('navigation_reports'), icon: BarChart },
      ],
    },
  ];

  const organizerDesktopItems = [
    { path: '/organizer/dashboard', label: t('navigation_dashboard'), icon: Home },
    { path: '/organizer/members', label: t('navigation_members'), icon: Users },
    { path: '/organizer/chit-groups', label: t('navigation_chitgroups'), icon: Briefcase },
    { path: '/organizer/collections', label: t('navigation_collections'), icon: Wallet },
    { path: '/organizer/winner-payouts', label: t('navigation_payouts'), icon: Trophy },
    { path: '/organizer/reports', label: t('navigation_reports'), icon: BarChart },
  ];

  // ── Member Nav Config ─────────────────────────────────────────
  const memberBottomItems = [
    { path: '/member/dashboard', label: t('navigation_dashboard'), icon: Home },
    { path: '/member/chits', label: t('navigation_my_chits'), icon: Briefcase },
    { path: '/member/payments', label: t('navigation_payments'), icon: IndianRupee },
    { path: '/member/passbook', label: t('navigation_passbook'), icon: BookOpen },
  ];

  const memberMoreGroups: MoreMenuGroup[] = [
    {
      title: t('navigation_account'),
      items: [
        { path: '/member/receipts', label: t('navigation_receipts'), icon: Receipt },
        { path: '/member/auction-results', label: t('navigation_auctions'), icon: Trophy },
        { path: '/member/winner-payouts', label: t('navigation_payouts'), icon: Wallet },
        { path: '/member/notifications', label: t('navigation_notifications'), icon: Bell },
        { path: '/member/profile', label: t('navigation_profile'), icon: Settings },
      ],
    },
  ];

  const memberDesktopItems = [
    { path: '/member/dashboard', label: t('navigation_dashboard'), icon: Home },
    { path: '/member/chits', label: t('navigation_my_chits'), icon: Briefcase },
    { path: '/member/payments', label: t('navigation_payments'), icon: IndianRupee },
    { path: '/member/receipts', label: t('navigation_receipts'), icon: Receipt },
    { path: '/member/passbook', label: t('navigation_passbook'), icon: BookOpen },
    { path: '/member/auction-results', label: t('navigation_auctions'), icon: Trophy },
    { path: '/member/winner-payouts', label: t('navigation_payouts'), icon: Wallet },
    { path: '/member/notifications', label: t('navigation_notifications'), icon: Bell },
    { path: '/member/profile', label: t('navigation_profile'), icon: Settings },
  ];

  // ── Admin Nav Config ──────────────────────────────────────────
  const adminDesktopItems = [
    { path: '/admin/organizers', label: t('navigation_organisers'), icon: Users },
  ];

  const adminBottomItems = [
    { path: '/admin/organizers', label: t('navigation_organisers'), icon: Users },
  ];

  const adminMoreGroups: MoreMenuGroup[] = [];

  // ── Role-based selection ──────────────────────────────────────
  const role = user?.role;
  const bottomItems = role === 'ORGANIZER' ? organizerBottomItems
    : role === 'MEMBER' ? memberBottomItems
    : adminBottomItems;

  const moreGroups = role === 'ORGANIZER' ? organizerMoreGroups
    : role === 'MEMBER' ? memberMoreGroups
    : adminMoreGroups;

  const desktopItems = role === 'ORGANIZER' ? organizerDesktopItems
    : role === 'MEMBER' ? memberDesktopItems
    : adminDesktopItems;

  return (
    <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-900 overflow-hidden relative">

      {/* ── Desktop/Tablet Sidebar ──────────────────────────────── */}
      <aside className={clsx(
        'hidden md:flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 shadow-sm z-10 transition-all duration-300 ease-in-out',
        isSidebarCollapsed ? 'w-20' : 'w-64'
      )}>
        <div className={clsx('p-6 flex items-center justify-between', isSidebarCollapsed && 'flex-col space-y-4 px-2')}>
          {!isSidebarCollapsed ? (
            <div className="flex items-center space-x-3 overflow-hidden">
              <img src="/logo.png" alt="Logo" className="w-8 h-8 rounded-lg shadow-sm border border-purple-100 dark:border-purple-900/30 shrink-0" />
              <div className="min-w-0">
                <h1 className="text-lg font-bold text-purple-600 dark:text-purple-400 truncate">ChitMate</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                  {role === 'ADMIN' ? t('portal_admin') : role === 'MEMBER' ? t('portal_member') : t('portal_organizer')}
                </p>
              </div>
            </div>
          ) : (
            <img src="/logo.png" alt="Logo" className="w-10 h-10 rounded-lg shadow-sm border border-purple-100 dark:border-purple-900/30 shrink-0" />
          )}
          <div className={clsx('flex items-center gap-1', isSidebarCollapsed && 'flex-col mt-2')}>
            {!isSidebarCollapsed && <LanguageSwitcher />}
            <button
              onClick={toggleTheme}
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              title={theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              onClick={toggleSidebar}
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              title={isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            >
              {isSidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
            </button>
          </div>
        </div>

        <nav className={clsx('flex-1 py-4 space-y-2 overflow-y-auto', isSidebarCollapsed ? 'px-2' : 'px-4')}>
          {desktopItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              title={isSidebarCollapsed ? item.label : undefined}
              className={({ isActive }) =>
                clsx(
                  'flex items-center rounded-xl transition-all font-medium',
                  isSidebarCollapsed ? 'justify-center p-3' : 'space-x-3 px-4 py-3',
                  isActive
                    ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-200'
                )
              }
            >
              <item.icon size={22} className="shrink-0" />
              {!isSidebarCollapsed && <span className="truncate">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className={clsx('p-4 border-t border-gray-200 dark:border-gray-700', isSidebarCollapsed && 'flex flex-col items-center px-2')}>
          {!isSidebarCollapsed ? (
            <>
              <div className="px-4 py-3 mb-2 rounded-xl bg-gray-50 dark:bg-gray-900">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.mobile}</p>
              </div>
              <button
                onClick={logout}
                className="flex items-center w-full space-x-3 px-4 py-3 rounded-xl text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all font-medium"
              >
                <LogOut size={22} className="shrink-0" />
                <span className="truncate">Sign Out</span>
              </button>
            </>
          ) : (
            <>
              <div className="w-10 h-10 mb-3 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold shrink-0" title={user?.name}>
                {user?.name?.charAt(0) || 'U'}
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-3 rounded-xl text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all flex items-center justify-center"
              >
                <LogOut size={22} className="shrink-0" />
              </button>
            </>
          )}
        </div>
      </aside>

      {/* ── Main Content ────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col overflow-hidden pb-0 relative bg-gray-50 dark:bg-gray-900">

        {/* Mobile Header */}
        <header className="md:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 h-14 sticky top-0 z-20 flex justify-between items-center shadow-sm">
          <div className="flex items-center space-x-2">
            <img src="/logo.png" alt="Logo" className="w-7 h-7 rounded-lg border border-purple-100 dark:border-purple-900/30 shrink-0" />
            <h1 className="text-base font-bold text-purple-600 dark:text-purple-400">ChitMate</h1>
          </div>
          <div className="flex items-center gap-1">
            <LanguageSwitcher />
            <button
              onClick={toggleTheme}
              className="p-2 text-gray-500 dark:text-gray-400"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button
              className="relative p-2 text-gray-500 dark:text-gray-400"
              aria-label="Notifications"
            >
              <Bell size={22} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-gray-800" />
            </button>
            <button
              onClick={() => setIsMoreOpen(true)}
              className="p-1 -mr-1 ml-1 text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400"
              aria-label="Open menu"
            >
              <Menu size={26} />
            </button>
          </div>
        </header>

        <MobileBottomNav
          items={bottomItems}
        />

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-0 sm:p-4 pb-20 md:pb-0">
          <Outlet />
        </div>
      </main>

      {/* ── More Menu Drawer ─────────────────────────────────────── */}
      <MoreMenuDrawer
        isOpen={isMoreOpen}
        onClose={() => setIsMoreOpen(false)}
        groups={moreGroups}
        onLogout={logout}
        userName={user?.name}
        userRole={user?.role}
      />
    </div>
  );
};
