import React, { useState, useEffect } from 'react';
import { FinancialSummaryCards } from '../components/FinancialSummaryCards';
import { CollectionVsPayoutChart } from '../components/CollectionVsPayoutChart';
import api from '../../../core/api';

export const FinancialSummaryPage = () => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get('/organizer/financial-summary/overview');
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Financial Summary</h1>
          <p className="text-slate-500 text-sm mt-1">Operational cash flow and financial health</p>
        </div>
        <div className="flex space-x-3">
          <select className="bg-white border border-slate-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:outline-none">
            <option>Current Month</option>
            <option>Last 3 Months</option>
            <option>Last 6 Months</option>
            <option>This Year</option>
          </select>
        </div>
      </div>

      <FinancialSummaryCards data={data?.overview} isLoading={isLoading} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-2">
          <CollectionVsPayoutChart data={data?.collection_vs_payout || []} />
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">Upcoming Actions</h3>
            {/* Empty state for MVP */}
            <div className="text-center py-10 text-slate-500">
                <p>No upcoming actions pending.</p>
            </div>
        </div>
      </div>
    </div>
  );
};
