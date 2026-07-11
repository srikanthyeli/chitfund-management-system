import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../core/AuthContext';
import { useTheme } from '../../core/useTheme';
import { AlertTriangle, Sun, Moon, ArrowLeft } from 'lucide-react';
import { LanguageSwitcher } from '../../components/common/LanguageSwitcher';
import toast from 'react-hot-toast';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { requestLoginOtp, login, forceLogin } = useAuth();
  const { theme, toggle: toggleTheme } = useTheme();
  const { t } = useTranslation(['auth', 'common']);
  
  const [mobile, setMobile] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'request' | 'verify'>('request');

  const [forceLoginRequired, setForceLoginRequired] = useState(false);
  const [forceLoginChecked, setForceLoginChecked] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleMobileChange = (val: string) => {
    setMobile(val);
    if (forceLoginRequired) {
      setForceLoginRequired(false);
      setForceLoginChecked(false);
    }
  };

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mobile) return;
    setLoading(true);
    
    const result = await requestLoginOtp(mobile);
    setLoading(false);
    
    if (result.success) {
      setStep('verify');
      toast.success(result.message || 'OTP sent successfully');
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    if (!mobile || !otp) {
      setLoading(false);
      return;
    }

    const deviceId = navigator.userAgent; 
    
    let result;
    if (forceLoginChecked) {
      result = await forceLogin({ mobile, otp, device_id: deviceId, device_name: 'Browser (Force)' });
    } else {
      result = await login({ mobile, otp, device_id: deviceId, device_name: 'Browser' });
    }
    
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
    } else if (result.forceLoginRequired) {
      setForceLoginRequired(true);
      setErrorMessage(result.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <div className="fixed top-4 right-4 flex items-center gap-2">
        <LanguageSwitcher />
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 shadow-sm"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8 border border-gray-100 dark:border-gray-700">
        <div className="text-center mb-8 flex flex-col items-center">
          <img src="/logo.png" alt="ChitMate Logo" className="w-20 h-20 mb-4 rounded-2xl shadow-md border-2 border-purple-100 dark:border-purple-900/30" />
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">ChitMate</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {step === 'request' ? t('auth:login_subtitle') : 'Enter OTP to securely log in'}
          </p>
        </div>

        {forceLoginRequired && (
          <div className="p-4 mb-6 rounded-lg bg-red-50 dark:bg-red-900/25 border border-red-200 dark:border-red-800/30 flex items-start space-x-3 text-red-800 dark:text-red-300 text-sm">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">{errorMessage}</p>
              <p className="mt-1 text-red-700 dark:text-red-400">
                {t('auth:login_force_warning')}
              </p>
            </div>
          </div>
        )}

        {step === 'request' ? (
          <form onSubmit={handleRequestOtp} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('auth:login_mobile')}</label>
              <input
                type="tel"
                value={mobile}
                onChange={(e) => handleMobileChange(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                placeholder={t('auth:login_mobile_placeholder')}
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading || !mobile}
              className={`w-full py-3 px-4 rounded-lg text-white font-medium bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/20 transition-all ${
                loading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Sending OTP...' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleLoginSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">6-Digit OTP</label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all text-center tracking-widest font-mono text-lg"
                placeholder="------"
                maxLength={6}
                required
              />
            </div>

            {forceLoginRequired && (
              <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/30 rounded-lg border border-gray-200 dark:border-gray-700">
                <input
                  type="checkbox"
                  id="forceLoginCheckbox"
                  checked={forceLoginChecked}
                  onChange={(e) => setForceLoginChecked(e.target.checked)}
                  className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <label htmlFor="forceLoginCheckbox" className="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer select-none">
                  Log out other devices and sign in here
                </label>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !otp}
              className={`w-full py-3 px-4 rounded-lg text-white font-medium bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/20 transition-all ${
                loading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {loading ? t('auth:login_loading') : forceLoginChecked ? t('auth:login_force_signin') : t('auth:login_button')}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => { setStep('request'); setOtp(''); }}
                className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Change Mobile Number
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
