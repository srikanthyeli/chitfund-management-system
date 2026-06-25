import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { payoutApi } from '../../core/payoutApi';
import toast from 'react-hot-toast';
import { Plus, IndianRupee, Search, ChevronRight } from 'lucide-react';

export const WinnerPayoutListPage: React.FC = () => {
  const navigate = useNavigate();
  const [payouts, setPayouts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPayouts();
  }, []);

  const loadPayouts = async () => {
    try {
      setLoading(true);
      const res = await payoutApi.listPayouts();
      setPayouts(res.items || []);
    } catch (err: any) {
      toast.error('Failed to load payouts');
    } finally {
      setLoading(false);
    }
  };

  const fmt = (v: any) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(v || 0));

  return (
    <div className="p-4 max-w-4xl mx-auto pb-24">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Winner Payouts</h1>
          <p className="text-gray-500 text-sm">Manage auction winner payouts and receipts</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-10"><div className="animate-spin h-8 w-8 border-b-2 border-purple-600 rounded-full"></div></div>
      ) : payouts.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 text-center border border-gray-200 dark:border-gray-700">
          <p className="text-gray-500 mb-4">No winner payouts found.</p>
          <p className="text-sm text-gray-400">Go to a finalized auction to create a payout.</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          {payouts.map((payout, i) => (
            <div 
              key={payout.id} 
              onClick={() => navigate(`/organizer/winner-payouts/${payout.id}`)}
              className={`p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${i > 0 ? 'border-t border-gray-100 dark:border-gray-700' : ''}`}
            >
              <div>
                <p className="font-bold text-gray-900 dark:text-white mb-1">{payout.winner_name}</p>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded font-medium">Month {payout.month_number}</span>
                  <span>{payout.chit_name}</span>
                </div>
              </div>
              <div className="text-right flex items-center gap-4">
                <div>
                  <p className="font-bold text-emerald-600">{fmt(payout.payout_amount)}</p>
                  <p className="text-xs text-gray-500 mt-1">{payout.status.replace('_', ' ')}</p>
                </div>
                <ChevronRight size={18} className="text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
