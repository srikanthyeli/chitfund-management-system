import React, { useEffect, useState } from 'react';
import { memberPortalApi } from '../api/memberPortalApi';
import type { MemberDashboardResponse } from '../api/memberPortalApi';
import { IndianRupee, Briefcase, Calendar, Trophy, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export const MemberDashboardPage: React.FC = () => {
  const { t } = useTranslation(['dashboard', 'common']);
  const [data, setData] = useState<MemberDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await memberPortalApi.getDashboard();
        setData(response);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-4 flex justify-center"><div className="animate-pulse flex space-x-4"><div className="h-4 bg-gray-200 rounded w-3/4"></div></div></div>;
  }

  if (!data) {
    return <div className="p-4 text-center text-gray-500">{t('common:error')}</div>;
  }

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('dashboard:dashboard_welcome')}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard:dashboard_summary')}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center text-purple-600 dark:text-purple-400">
            <Briefcase size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Chits</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{data.stats.active_chit_groups}</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400">
            <Trophy size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Shares Held</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{data.stats.total_shares_held}</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-red-200 dark:border-red-900/30 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center text-red-600 dark:text-red-400">
            <AlertCircle size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Overdue Amount</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">₹{data.stats.pending_overdue_amount}</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center text-green-600 dark:text-green-400">
            <IndianRupee size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Dividends Earned</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">₹{data.stats.total_dividends_earned}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center"><Calendar className="w-5 h-5 mr-2 text-purple-600" /> Upcoming Dues</h2>
            <Link to="/member/payments" className="text-sm text-purple-600 hover:text-purple-700 font-medium">{t('common:view')}</Link>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {data.upcoming_dues.length > 0 ? data.upcoming_dues.map(due => (
              <div key={`${due.chit_group_id}-${due.month_number}`} className="p-4 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">{due.chit_group_name}</p>
                  <p className="text-xs text-gray-500">Month {due.month_number} • Due: {due.due_date || 'N/A'}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-red-600">₹{due.amount_due}</p>
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">
                    {due.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            )) : (
              <div className="p-8 text-center text-gray-500">{t('common:empty_state')}</div>
            )}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center"><IndianRupee className="w-5 h-5 mr-2 text-green-600" /> Recent Payments</h2>
            <Link to="/member/receipts" className="text-sm text-purple-600 hover:text-purple-700 font-medium">{t('common:view')}</Link>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {data.recent_payments.length > 0 ? data.recent_payments.map(payment => (
              <div key={payment.receipt_id} className="p-4 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">{payment.chit_group_name}</p>
                  <p className="text-xs text-gray-500">{new Date(payment.payment_date).toLocaleDateString()} • {payment.receipt_number}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-green-600">₹{payment.amount}</p>
                </div>
              </div>
            )) : (
              <div className="p-8 text-center text-gray-500">{t('common:empty_state')}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
