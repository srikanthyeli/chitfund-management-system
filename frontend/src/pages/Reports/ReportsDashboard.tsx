import React, { useEffect, useState } from 'react';
import { reportApi } from '../../core/reportApi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export const ReportsDashboard = () => {
  const { t } = useTranslation(['dashboard', 'collections', 'reports']);

  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await reportApi.getDashboardMetrics();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to load dashboard metrics', error);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading metrics...</div>;
  }

  if (!metrics) {
    return <div className="p-8 text-center text-red-500">Failed to load metrics.</div>;
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 pb-24">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reports & Analytics</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">{t('collections:collections_total')}</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">₹{metrics.total_collections.toLocaleString()}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">{t('dashboard:dashboard_pending_collections')}</p>
          <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">₹{metrics.pending_collections.toLocaleString()}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">{t('reports:reports_total_payouts')}</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">₹{metrics.total_winner_payouts.toLocaleString()}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Net Cash Flow</p>
          <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">₹{metrics.net_cash_flow.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="md:col-span-2 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Collection vs Expected</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'Collections', value: metrics.total_collections },
                { name: 'Pending', value: metrics.pending_collections }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#4F46E5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Detailed Reports</h2>
          <div className="flex flex-col gap-2">
            <Link to="/organizer/reports/collections" className="text-blue-600 dark:text-blue-400 hover:underline">Collection Report &rarr;</Link>
            <Link to="/organizer/reports/pending-collections" className="text-blue-600 dark:text-blue-400 hover:underline">Pending Collections &rarr;</Link>
            <Link to="/organizer/reports/auctions" className="text-blue-600 dark:text-blue-400 hover:underline">Auction Report &rarr;</Link>
            <Link to="/organizer/reports/winner-payouts" className="text-blue-600 dark:text-blue-400 hover:underline">Winner Payout Report &rarr;</Link>
            <Link to="/organizer/reports/member-financial" className="text-blue-600 dark:text-blue-400 hover:underline">Member Financial Report &rarr;</Link>
            <Link to="/organizer/reports/organizer-financial" className="text-blue-600 dark:text-blue-400 hover:underline">Organizer Financial Report &rarr;</Link>
            <Link to="/organizer/reports/chit-performance" className="text-blue-600 dark:text-blue-400 hover:underline">Chit Performance Report &rarr;</Link>
          </div>
        </div>
      </div>
    </div>
  );
};
