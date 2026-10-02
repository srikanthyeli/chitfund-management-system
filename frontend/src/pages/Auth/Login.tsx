import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../core/AuthContext';
import { useTheme } from '../../core/useTheme';
import { Sun, Moon, Eye, EyeOff } from 'lucide-react';
import { LanguageSwitcher } from '../../components/common/LanguageSwitcher';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const { theme, toggle: toggleTheme } = useTheme();
  const { t } = useTranslation(['auth', 'common']);

  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleMobileChange = (val: string) => {
    setMobile(val);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    if (!mobile || !password) {
      setLoading(false);
      return;
    }

    const deviceId = navigator.userAgent;

    const result = await login({ mobile, password, device_id: deviceId, device_name: 'Browser' });

    setLoading(false);

    if (result.success) {
      let defaultDashboard = '/member/dashboard';
      if (result.user.role === 'ADMIN' || result.user.role === 'SUPER_ADMIN') {
        defaultDashboard = '/admin/organizers';
      } else if (result.user.role === 'ORGANIZER') {
        defaultDashboard = '/organizer/dashboard';
      }

      const from = location.state?.from?.pathname || defaultDashboard;
      navigate(from, { replace: true });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <div className="fixed top-4 right-4 flex items-center gap-2">
        <LanguageSwitcher />
        <button
          onClick={toggleTheme}
          className="touch-target p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 shadow-sm flex items-center justify-center"
          aria-label={t('common:toggle_theme')}
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 sm:p-8 border border-gray-100 dark:border-gray-700">
        <div className="text-center mb-8 flex flex-col items-center">
          <img src="/logo.png" alt={t('common:app_brand')} className="w-20 h-20 mb-4 rounded-2xl shadow-md border-2 border-purple-100 dark:border-purple-900/30" />
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">{t('common:app_brand')}</h2>
          <p className="text-base text-gray-500 dark:text-gray-400 mt-2">
            {t('auth:login_subtitle')}
          </p>
        </div>

        <form onSubmit={handleLoginSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('auth:login_mobile')}
            </label>
            <input
              type="tel"
              inputMode="numeric"
              autoComplete="tel"
              value={mobile}
              onChange={(e) => handleMobileChange(e.target.value)}
              className="touch-target w-full px-4 py-3.5 text-base rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
              placeholder={t('auth:login_mobile_placeholder')}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('auth:login_password')}
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="touch-target w-full px-4 py-3.5 text-base rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all pr-12"
                placeholder={t('auth:login_password_placeholder')}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 touch-target"
                aria-label={t('auth:login_toggle_password')}
              >
                {showPassword ? <EyeOff size={22} /> : <Eye size={22} />}
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading || !mobile || !password}
            className={`touch-target w-full py-3.5 px-4 rounded-xl text-white text-base font-semibold bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/20 transition-all ${
              loading ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {loading ? t('auth:login_loading') : t('auth:login_button')}
          </button>
        </form>
      </div>
    </div>
  );
};
