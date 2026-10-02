import React, { useEffect, useState } from 'react';
import { useAuth } from '../../core/AuthContext';
import api from '../../core/api';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';
import {
  Users, IndianRupee, Activity, Calendar,
  Trophy, CheckCircle2, Clock, UserPlus,
  Wallet, Play, ChevronRight,
  Loader2,
} from 'lucide-react';
import { QuickActionCard } from '../../components/common/QuickActionCard';
import { MoneyText } from '../../components/common/MoneyText';

interface DashboardSummary {
  organizer_name: string;
  active_chits: number;
  total_members: number;
  collections_due_today: number;
  collections_received_today: number;
  pending_amount: number;
  auctions_today: number;
}

interface ActivityItem {
  id: string;
  type: string;
  description: string;
  timestamp: string;
}

const ACTIVITY_ICONS: Record<string, { icon: React.ReactNode; color: string }> = {
  member_joined: { icon: <UserPlus size={14} />, color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' },
  collection_done: { icon: <Wallet size={14} />, color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' },
  winner_paid: { icon: <Trophy size={14} />, color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' },
  receipt_shared: { icon: <CheckCircle2 size={14} />, color: 'bg-teal-100 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400' },
  auction_completed: { icon: <Play size={14} />, color: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400' },
};

export const OrganizerDashboard = () => {
  const { user } = useAuth();
  const { t, i18n } = useTranslation(['dashboard', 'common']);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'ORGANIZER') { setLoading(false); return; }
    const loadAll = async () => {
      try {
        const dashRes = await api.get('/dashboard/summary');
        if (dashRes.status === 200) setSummary(dashRes.data);
      } catch {
        toast.error(t('common:error'));
      } finally {
        setLoading(false);
      }
    };
    loadAll();
  }, [user, t]);

  const mockActivities: ActivityItem[] = [
    { id: '1', type: 'member_joined', description: t('dashboard:dashboard_activity_member_joined', 'New member onboarded to Chit Group A'), timestamp: t('dashboard:dashboard_activity_2m', '2 mins ago') },
    { id: '2', type: 'collection_done', description: t('dashboard:dashboard_activity_collection', '₹5,000 collected from Ramesh Kumar'), timestamp: t('dashboard:dashboard_activity_15m', '15 mins ago') },
    { id: '3', type: 'auction_completed', description: t('dashboard:dashboard_activity_auction', 'Auction #4 finalized for Group B'), timestamp: t('dashboard:dashboard_activity_1h', '1 hr ago') },
    { id: '4', type: 'winner_paid', description: t('dashboard:dashboard_activity_payout', 'Winner payout of ₹50,000 processed'), timestamp: t('dashboard:dashboard_activity_3h', '3 hrs ago') },
    { id: '5', type: 'receipt_shared', description: t('dashboard:dashboard_activity_receipt', 'Receipt shared to Priya Sharma via WhatsApp'), timestamp: t('dashboard:dashboard_activity_yesterday', 'Yesterday') },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <Loader2 className="animate-spin mr-2" size={20} /> {t('common:loading')}
      </div>
    );
  }

  const dateLocale = i18n.language?.startsWith('te') ? 'te-IN' : 'en-IN';

  const kpiCards = [
    { title: t('dashboard:dashboard_total_collections'), valueNode: <MoneyText amount={summary?.collections_received_today || 0} size="sm" className="text-gray-900 dark:text-white" />, icon: <IndianRupee size={18} />, color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' },
    { title: t('dashboard:dashboard_pending_collections'), valueNode: <MoneyText amount={summary?.pending_amount || 0} size="sm" className="text-gray-900 dark:text-white" />, icon: <Clock size={18} />, color: 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400' },
    { title: t('dashboard:dashboard_upcomming_payouts'), valueNode: <span className="text-base font-bold text-gray-900 dark:text-white">{summary?.auctions_today ? t('common:pending_count', { count: 1 }) : t('common:none')}</span>, icon: <Trophy size={18} />, color: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400' },
    { title: t('dashboard:dashboard_pending_auctions'), valueNode: <span className="text-base font-bold text-gray-900 dark:text-white">{summary?.auctions_today ? t('common:today_count', { count: summary.auctions_today }) : t('common:none')}</span>, icon: <Calendar size={18} />, color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' },
    { title: t('dashboard:dashboard_total_chit_groups'), valueNode: <span className="text-base font-bold text-gray-900 dark:text-white">{summary?.active_chits || 0}</span>, icon: <Activity size={18} />, color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' },
    { title: t('dashboard:dashboard_active_members'), valueNode: <span className="text-base font-bold text-gray-900 dark:text-white">{summary?.total_members || 0}</span>, icon: <Users size={18} />, color: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400' },
  ];

  const quickActions = [
    { title: t('dashboard:dashboard_add_member'), description: t('dashboard:dashboard_qa_add_member_desc'), icon: '➕', to: '/organizer/members/new', colorClass: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' },
    { title: t('dashboard:dashboard_create_collection'), description: t('dashboard:dashboard_qa_collection_desc'), icon: '💰', to: '/organizer/collections', colorClass: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' },
    { title: t('dashboard:dashboard_start_auction'), description: t('dashboard:dashboard_qa_auction_desc'), icon: '🏆', to: '/organizer/chit-groups', colorClass: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400' },
    { title: t('dashboard:dashboard_winner_payout'), description: t('dashboard:dashboard_qa_payout_desc'), icon: '💵', to: '/organizer/winner-payouts', colorClass: 'bg-teal-100 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400' },
    { title: t('dashboard:dashboard_bond_calculator'), description: t('dashboard:dashboard_qa_bond_desc'), icon: '🧮', to: '/dashboard/bond-calculator', colorClass: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' },
    { title: t('dashboard:dashboard_view_reports'), description: t('dashboard:dashboard_qa_reports_desc'), icon: '📊', to: '/organizer/reports', colorClass: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400' },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto p-4 sm:p-6 pb-24 sm:pb-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {t('dashboard:dashboard_organizer_welcome', { name: summary?.organizer_name || user?.name || 'Organizer' })}
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          {new Date().toLocaleDateString(dateLocale, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
        </p>
      </div>

      {/* 1. Today's Summary — KPI Cards */}
      <section>
        <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
          {t('dashboard:dashboard_summary')}
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {kpiCards.map((card) => (
            <KPICard key={card.title} title={card.title} valueNode={card.valueNode} icon={card.icon} color={card.color} />
          ))}
        </div>
      </section>

      {/* 2. Quick Actions */}
      <section>
        <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
          {t('dashboard:dashboard_quick_actions')}
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {quickActions.map((action) => (
            <QuickActionCard
              key={action.title}
              title={action.title}
              description={action.description}
              icon={<span className="text-xl leading-none">{action.icon}</span>}
              to={action.to}
              colorClass={action.colorClass}
            />
          ))}
        </div>
      </section>

      {/* 3. Recent Activities */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            {t('dashboard:dashboard_recent_activity')}
          </h2>
          <button className="text-sm text-purple-600 dark:text-purple-400 font-medium hover:underline flex items-center gap-1 touch-target">
            {t('common:view')} <ChevronRight size={13} />
          </button>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm divide-y divide-gray-50 dark:divide-gray-700/50">
          {mockActivities.map((item) => {
            const meta = ACTIVITY_ICONS[item.type] ?? ACTIVITY_ICONS.collection_done;
            return (
              <div key={item.id} className="flex items-center gap-3 px-4 py-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${meta.color}`}>
                  {meta.icon}
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 flex-1 leading-snug">{item.description}</p>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{item.timestamp}</span>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};

const KPICard = ({ title, valueNode, icon, color }: { title: string; valueNode: React.ReactNode; icon: React.ReactNode; color: string }) => (
  <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm p-3 flex flex-col items-center text-center gap-2 hover:shadow-md transition-shadow min-h-[96px]">
    <div className={`w-9 h-9 rounded-full flex items-center justify-center ${color}`}>{icon}</div>
    <p className="text-xs text-gray-500 dark:text-gray-400 font-medium leading-tight">{title}</p>
    <div className="leading-tight">{valueNode}</div>
  </div>
);
