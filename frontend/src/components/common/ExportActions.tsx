import React from 'react';
import { Download, Printer } from 'lucide-react';

interface ExportActionsProps {
  data: any[];
  filename: string;
  onExportBackend?: () => void; // Used if we trigger a backend export instead of client side
}

export const ExportActions: React.FC<ExportActionsProps> = ({ data, filename, onExportBackend }) => {

  const convertToCSV = (arr: any[]) => {
    if (arr.length === 0) return '';
    const keys = Object.keys(arr[0]);
    const headerRow = keys.join(',');
    const rows = arr.map(obj => {
      return keys.map(key => {
        let val = obj[key];
        if (val === null || val === undefined) val = '';
        const strVal = String(val).replace(/"/g, '""');
        return `"${strVal}"`;
      }).join(',');
    });
    return [headerRow, ...rows].join('\n');
  };

  const handleExportCSV = () => {
    if (onExportBackend) {
      onExportBackend();
      return;
    }
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('url');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="flex items-center gap-2 no-print">
      <button
        onClick={handleExportCSV}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        <Download className="w-4 h-4" />
        Export CSV
      </button>
      <button
        onClick={handlePrint}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        <Printer className="w-4 h-4" />
        Print / PDF
      </button>
    </div>
  );
};
