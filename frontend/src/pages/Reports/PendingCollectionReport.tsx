import React, { useState, useEffect } from 'react';
import { reportApi } from '../../core/reportApi';
import type { ReportParams } from '../../core/reportApi';
import { ExportActions } from '../../components/common/ExportActions';

export const PendingCollectionReport = () => {
  const [data, setData] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  
  const [params, setParams] = useState<ReportParams>({
    page: 1,
    limit: 20
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await reportApi.getPendingCollectionsReport(params);
      setData(response.data);
      setTotal(response.pagination.total_records);
    } catch (error) {
      console.error('Failed to load report', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [params.page, params.limit]);

  const handleExportBackend = async () => {
    try {
      const response = await reportApi.getPendingCollectionsReport({ ...params, export: true });
      const fullData = response.data;
      if (fullData.length === 0) return;
      const keys = Object.keys(fullData[0]);
      const csv = [
        keys.join(','),
        ...fullData.map((obj: any) => keys.map(k => `"${String(obj[k] || '').replace(/"/g, '""')}"`).join(','))
      ].join('\n');
      
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pending_collections_full.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pending Collections</h1>
          <p className="text-sm text-gray-500">View members with pending or overdue installments.</p>
        </div>
        <ExportActions data={data} filename="pending_collections" onExportBackend={handleExportBackend} />
      </div>

      <div className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden mt-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Member</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mobile</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Group</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Month</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pending Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Overdue Days</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-4 text-center text-gray-500">Loading...</td></tr>
              ) : data.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-4 text-center text-gray-500">No pending collections found</td></tr>
              ) : (
                data.map(row => (
                  <tr key={row.due_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{row.member_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.mobile}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.chit_group_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">M {row.month_number}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600 font-semibold">₹{row.pending_amount}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-semibold">{row.overdue_days > 0 ? `${row.overdue_days} Days` : 'Not Overdue'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Controls */}
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div className="text-sm text-gray-700">
            Showing <span className="font-medium">{Math.min((params.page! - 1) * params.limit! + 1, total)}</span> to <span className="font-medium">{Math.min(params.page! * params.limit!, total)}</span> of <span className="font-medium">{total}</span> results
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setParams(p => ({ ...p, page: p.page! - 1 }))}
              disabled={params.page === 1}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setParams(p => ({ ...p, page: p.page! + 1 }))}
              disabled={params.page! * params.limit! >= total}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
