import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, FileText, CheckCircle2, AlertCircle, 
  Wallet, TrendingUp, IndianRupee, PieChart, Lock
} from 'lucide-react';
import { payoutApi } from '../../core/payoutApi';
import toast from 'react-hot-toast';

export const ChitFinancialSummaryPage: React.FC = () => {
  const { chitGroupId } = useParams<{ chitGroupId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchData();
  }, [chitGroupId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await payoutApi.getFinancialSummary(chitGroupId!);
      setData(res);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to load financial summary');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseMonth = async (monthNumber: number) => {
    try {
      await payoutApi.closeMonth(chitGroupId!, monthNumber, { remarks: 'Closed from summary dashboard' });
      toast.success(`Month ${monthNumber} financially closed!`);
      fetchData(); // Refresh
    } catch (error: any) {
      toast.error(error.response?.data?.message || `Failed to close month ${monthNumber}`);
    }
  };

  const fmt = (v: any) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(v || 0));

  if (loading) {
    return <div className="p-4 flex justify-center items-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  if (!data) return null;

  return (
    <div className="p-4 max-w-5xl mx-auto pb-24">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 font-medium">
        <ArrowLeft size={20} /> Back
      </button>

      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Financial Summary</h1>
          <p className="text-gray-500">Group Level Ledger & Monthly Closures</p>
        </div>
      </div>

      {/* High Level Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="bg-blue-50 text-blue-600 p-3 rounded-full mb-3"><Wallet size={24} /></div>
          <p className="text-sm text-gray-500">Total Expected</p>
          <p className="text-xl font-bold mt-1">{fmt(data.total_expected_collection)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="bg-emerald-50 text-emerald-600 p-3 rounded-full mb-3"><TrendingUp size={24} /></div>
          <p className="text-sm text-gray-500">Total Collected</p>
          <p className="text-xl font-bold mt-1 text-emerald-600">{fmt(data.total_actual_collection)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="bg-purple-50 text-purple-600 p-3 rounded-full mb-3"><IndianRupee size={24} /></div>
          <p className="text-sm text-gray-500">Winner Payouts</p>
          <p className="text-xl font-bold mt-1 text-purple-600">{fmt(data.total_winner_payouts)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col items-center justify-center text-center">
          <div className="bg-amber-50 text-amber-600 p-3 rounded-full mb-3"><AlertCircle size={24} /></div>
          <p className="text-sm text-gray-500">Org. Contribution</p>
          <p className="text-xl font-bold mt-1 text-amber-600">{fmt(data.total_organizer_contribution)}</p>
        </div>
      </div>

      {/* Monthly Timeline */}
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <FileText size={20} /> Monthly Financial Closures
      </h2>
      
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {data.monthly_summaries.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No finalized months available for closure yet.</div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {data.monthly_summaries.map((m: any) => (
              <div key={m.id} className="p-5 flex flex-col md:flex-row gap-4 items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">
                
                <div className="flex items-center gap-4 w-full md:w-auto">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg
                    ${m.closure_status === 'CLOSED' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-700'}`}>
                    M{m.month_number}
                  </div>
                  <div>
                    <h3 className="font-bold flex items-center gap-2">
                      Month {m.month_number}
                      {m.closure_status === 'CLOSED' && <CheckCircle2 size={16} className="text-emerald-500" />}
                    </h3>
                    <p className="text-sm text-gray-500 flex gap-4 mt-1">
                      <span>Collected: <span className="font-medium text-emerald-600">{fmt(m.actual_collection_amount)}</span></span>
                      <span>Payout: <span className="font-medium text-purple-600">{fmt(m.winner_payout_amount)}</span></span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto justify-end">
                  {m.closure_status === 'READY_FOR_CLOSURE' && (
                    <button 
                      onClick={() => handleCloseMonth(m.month_number)}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg flex items-center gap-2 transition-colors"
                    >
                      <Lock size={16} /> Close Month
                    </button>
                  )}
                  
                  {m.closure_status === 'OPEN' && m.winner_payout_amount == 0 && (
                    <button 
                      onClick={() => navigate(`/organizer/chit-groups/${chitGroupId}/auctions/${m.auction_id}`)}
                      className="px-4 py-2 bg-purple-100 text-purple-700 hover:bg-purple-200 text-sm font-bold rounded-lg flex items-center gap-2 transition-colors"
                    >
                      <IndianRupee size={16} /> Pay Winner
                    </button>
                  )}

                  {m.closure_status === 'CLOSED' && (
                    <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-bold uppercase tracking-wider">
                      Locked
                    </span>
                  )}
                </div>

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};
