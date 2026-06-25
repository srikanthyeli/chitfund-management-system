import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import api from '../../core/api';
import toast from 'react-hot-toast';

interface StatusDialogProps {
  isOpen: boolean;
  onClose: () => void;
  memberId: string;
  currentStatus: boolean;
  memberName: string;
  onSuccess: (updatedMember: any) => void;
}

export const StatusDialog: React.FC<StatusDialogProps> = ({
  isOpen,
  onClose,
  memberId,
  currentStatus,
  memberName,
  onSuccess,
}) => {
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.patch(`/members/${memberId}/status`, {
        is_active: !currentStatus,
        remarks: remarks.trim() || undefined,
      });
      
      const newStatusStr = !currentStatus ? 'activated' : 'deactivated';
      toast.success(`Member ${newStatusStr} successfully`);
      onSuccess(response.data);
      onClose();
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to update member status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-md overflow-hidden shadow-xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700 bg-slate-50 dark:bg-gray-850">
          <h3 className="font-bold text-gray-900 dark:text-white">
            {currentStatus ? 'Deactivate Member' : 'Activate Member'}
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full">
            <X size={20} className="text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div className="flex items-start space-x-3 p-3 bg-amber-50 dark:bg-amber-950/20 text-amber-800 dark:text-amber-300 rounded-xl border border-amber-100 dark:border-amber-900/30 text-sm">
            <AlertTriangle className="mt-0.5 shrink-0" size={18} />
            <div>
              <p className="font-semibold">Confirm Status Change</p>
              <p className="mt-0.5 opacity-90">
                Are you sure you want to {currentStatus ? 'deactivate' : 'activate'}{' '}
                <span className="font-bold">{memberName}</span>?
                {currentStatus && ' Deactivated members will not be able to participate in new chit groups or transactions.'}
              </p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">
              Reason / Remarks (Optional)
            </label>
            <textarea
              placeholder="e.g. Left village, unpaid dues, etc."
              rows={3}
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary resize-none"
            />
          </div>

          <div className="flex space-x-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`flex-1 py-2.5 rounded-xl text-white font-medium text-sm transition-colors disabled:opacity-50 ${
                currentStatus 
                  ? 'bg-rose-600 hover:bg-rose-700' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {loading ? 'Processing...' : currentStatus ? 'Deactivate' : 'Activate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
