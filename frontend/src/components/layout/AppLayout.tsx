import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Home, Users, Briefcase, IndianRupee, Menu, Bell, X, LogOut, Settings, ChevronLeft, ChevronRight, Wallet, Trophy, PieChart, MoreHorizontal } from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../../core/AuthContext';

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => localStorage.getItem('sidebar_collapsed') === 'true');

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => {
      const newVal = !prev;
      localStorage.setItem('sidebar_collapsed', String(newVal));
      return newVal;
    });
  };

  const getNavItems = () => {
    if (user?.role === 'ADMIN') {
      return [
        { path: '/admin/organizers', label: 'Organizers', icon: Users }
      ];
    } else if (user?.role === 'ORGANIZER') {
      return [
        { path: '/organizer/dashboard', label: 'Home', icon: Home },
        { path: '/organizer/members', label: 'Members', icon: Users },
        { path: '/organizer/chit-groups', label: 'Chits', icon: Briefcase },
        { path: '/organizer/collections', label: 'Collections', icon: Wallet },
        { path: '/organizer/winner-payouts', label: 'Payouts', icon: Trophy },
        { path: '/organizer/financial-summary', label: 'Summary', icon: PieChart },
      ];
    }
    return [];
  };

  const navItems = getNavItems();

  return (
    <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-900 overflow-hidden relative">
      {/* Desktop/Tablet Sidebar */}
      <aside className={clsx(
        "hidden md:flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 shadow-sm z-10 transition-all duration-300 ease-in-out",
        isSidebarCollapsed ? "w-20" : "w-64"
      )}>
        <div className={clsx("p-6 flex items-center justify-between", isSidebarCollapsed && "flex-col space-y-4 px-2")}>
          {!isSidebarCollapsed ? (
            <div className="flex items-center space-x-3 overflow-hidden">
              <img src="/logo.png" alt="Logo" className="w-8 h-8 rounded-lg shadow-sm border border-purple-100 dark:border-purple-900/30 shrink-0" />
              <div className="min-w-0">
                <h1 className="text-lg font-bold text-purple-600 dark:text-purple-400 truncate">ChitMate</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{user?.role === 'ADMIN' ? 'Admin Portal' : 'Organizer Portal'}</p>
              </div>
            </div>
          ) : (
            <img src="/logo.png" alt="Logo" className="w-10 h-10 rounded-lg shadow-sm border border-purple-100 dark:border-purple-900/30 shrink-0" />
          )}
          <button
            onClick={toggleSidebar}
            className={clsx(
              "p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors",
              isSidebarCollapsed && "mt-2"
            )}
            title={isSidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isSidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>
        
        <nav className={clsx("flex-1 py-4 space-y-2 overflow-y-auto", isSidebarCollapsed ? "px-2" : "px-4")}>
          {navItems.map((item) => (
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
        
        <div className={clsx("p-4 border-t border-gray-200 dark:border-gray-700", isSidebarCollapsed && "flex flex-col items-center px-2")}>
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

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden pb-16 md:pb-0 relative bg-gray-50 dark:bg-gray-900">
        {/* Mobile Header */}
        <header className="md:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 sticky top-0 z-10 flex justify-between items-center shadow-sm">
          <div className="flex items-center space-x-2">
            <img src="/logo.png" alt="Logo" className="w-8 h-8 rounded-lg shadow-sm border border-purple-100 dark:border-purple-900/30 shrink-0" />
            <h1 className="text-lg font-bold text-purple-600 dark:text-purple-400">ChitMate</h1>
          </div>
          <div className="flex items-center space-x-4 text-gray-600 dark:text-gray-400">
            <button className="relative p-1">
              <Bell size={24} />
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
            </button>
            <button onClick={() => setIsMobileMenuOpen(true)} className="p-1">
              <Menu size={28} />
            </button>
          </div>
        </header>

        {/* Mobile Full-Screen Menu Drawer */}
        {isMobileMenuOpen && (
          <div className="md:hidden fixed inset-0 bg-white dark:bg-gray-900 z-50 flex flex-col p-4 animate-in slide-in-from-right duration-200">
            <div className="flex justify-between items-center mb-8 border-b border-gray-100 dark:border-gray-800 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 font-bold">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <div>
                  <p className="font-bold text-gray-900 dark:text-white">{user?.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{user?.role}</p>
                </div>
              </div>
              <button onClick={() => setIsMobileMenuOpen(false)} className="text-gray-500 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors">
                <X size={28} />
              </button>
            </div>
            <nav className="flex flex-col space-y-2 px-2 text-lg font-medium text-gray-700 dark:text-gray-300">
              {navItems.slice(5).map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center space-x-3 p-3 rounded-xl transition-colors',
                      isActive ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                    )
                  }
                >
                  <item.icon size={22} className={clsx(!location.pathname.startsWith(item.path) && "text-gray-400")} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
              <div className="h-px bg-gray-100 dark:bg-gray-800 my-2"></div>
              <a href="#" className="flex items-center space-x-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"><Settings size={22} className="text-gray-400" /><span>Settings</span></a>
              <button onClick={logout} className="flex items-center space-x-3 p-3 rounded-xl text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors mt-auto border-t border-gray-100 dark:border-gray-800 pt-4 text-left w-full"><LogOut size={22} /><span>Log Out</span></button>
            </nav>
          </div>
        )}

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-0 sm:p-4">
          <Outlet />
        </div>

        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex justify-around items-center h-16 z-20 pb-safe shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.1)] overflow-x-auto px-1">
          {navItems.slice(0, 5).map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={clsx(
                  'flex flex-col items-center justify-center min-w-[60px] flex-1 h-full space-y-1 transition-all',
                  isActive ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                )}
              >
                <item.icon size={22} className={isActive ? 'stroke-[2.5]' : 'stroke-[1.5]'} />
                <span className={clsx("text-[9px] truncate w-full text-center px-0.5", isActive ? "font-bold" : "font-medium")}>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </main>
    </div>
  );
};
