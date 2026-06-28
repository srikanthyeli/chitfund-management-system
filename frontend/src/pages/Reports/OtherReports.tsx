import React, { useState, useEffect } from 'react';
import { reportApi } from '../../core/reportApi';
import type { ReportParams } from '../../core/reportApi';
import { ExportActions } from '../../components/common/ExportActions';
import { useTranslation } from 'react-i18next';

// Generic Report Page Component to avoid code duplication
export const GenericReportPage = ({ title, description, apiCall, columns, exportFilename }: any) => {
  const { t } = useTranslation(['common', 'reports']);

  const [data, setData] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [params, setParams] = useState<ReportParams>({ page: 1, limit: 20 });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await apiCall(params);
        setData(response.data);
        setTotal(response.pagination.total_records);
      } catch (error) {
        console.error('Failed to load report', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [params.page, params.limit, apiCall]);

  const handleExportBackend = async () => {
    try {
      const response = await apiCall({ ...params, export: true });
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
      a.download = `${exportFilename}_full.csv`;
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
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
        <ExportActions data={data} filename={exportFilename} onExportBackend={handleExportBackend} />
      </div>

      <div className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden mt-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((col: any) => (
                  <th key={col.key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{col.label}</th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr><td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">{t('common:loading')}</td></tr>
              ) : data.length === 0 ? (
                <tr><td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">No data found</td></tr>
              ) : (
                data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {columns.map((col: any) => (
                      <td key={col.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{String(row[col.key] || '')}</td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div className="text-sm text-gray-700">
            Showing <span className="font-medium">{Math.min((params.page! - 1) * params.limit! + 1, total)}</span> to <span className="font-medium">{Math.min(params.page! * params.limit!, total)}</span> of <span className="font-medium">{total}</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setParams(p => ({ ...p, page: p.page! - 1 }))}
              disabled={params.page === 1}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >{t('common:previous')}</button>
            <button
              onClick={() => setParams(p => ({ ...p, page: p.page! + 1 }))}
              disabled={params.page! * params.limit! >= total}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >{t('common:next')}</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const AuctionReport = () => (
  <GenericReportPage 
    title={t('reports:reports_auction')} 
    description="Details of all conducted auctions."
    apiCall={reportApi.getAuctionReport}
    exportFilename="auction_report"
    columns={[
      { key: 'chit_group_name', label: 'Chit Group' },
      { key: 'auction_month', label: 'Month' },
      { key: 'winner_name', label: 'Winner' },
      { key: 'gross_amount', label: 'Gross Amount' },
      { key: 'discount_amount', label: 'Discount' },
      { key: 'status', label: 'Status' }
    ]}
  />
);

export const WinnerPayoutReport = () => (
  <GenericReportPage 
    title={t('reports:reports_winner_payout')} 
    description="Details of all winner payouts."
    apiCall={reportApi.getWinnerPayoutReport}
    exportFilename="winner_payout_report"
    columns={[
      { key: 'chit_group_name', label: 'Chit Group' },
      { key: 'winner_name', label: 'Winner' },
      { key: 'net_amount', label: 'Net Amount' },
      { key: 'payment_status', label: 'Status' },
      { key: 'payment_mode', label: 'Mode' },
      { key: 'payout_date', label: 'Date' }
    ]}
  />
);

export const MemberFinancialReport = () => (
  <GenericReportPage 
    title={t('reports:reports_member_financial')} 
    description="Financial summary for all members."
    apiCall={reportApi.getMemberFinancialReport}
    exportFilename="member_financial_report"
    columns={[
      { key: 'member_name', label: 'Member' },
      { key: 'mobile', label: 'Mobile' },
      { key: 'total_paid', label: 'Total Paid' },
      { key: 'pending_amount', label: 'Pending' },
      { key: 'total_dividend_earned', label: 'Dividends Earned' },
      { key: 'current_balance', label: 'Balance' }
    ]}
  />
);

export const OrganizerFinancialReport = () => (
  <GenericReportPage 
    title="Organizer Financial Report" 
    description="Monthly revenue, commissions, and cash flow."
    apiCall={reportApi.getOrganizerFinancialReport}
    exportFilename="organizer_financial_report"
    columns={[
      { key: 'month', label: 'Month' },
      { key: 'collections_received', label: 'Collections' },
      { key: 'commission_income', label: 'Commission' },
      { key: 'maintenance_income', label: 'Maintenance' },
      { key: 'net_cash_flow', label: 'Net Cash Flow' }
    ]}
  />
);

export const ChitPerformanceReport = () => (
  <GenericReportPage 
    title={t('reports:reports_chit_performance')} 
    description="Health and performance of all chit groups."
    apiCall={reportApi.getChitPerformanceReport}
    exportFilename="chit_performance_report"
    columns={[
      { key: 'chit_group_name', label: 'Chit Group' },
      { key: 'status', label: 'Status' },
      { key: 'completion_percentage', label: 'Completion %' },
      { key: 'total_collections', label: 'Total Collected' },
      { key: 'total_pending', label: 'Total Pending' },
      { key: 'risk_score', label: 'Risk Score' }
    ]}
  />
);
