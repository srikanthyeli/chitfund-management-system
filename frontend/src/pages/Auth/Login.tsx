import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../core/AuthContext';
import { useTheme } from '../../core/useTheme';
import { Eye, EyeOff, AlertTriangle, Sun, Moon, ArrowLeft } from 'lucide-react';
import { LanguageSwitcher } from '../../components/common/LanguageSwitcher';
import api from '../../core/api'; // Assuming default api instance
import toast from 'react-hot-toast';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, forceLogin } = useAuth();
  const { theme, toggle: toggleTheme } = useTheme();
  const { t } = useTranslation(['auth', 'common']);
  
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [forceLoginRequired, setForceLoginRequired] = useState(false);
  const [forceLoginChecked, setForceLoginChecked] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Forgot Password State
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const handleMobileChange = (val: string) => {
    setMobile(val);
    if (forceLoginRequired) {
      setForceLoginRequired(false);
      setForceLoginChecked(false);
    }
  };

  const handlePasswordChange = (val: string) => {
    setPassword(val);
    if (forceLoginRequired) {
      setForceLoginRequired(false);
      setForceLoginChecked(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    if (!mobile || !password) {
      setLoading(false);
      return;
    }

    const deviceId = navigator.userAgent; 
    
    let result;
    if (forceLoginChecked) {
      result = await forceLogin({ mobile, password, device_id: deviceId, device_name: 'Browser (Force)' });
    } else {
      result = await login({ mobile, password, device_id: deviceId, device_name: 'Browser' });
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

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mobile) return;
    setLoading(true);
    try {
      await api.post('/auth/forgot-password/request-otp', { mobile });
      setOtpSent(true);
      toast.success('OTP sent successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mobile || !otp || !newPassword) return;
    setLoading(true);
    try {
      await api.post('/auth/forgot-password/reset', {
        mobile,
        otp,
        new_password: newPassword
      });
      toast.success('Password reset successfully. You can now login.');
      setIsForgotPassword(false);
      setOtpSent(false);
      setOtp('');
      setPassword(newPassword);
      setNewPassword('');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to reset password');
    } finally {
      setLoading(false);
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
            {isForgotPassword ? 'Reset your password' : t('auth:login_subtitle')}
          </p>
        </div>

        {!isForgotPassword ? (
          <>
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

            <form onSubmit={handleSubmit} className="space-y-6">
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

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{t('auth:login_password')}</label>
                  <button
                    type="button"
                    onClick={() => setIsForgotPassword(true)}
                    className="text-sm font-medium text-purple-600 hover:text-purple-500 dark:text-purple-400"
                  >
                    Forgot Password?
                  </button>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => handlePasswordChange(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                    placeholder={t('auth:login_password_placeholder')}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
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
                disabled={loading}
                className={`w-full py-3 px-4 rounded-lg text-white font-medium bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/20 transition-all ${
                  loading ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {loading ? t('auth:login_loading') : forceLoginChecked ? t('auth:login_force_signin') : t('auth:login_button')}
              </button>
            </form>
          </>
        ) : (
          <div className="space-y-6">
            {!otpSent ? (
              <form onSubmit={handleRequestOtp} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('auth:login_mobile')}
                  </label>
                  <input
                    type="tel"
                    required
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                    placeholder="Enter registered mobile number"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !mobile}
                  className="w-full py-3 px-4 rounded-lg text-white font-medium bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/20 transition-all disabled:opacity-50"
                >
                  {loading ? 'Sending OTP...' : 'Send OTP'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Enter OTP
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="Enter 6-digit OTP"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    required
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !otp || !newPassword}
                  className="w-full py-3 px-4 rounded-lg text-white font-medium bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/20 transition-all disabled:opacity-50"
                >
                  {loading ? 'Setting Password...' : 'Reset Password'}
                </button>
              </form>
            )}
            
            <div className="text-center">
              <button
                type="button"
                onClick={() => { setIsForgotPassword(false); setOtpSent(false); }}
                className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to Login
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
