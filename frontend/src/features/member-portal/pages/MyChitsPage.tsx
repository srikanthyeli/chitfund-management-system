import React, { useEffect, useState } from 'react';
import { memberPortalApi } from '../api/memberPortalApi';
import type { ChitSummaryResponse } from '../api/memberPortalApi';
import { Briefcase, Calendar, Info } from 'lucide-react';
import { Link } from 'react-router-dom';

export const MyChitsPage: React.FC = () => {
  const [chits, setChits] = useState<ChitSummaryResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchChits = async () => {
      try {
        const response = await memberPortalApi.listChits();
        setChits(response);
      } catch (error) {
        console.error('Failed to fetch chits', error);
      } finally {
        setLoading(false);
      }
    };
    fetchChits();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading chits...</div>;
  }

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <Briefcase className="w-6 h-6 mr-2 text-purple-600" /> My Chits
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">View all your active and past chit groups.</p>
        </div>
      </div>

      {chits.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-200 dark:border-gray-700 shadow-sm">
          <Info className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">No chits found</h3>
          <p className="text-gray-500 mt-2">You are not part of any chit groups yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {chits.map((chit) => (
            <div key={chit.chit_group_id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow overflow-hidden flex flex-col">
              <div className="p-5 flex-1">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400 mb-2">
                      {chit.chit_code}
                    </span>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white line-clamp-1" title={chit.chit_group_name}>
                      {chit.chit_group_name}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Organizer: {chit.organizer_name}</p>
                  </div>
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${chit.status === 'ACTIVE' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'}`}>
                    {chit.status}
                  </span>
                </div>
                
                <div className="space-y-3 mt-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Total Value</span>
                    <span className="font-semibold text-gray-900 dark:text-white">₹{chit.duration_months * chit.monthly_installment_per_share}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Monthly Installment</span>
                    <span className="font-semibold text-gray-900 dark:text-white">₹{chit.monthly_installment_per_share}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Shares Held</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{chit.shares_held} Share(s)</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Current Month</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{chit.current_month} / {chit.duration_months}</span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800/50 p-4 border-t border-gray-100 dark:border-gray-700">
                <div className="flex justify-between items-center">
                  <div className="flex items-center text-xs text-gray-500">
                    <Calendar className="w-3 h-3 mr-1" />
                    Started: {new Date(chit.start_date).toLocaleDateString()}
                  </div>
                  <Link 
                    to={`/member/chits/${chit.chit_group_id}`}
                    className="text-sm font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
                  >
                    View Details →
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
