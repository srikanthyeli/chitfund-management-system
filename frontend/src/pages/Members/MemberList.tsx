import React, { useState, useEffect } from 'react';
import { Plus, Search, Phone, MapPin, User } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../core/api';
import toast from 'react-hot-toast';
import clsx from 'clsx';

interface MemberListItem {
  id: string;
  member_code: string;
  full_name: string;
  mobile: string;
  village: string | null;
  district: string | null;
  is_active: boolean;
  created_at: string;
}

export const MemberList: React.FC = () => {
  const navigate = useNavigate();
  const [members, setMembers] = useState<MemberListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [page, setPage] = useState(1);
  const limit = 15;

  // Debounce search input to minimize API calls
  useEffect(() => {
    const handler = setTimeout(() => {
      setSearch(searchInput);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  const fetchMembers = async (pageToFetch: number, isReset: boolean) => {
    if (isReset) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      let url = `/members?page=${pageToFetch}&limit=${limit}`;
      if (search.trim()) {
        url += `&search=${encodeURIComponent(search.trim())}`;
      }
      if (statusFilter === 'active') {
        url += `&is_active=true`;
      } else if (statusFilter === 'inactive') {
        url += `&is_active=false`;
      }

      const response = await api.get(url);
      const items = response.data.items || [];
      const newTotal = response.data.total || 0;

      setMembers((prev) => (isReset ? items : [...prev, ...items]));
      setTotal(newTotal);
    } catch (error) {
      toast.error('Failed to load members');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // Reset page and list when search or statusFilter changes
  useEffect(() => {
    setPage(1);
    fetchMembers(1, true);
  }, [search, statusFilter]);

  // Load next pages
  useEffect(() => {
    if (page > 1) {
      fetchMembers(page, false);
    }
  }, [page]);

  // IntersectionObserver for Infinite Scroll
  const observerRef = React.useRef<IntersectionObserver | null>(null);
  const sentinelRef = React.useCallback(
    (node: HTMLDivElement | null) => {
      if (loading || loadingMore) return;
      if (observerRef.current) observerRef.current.disconnect();

      const hasMore = members.length < total;
      if (!hasMore) return;

      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          setPage((prev) => prev + 1);
        }
      });

      if (node) observerRef.current.observe(node);
    },
    [loading, loadingMore, members.length, total]
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-1 sm:p-4 pb-20">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Members Directory</h1>
          <p className="text-sm text-slate-500">Manage all customer/member records in your organization</p>
        </div>
        <Link
          to="/organizer/members/new"
          className="inline-flex items-center justify-center space-x-2 bg-primary hover:bg-primary-dark text-white px-5 py-2.5 rounded-xl font-medium text-sm transition-colors shadow-sm self-start sm:self-auto"
        >
          <Plus size={18} />
          <span>Add Member</span>
        </Link>
      </div>

      {/* Filters and Search */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-sm border border-slate-100 dark:border-gray-700 flex flex-col md:flex-row md:items-center gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={18} />
          </span>
          <input
            type="text"
            placeholder="Search by name, mobile number or member code..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-gray-700 dark:bg-gray-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        {/* Status Filters */}
        <div className="flex space-x-2 overflow-x-auto">
          {(['all', 'active', 'inactive'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={clsx(
                "px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-colors",
                statusFilter === status
                  ? "bg-primary text-white"
                  : "bg-slate-100 text-slate-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-slate-200"
              )}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="flex justify-center py-12 text-slate-500">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent"></div>
            <span>Loading members...</span>
          </div>
        </div>
      ) : members.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 text-center py-16 rounded-2xl border border-slate-100 dark:border-gray-700">
          <User className="mx-auto text-slate-300 dark:text-gray-600 mb-4" size={48} />
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">No Members Found</h3>
          <p className="text-slate-500 text-sm mt-1 max-w-sm mx-auto">
            {search || statusFilter !== 'all'
              ? 'Try adjusting your search terms or status filters'
              : 'Get started by onboarding your first member using the "Add Member" button above.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          
          {/* Desktop Table View */}
          <div className="hidden md:block bg-white dark:bg-gray-800 rounded-2xl border border-slate-100 dark:border-gray-700 overflow-hidden shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-gray-850 text-slate-500 dark:text-gray-400 font-semibold text-xs uppercase tracking-wider border-b border-slate-100 dark:border-gray-700">
                  <th className="px-6 py-4">Code</th>
                  <th className="px-6 py-4">Full Name</th>
                  <th className="px-6 py-4">Mobile</th>
                  <th className="px-6 py-4">Village</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-gray-700 text-sm text-slate-700 dark:text-gray-300">
                {members.map((m) => (
                  <tr
                    key={m.id}
                    onClick={() => navigate(`/organizer/members/${m.id}`)}
                    className="hover:bg-slate-50 dark:hover:bg-gray-705 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 font-mono text-xs font-bold text-slate-500">{m.member_code}</td>
                    <td className="px-6 py-4 font-bold text-slate-800 dark:text-white">{m.full_name}</td>
                    <td className="px-6 py-4">{m.mobile}</td>
                    <td className="px-6 py-4">{m.village || '-'}</td>
                    <td className="px-6 py-4">
                      <span className={clsx(
                        "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold",
                        m.is_active
                          ? "bg-green-50 text-green-700 dark:bg-green-950/20 dark:text-green-400"
                          : "bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400"
                      )}>
                        {m.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-primary hover:text-primary-dark font-medium text-xs">View Profile</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card List View */}
          <div className="block md:hidden space-y-3">
            {members.map((m) => (
              <div
                key={m.id}
                onClick={() => navigate(`/organizer/members/${m.id}`)}
                className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-slate-100 dark:border-gray-700 active:bg-slate-50 dark:active:bg-gray-750 transition-colors shadow-sm space-y-3"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-slate-800 dark:text-white text-base">{m.full_name}</h3>
                    <span className="font-mono text-xs font-bold text-slate-400">{m.member_code}</span>
                  </div>
                  <span className={clsx(
                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold",
                    m.is_active
                      ? "bg-green-50 text-green-700 dark:bg-green-950/20 dark:text-green-400"
                      : "bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400"
                  )}>
                    {m.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="flex flex-col gap-1 text-xs text-slate-500">
                  <div className="flex items-center space-x-1.5">
                    <Phone size={14} className="text-slate-400" />
                    <span>{m.mobile}</span>
                  </div>
                  {m.village && (
                    <div className="flex items-center space-x-1.5">
                      <MapPin size={14} className="text-slate-400" />
                      <span>{m.village}</span>
                    </div>
                  )}
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
                <span>Loading more members...</span>
              </div>
            ) : members.length < total ? (
              <span className="text-xs text-slate-400">Scroll down to load more</span>
            ) : (
              <span className="text-xs text-slate-400">
                Showing all {total} members
              </span>
            )}
          </div>

        </div>
      )}
    </div>
  );
};
