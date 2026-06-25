import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ChartProps {
  data: any[];
}

export const CollectionVsPayoutChart: React.FC<ChartProps> = ({ data }) => {
  // Use recharts as agreed
  const mockData = data && data.length > 0 ? data : [
    { month_label: 'Jan', collection_amount: 120000, winner_payout_amount: 100000 },
    { month_label: 'Feb', collection_amount: 150000, winner_payout_amount: 100000 },
    { month_label: 'Mar', collection_amount: 180000, winner_payout_amount: 120000 },
    { month_label: 'Apr', collection_amount: 140000, winner_payout_amount: 100000 },
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <h3 className="text-lg font-semibold text-slate-800 mb-6">Collection vs Payout Trend</h3>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={mockData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
            <XAxis dataKey="month_label" axisLine={false} tickLine={false} tick={{ fill: '#64748B' }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748B' }} />
            <Tooltip 
              cursor={{ fill: '#F1F5F9' }}
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="collection_amount" name="Collection" fill="#10B981" radius={[4, 4, 0, 0]} />
            <Bar dataKey="winner_payout_amount" name="Winner Payout" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
