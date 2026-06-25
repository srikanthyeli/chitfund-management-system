import React, { useEffect, useState } from 'react';
import { useAuth } from '../../core/AuthContext';
import api from '../../core/api';
import toast from 'react-hot-toast';
import { Users, IndianRupee, Activity, Calendar, PlusCircle, FileText, Play, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

interface DashboardSummary {
  organizer_name: string;
  active_chits: number;
  total_members: number;
  collections_due_today: number;
  collections_received_today: number;
  pending_amount: number;
  auctions_today: number;
}

export const OrganizerDashboard = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/dashboard/summary');
        setSummary(response.data);
      } catch (error) {
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    
    if (user?.role === 'ORGANIZER') {
      fetchSummary();
    } else {
      setLoading(false);
    }
  }, [user]);

  if (loading) return <div className="flex justify-center p-8 text-slate-500">Loading dashboard...</div>;

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-4 sm:p-6 pb-20 sm:pb-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome, {summary?.organizer_name || user?.name || 'Organizer'}
        </h1>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <KPICard title="Active Chits" value={summary?.active_chits || 0} icon={<Activity size={20} />} color="purple" />
        <KPICard title="Total Members" value={summary?.total_members || 0} icon={<Users size={20} />} color="blue" />
        <KPICard title="Auctions Today" value={summary?.auctions_today || 0} icon={<Calendar size={20} />} color="amber" />
        <KPICard title="Due Today" value={summary?.collections_due_today || 0} icon={<FileText size={20} />} color="indigo" />
        <KPICard title="Received Today" value={summary?.collections_received_today || 0} icon={<CheckCircle size={20} />} color="green" />
        <KPICard title="Pending Amount" value={`₹${summary?.pending_amount || 0}`} icon={<IndianRupee size={20} />} color="rose" />
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <QuickAction icon={<Users />} label="Add Member" to="/organizer/members/new" />
          <QuickAction icon={<PlusCircle />} label="Create Chit" disabled />
          <QuickAction icon={<Play />} label="Start Auction" disabled />
          <QuickAction icon={<IndianRupee />} label="Collect Payment" disabled />
        </div>
      </div>
    </div>
  );
};

const KPICard = ({ title, value, icon, color }: { title: string, value: string | number, icon: React.ReactNode, color: string }) => {
  const colorMap: Record<string, string> = {
    purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
    blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    amber: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
    indigo: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
    green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    rose: 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400',
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col items-center text-center justify-center space-y-2 hover:shadow-md transition-shadow">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${colorMap[color]}`}>
        {icon}
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{title}</p>
      <p className="text-xl font-bold text-gray-900 dark:text-white">{value}</p>
    </div>
  );
};

const QuickAction = ({ icon, label, to, disabled }: { icon: React.ReactNode, label: string, to?: string, disabled?: boolean }) => {
  if (to && !disabled) {
    return (
      <Link 
        to={to}
        className="bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center space-y-2 hover:shadow-md hover:border-purple-300 dark:hover:border-purple-900 transition-all text-center w-full"
      >
        <div className="text-purple-600 dark:text-purple-400">{icon}</div>
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 text-center">{label}</span>
      </Link>
    );
  }

  return (
    <button 
      disabled 
      className="bg-gray-50 dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center space-y-2 opacity-60 cursor-not-allowed group relative w-full"
    >
      <div className="text-gray-400 dark:text-gray-500">{icon}</div>
      <span className="text-sm font-medium text-gray-600 dark:text-gray-400 text-center">{label}</span>
      
      {/* Tooltip for Phase 1 */}
      <div className="absolute -top-10 scale-0 group-hover:scale-100 transition-transform bg-gray-900 text-white text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap z-30">
        Available in next phase
      </div>
    </button>
  );
};
