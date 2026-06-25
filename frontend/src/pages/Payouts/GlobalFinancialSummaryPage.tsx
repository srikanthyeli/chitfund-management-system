import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PieChart, ArrowRight, Wallet, Users, LayoutDashboard } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';

export const GlobalFinancialSummaryPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [chitGroups, setChitGroups] = useState<any[]>([]);

  useEffect(() => {
    fetchChitGroups();
  }, []);

  const fetchChitGroups = async () => {
    try {
      setLoading(true);
      // Reusing the general get chit groups endpoint
      const response = await api.get('/chit-groups?limit=100');
      setChitGroups(response.data.items || response.data);
    } catch (error: any) {
      toast.error('Failed to load chit groups');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4 flex justify-center items-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  return (
    <div className="p-4 max-w-5xl mx-auto pb-24">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <PieChart size={24} className="text-purple-600" /> Financial Summary
        </h1>
        <p className="text-gray-500 mt-1">Select a chit group to view its detailed financial ledger and closures.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {chitGroups.length === 0 ? (
          <div className="col-span-full p-8 text-center text-gray-500 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <LayoutDashboard size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="font-medium text-lg text-gray-600">No Chit Groups Found</p>
            <p className="text-sm">Create a chit group first to view its financial summary.</p>
          </div>
        ) : (
          chitGroups.map((group) => (
            <div 
              key={group.id}
              onClick={() => navigate(`/organizer/chit-groups/${group.id}/financial-summary`)}
              className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5 cursor-pointer hover:shadow-md hover:border-purple-300 dark:hover:border-purple-700 transition-all group"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white group-hover:text-purple-600 transition-colors">
                    {group.chit_name}
                  </h3>
                  <p className="text-xs text-gray-500 font-medium px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-full inline-block mt-1 uppercase">
                    {group.status}
                  </p>
                </div>
                <div className="p-2 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg group-hover:bg-purple-100 transition-colors">
                  <ArrowRight size={18} />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
                <div>
                  <p className="text-xs text-gray-500 flex items-center gap-1 mb-1"><Wallet size={12} /> Total Value</p>
                  <p className="font-bold">₹{new Intl.NumberFormat('en-IN').format(group.chit_value)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 flex items-center gap-1 mb-1"><Users size={12} /> Members</p>
                  <p className="font-bold">{group.total_members} / {group.total_months}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
