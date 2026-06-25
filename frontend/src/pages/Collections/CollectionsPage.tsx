import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { IndianRupee, Clock, CheckCircle2, TrendingUp, Users } from 'lucide-react';
import { chitCollectionApi } from '../../core/chitCollectionApi';
import toast from 'react-hot-toast';

export const CollectionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [collections, setCollections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      const data = await chitCollectionApi.getActiveCollections();
      setCollections(data);
    } catch (error) {
      toast.error('Failed to load active collections');
    } finally {
      setLoading(false);
    }
  };

  const fmt = (v: any) => {
    if (v == null) return '₹0';
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(v));
  };

  if (loading) {
    return (
      <div className="p-4 space-y-4 max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Active Collections</h1>
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-40 rounded-2xl bg-gray-200 dark:bg-gray-800 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-4 max-w-4xl mx-auto pb-24">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Active Collections</h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Manage dues across all your finalized chit auctions.</p>

      {collections.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm text-center">
          <CheckCircle2 size={48} className="text-emerald-500 mb-4 opacity-80" />
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">All Caught Up!</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">There are no active collections right now. Finalize a new auction to start collecting dues.</p>
          <button 
            onClick={() => navigate('/organizer/chit-groups')}
            className="mt-6 px-6 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold transition-all active:scale-95"
          >
            Go to Chit Groups
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {collections.map((c) => {
            const isComplete = c.total_remaining <= 0 && c.total_expected > 0;
            const progress = c.total_expected > 0 ? (c.total_collected / c.total_expected) * 100 : 0;
            
            return (
              <div 
                key={c.auction_id} 
                className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col transition-all hover:shadow-md"
              >
                {/* Header */}
                <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white truncate">{c.chit_name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="px-2 py-0.5 rounded-md bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-bold">
                        Month {c.month_number}
                      </span>
                      <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                        <Users size={12} /> {c.total_memberships} Members
                      </span>
                    </div>
                  </div>
                  {isComplete && (
                    <span className="flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
                      <CheckCircle2 size={14} /> Complete
                    </span>
                  )}
                </div>

                {/* Stats */}
                <div className="p-4 grid grid-cols-2 gap-4 flex-1">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1 flex items-center gap-1">
                      <TrendingUp size={12} /> Collected
                    </p>
                    <p className="font-bold text-emerald-600 dark:text-emerald-400 text-lg">{fmt(c.total_collected)}</p>
                    <p className="text-[10px] text-gray-400 mt-0.5">of {fmt(c.total_expected)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1 flex items-center gap-1">
                      <Clock size={12} /> Remaining
                    </p>
                    <p className={`font-bold text-lg ${isComplete ? 'text-gray-400' : 'text-red-500 dark:text-red-400'}`}>
                      {fmt(c.total_remaining)}
                    </p>
                    <p className="text-[10px] text-gray-400 mt-0.5">
                      {c.pending_count + c.partial_count} pending
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="px-4 pb-2">
                  <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-1.5 mb-1 overflow-hidden">
                    <div 
                      className={`h-1.5 rounded-full ${isComplete ? 'bg-emerald-500' : 'bg-purple-500'}`} 
                      style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                    ></div>
                  </div>
                </div>

                {/* Footer Action */}
                <div className="p-3 bg-gray-50 dark:bg-gray-900/50 mt-auto">
                  <button
                    onClick={() => navigate(`/organizer/chit-groups/${c.chit_group_id}/auctions/${c.auction_id}/collections`)}
                    className="w-full flex items-center justify-center gap-2 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl font-bold text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm active:scale-[0.98]"
                  >
                    <IndianRupee size={16} className={isComplete ? "text-emerald-500" : "text-purple-600 dark:text-purple-400"} /> 
                    Manage Collection
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
