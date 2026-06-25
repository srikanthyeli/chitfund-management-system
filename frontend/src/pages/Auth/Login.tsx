import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../core/AuthContext';
import { Eye, EyeOff, AlertTriangle } from 'lucide-react';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, forceLogin } = useAuth();
  
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

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
    
    // Minimal validation
    if (!mobile || !password) {
      setLoading(false);
      return;
    }

    const deviceId = navigator.userAgent; // simple placeholder
    
    let result;
    if (forceLoginChecked) {
      result = await forceLogin({ mobile, password, device_id: deviceId, device_name: 'Browser (Force)' });
    } else {
      result = await login({ mobile, password, device_id: deviceId, device_name: 'Browser' });
    }
    
    setLoading(false);
    
    if (result.success) {
      const from = location.state?.from?.pathname || (result.user.role === 'ADMIN' ? '/admin/organizers' : '/organizer/dashboard');
      navigate(from, { replace: true });
    } else if (result.forceLoginRequired) {
      setForceLoginRequired(true);
      setErrorMessage(result.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8 border border-gray-100 dark:border-gray-700">
        <div className="text-center mb-8 flex flex-col items-center">
          <img src="/logo.png" alt="ChitMate Logo" className="w-20 h-20 mb-4 rounded-2xl shadow-md border-2 border-purple-100 dark:border-purple-900/30" />
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">ChitMate</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Sign in to your account</p>
        </div>

        {forceLoginRequired && (
          <div className="p-4 mb-6 rounded-lg bg-red-50 dark:bg-red-900/25 border border-red-200 dark:border-red-800/30 flex items-start space-x-3 text-red-800 dark:text-red-300 text-sm">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">{errorMessage}</p>
              <p className="mt-1 text-red-700 dark:text-red-400">
                Please check the option below to log out other devices and sign in.
              </p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Mobile Number</label>
            <input
              type="tel"
              value={mobile}
              onChange={(e) => handleMobileChange(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
              placeholder="Enter mobile number"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                placeholder="Enter password"
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
            {loading ? 'Signing in...' : forceLoginChecked ? 'Log out other devices & Sign In' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};
