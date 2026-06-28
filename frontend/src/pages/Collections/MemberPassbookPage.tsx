import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen } from 'lucide-react';
import { chitCollectionApi } from '../../core/chitCollectionApi';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';

export const MemberPassbookPage: React.FC = () => {
  const { t } = useTranslation(['collections']);

  const { memberId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (memberId) {
      fetchPassbook();
    }
  }, [memberId]);

  const fetchPassbook = async () => {
    try {
      const response = await chitCollectionApi.getMemberPassbook(memberId as string);
      setData(response);
    } catch (error) {
      toast.error('Failed to load passbook');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4 text-center mt-10">Loading Passbook...</div>;
  if (!data) return <div className="p-4 text-center text-red-500 mt-10">Data not found.</div>;

  return (
    <div className="pb-24 max-w-lg mx-auto bg-gray-50 min-h-screen">
      <div className="bg-purple-900 text-white p-4 sticky top-0 z-30 shadow-md">
        <div className="flex items-center">
          <button onClick={() => navigate(-1)} className="mr-3">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <BookOpen className="w-5 h-5 mr-2" />
          <h1 className="text-xl font-bold">Digital Passbook</h1>
        </div>
      </div>

      <div className="p-4 bg-white shadow-sm mb-4">
        <p className="text-gray-500 text-sm font-semibold uppercase tracking-wide">{t('collections:collections_member')}</p>
        <p className="text-xl font-bold text-gray-900">{data.member_name}</p>
      </div>

      <div className="px-4 space-y-4">
        {data.entries.length === 0 ? (
          <p className="text-center text-gray-500 py-10">No records found.</p>
        ) : (
          data.entries.map((entry: any, index: number) => (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="bg-purple-50 p-3 border-b border-purple-100 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-purple-900">{entry.chit_name}</h3>
                  <p className="text-xs text-purple-600 font-semibold">Month {entry.month_number} ({entry.share_count} Shares)</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-bold ${
                  entry.payment_status === 'PAID' ? 'bg-green-100 text-green-700' :
                  entry.payment_status === 'PARTIALLY_PAID' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-200 text-gray-700'
                }`}>
                  {entry.payment_status.replace('_', ' ')}
                </span>
              </div>
              
              <div className="p-3">
                <div className="grid grid-cols-2 gap-y-2 text-sm mb-3">
                  <div className="text-gray-600">Net Payable</div>
                  <div className="text-right font-semibold text-gray-900">₹{entry.net_payable}</div>
                  
                  <div className="text-gray-600">Total Paid</div>
                  <div className="text-right font-semibold text-green-600">₹{entry.total_paid}</div>
                  
                  <div className="text-gray-600 font-bold">Remaining</div>
                  <div className="text-right font-bold text-red-600">₹{entry.remaining}</div>
                </div>

                {entry.receipt_numbers && entry.receipt_numbers.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-dashed border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Receipts:</p>
                    <div className="flex flex-wrap gap-1">
                      {entry.receipt_numbers.map((receipt: string) => (
                        <span key={receipt} className="text-[10px] bg-gray-100 px-2 py-1 rounded text-gray-600 font-mono">
                          {receipt}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
