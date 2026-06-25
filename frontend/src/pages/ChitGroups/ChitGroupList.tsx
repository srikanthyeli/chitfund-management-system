import React, { useState, useEffect } from 'react';
import { Plus, Search, Calendar, Folder, UserCheck, Play, Briefcase } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../core/api';
import toast from 'react-hot-toast';
import clsx from 'clsx';

interface ChitGroupListItem {
  id: string;
  chit_code: string;
  chit_name: string;
  total_chit_value: number;
  monthly_installment_per_share: number;
  total_shares: number;
  allocated_shares: number;
  available_shares: number;
  start_date: string;
  status: 'DRAFT' | 'READY_TO_START' | 'ACTIVE' | 'CANCELLED';
}

interface SummaryData {
  total_chits: number;
  draft_chits: number;
  ready_to_start_chits: number;
  active_chits: number;
  total_allocated_shares: number;
  total_available_shares: number;
  upcoming_chits_count: number;
}

export const ChitGroupList: React.FC = () => {
  const navigate = useNavigate();
  const [chits, setChits] = useState<ChitGroupListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const limit = 15;
  
  const [summary, setSummary] = useState<SummaryData>({
    total_chits: 0,
    draft_chits: 0,
    ready_to_start_chits: 0,
    active_chits: 0,
    total_allocated_shares: 0,
    total_available_shares: 0,
    upcoming_chits_count: 0
  });

  const fetchSummary = async () => {
    try {
      const response = await api.get('/chit-groups/summary');
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to load summary stats');
    }
  };

  // Debounce search input to minimize API calls
  useEffect(() => {
    const handler = setTimeout(() => {
      setSearch(searchInput);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  const fetchChits = async (pageToFetch: number, isReset: boolean) => {
    if (isReset) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      let url = `/chit-groups?page=${pageToFetch}&page_size=${limit}`;
      if (search.trim()) {
        url += `&search=${encodeURIComponent(search.trim())}`;
      }
      if (statusFilter !== 'all') {
        url += `&status=${statusFilter}`;
      }

      const response = await api.get(url);
      const items = response.data.items || [];
      const newTotal = response.data.total || 0;

      setChits((prev) => (isReset ? items : [...prev, ...items]));
      setTotal(newTotal);
    } catch (error) {
      toast.error('Failed to load chit groups');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  // Reset page and list when search or statusFilter changes
  useEffect(() => {
    setPage(1);
    fetchChits(1, true);
  }, [search, statusFilter]);

  // Load next pages
  useEffect(() => {
    if (page > 1) {
      fetchChits(page, false);
    }
  }, [page]);

  // IntersectionObserver for Infinite Scroll
  const observerRef = React.useRef<IntersectionObserver | null>(null);
  const sentinelRef = React.useCallback(
    (node: HTMLDivElement | null) => {
      if (loading || loadingMore) return;
      if (observerRef.current) observerRef.current.disconnect();

      const hasMore = chits.length < total;
      if (!hasMore) return;

      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          setPage((prev) => prev + 1);
        }
      });

      if (node) observerRef.current.observe(node);
    },
    [loading, loadingMore, chits.length, total]
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DRAFT':
        return 'bg-amber-50 text-amber-700 dark:bg-amber-950/20 dark:text-amber-400';
      case 'READY_TO_START':
        return 'bg-blue-50 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400';
      case 'ACTIVE':
        return 'bg-green-50 text-green-700 dark:bg-green-950/20 dark:text-green-400';
      case 'CANCELLED':
        return 'bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400';
      default:
        return 'bg-slate-50 text-slate-700 dark:bg-gray-800 dark:text-gray-400';
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-1 sm:p-4 pb-20">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Chit Groups</h1>
          <p className="text-sm text-slate-500">Organize chit groups, allocate member shares, and start funds</p>
        </div>
        <Link
          to="/organizer/chit-groups/new"
          className="inline-flex items-center justify-center space-x-2 bg-primary hover:bg-primary-dark text-white px-5 py-2.5 rounded-xl font-medium text-sm transition-colors shadow-sm self-start sm:self-auto"
        >
          <Plus size={18} />
          <span>New Chit Group</span>
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/20 text-purple-600 dark:text-purple-400">
            <Briefcase size={20} />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Total Groups</p>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">{summary.total_chits}</h3>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400">
            <Play size={20} />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Active</p>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">{summary.active_chits}</h3>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400">
            <UserCheck size={20} />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Ready to Start</p>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">{summary.ready_to_start_chits}</h3>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400">
            <Folder size={20} />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Draft / Allocating</p>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">{summary.draft_chits}</h3>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-sm border border-slate-100 dark:border-gray-700 flex flex-col md:flex-row md:items-center gap-4">
        <div className="relative flex-1">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={18} />
          </span>
          <input
            type="text"
            placeholder="Search by chit group name or code..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        <div className="flex space-x-2 overflow-x-auto">
          {['all', 'DRAFT', 'READY_TO_START', 'ACTIVE', 'CANCELLED'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={clsx(
                "px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-colors whitespace-nowrap",
                statusFilter === status
                  ? "bg-primary text-white"
                  : "bg-slate-100 text-slate-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-slate-200"
              )}
            >
              {status === 'all' ? 'All Status' : status.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* List Area */}
      {loading ? (
        <div className="flex justify-center py-12 text-slate-500">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent"></div>
            <span>Loading chit groups...</span>
          </div>
        </div>
      ) : chits.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 text-center py-16 rounded-2xl border border-slate-100 dark:border-gray-700">
          <Briefcase className="mx-auto text-slate-300 dark:text-gray-600 mb-4" size={48} />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Chit Groups Found</h3>
          <p className="text-slate-500 text-sm mt-1 max-w-sm mx-auto">
            {search || statusFilter !== 'all'
              ? 'Try adjusting your search terms or filters'
              : 'Create your first chit group using the "New Chit Group" button above to start onboarding members.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          
          {/* Desktop Table View */}
          <div className="hidden md:block bg-white dark:bg-gray-800 rounded-2xl border border-slate-100 dark:border-gray-700 overflow-hidden shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-gray-855 text-slate-500 dark:text-gray-400 font-semibold text-xs uppercase tracking-wider border-b border-slate-100 dark:border-gray-700">
                  <th className="px-6 py-4">Code</th>
                  <th className="px-6 py-4">Group Name</th>
                  <th className="px-6 py-4">Chit Value</th>
                  <th className="px-6 py-4">Allocated Shares</th>
                  <th className="px-6 py-4">Start Date</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-gray-700 text-sm text-slate-700 dark:text-gray-300">
                {chits.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => navigate(`/organizer/chit-groups/${c.id}`)}
                    className="hover:bg-slate-50 dark:hover:bg-gray-750 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 font-mono text-xs font-bold text-slate-500">{c.chit_code}</td>
                    <td className="px-6 py-4 font-bold text-slate-800 dark:text-white">
                      <div>{c.chit_name}</div>
                      <div className="text-xs text-slate-400 font-normal mt-0.5">
                        ₹{Number(c.monthly_installment_per_share).toLocaleString('en-IN')}/mo • {c.total_shares} shares
                      </div>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-800 dark:text-slate-200">
                      ₹{Number(c.total_chit_value).toLocaleString('en-IN')}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-slate-100 dark:bg-gray-700 h-2 rounded-full overflow-hidden">
                          <div 
                            className="bg-primary h-full rounded-full" 
                            style={{ width: `${(c.allocated_shares / c.total_shares) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-slate-600 dark:text-gray-400">
                          {c.allocated_shares}/{c.total_shares}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-1">
                        <Calendar size={14} className="text-slate-400" />
                        <span>{new Date(c.start_date).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={clsx(
                        "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider",
                        getStatusBadge(c.status)
                      )}>
                        {c.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-primary hover:text-primary-dark font-medium text-xs">Manage</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card List View */}
          <div className="block md:hidden space-y-3">
            {chits.map((c) => (
              <div
                key={c.id}
                onClick={() => navigate(`/organizer/chit-groups/${c.id}`)}
                className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-slate-100 dark:border-gray-700 active:bg-slate-50 dark:active:bg-gray-750 transition-colors shadow-sm space-y-3"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-slate-800 dark:text-white text-base">{c.chit_name}</h3>
                    <span className="font-mono text-xs font-bold text-slate-400">{c.chit_code}</span>
                  </div>
                  <span className={clsx(
                    "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider",
                    getStatusBadge(c.status)
                  )}>
                    {c.status.replace(/_/g, ' ')}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 border-y border-slate-50 dark:border-gray-700 py-2.5 text-xs">
                  <div>
                    <p className="text-slate-400">Total Value</p>
                    <p className="font-bold text-slate-800 dark:text-white">₹{Number(c.total_chit_value).toLocaleString('en-IN')}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Installment</p>
                    <p className="font-bold text-slate-800 dark:text-white">₹{Number(c.monthly_installment_per_share).toLocaleString('en-IN')}/mo</p>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs">
                  <div className="flex items-center space-x-1.5 text-slate-500">
                    <Calendar size={14} className="text-slate-400" />
                    <span>{new Date(c.start_date).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}</span>
                  </div>
                  <div className="font-semibold text-slate-700 dark:text-gray-300">
                    Allocated: {c.allocated_shares} / {c.total_shares}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Infinite Scroll Sentinel / Status */}
          <div
            ref={sentinelRef}
            className="flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-2xl border border-slate-100 dark:border-gray-700 shadow-sm text-sm"
          >
            {loadingMore ? (
              <div className="flex items-center space-x-2 text-slate-500 text-sm">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
                <span>Loading more groups...</span>
              </div>
            ) : chits.length < total ? (
              <span className="text-xs text-slate-400">Scroll down to load more</span>
            ) : (
              <span className="text-xs text-slate-400">
                Showing all {total} groups
              </span>
            )}
          </div>

        </div>
      )}
    </div>
  );
};
